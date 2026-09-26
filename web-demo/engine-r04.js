/* Static inspection only. Untrusted markup stays in an inert template. */
(function(global){
 'use strict';
 const targets=new Set(['img','input','textarea','select','a']);
 const signature=n=>JSON.stringify([n.localName,...Array.from(n.attributes).map(a=>[a.name,a.value]).sort((a,b)=>a[0].localeCompare(b[0]))]);
 function tree(source){
  if(typeof source!=='string'||source.length>2_000_000)throw Error('source_limit');
  const template=document.createElement('template');template.innerHTML=source;
  const locations=new Map();
  // Skip comments and raw-text elements when locating original start tags.
  const tokens=/<!--[\s\S]*?(?:-->|$)|<![^>]*>|<\/?[a-zA-Z][^>"']*(?:(?:"[^"]*"|'[^']*')[^>"']*)*>/g;
  let match,raw='';
  while((match=tokens.exec(source))){
   const tag=match[0].match(/^<(\/?)([\w:-]+)/);if(!tag)continue;
   const name=tag[2].toLowerCase();
   if(raw){if(tag[1]&&name===raw)raw='';continue;}
   if(tag[1])continue;
   if(targets.has(name)){
    const t=document.createElement('template');t.innerHTML=match[0]+(name==='textarea'?'</textarea>':name==='select'?'</select>':name==='a'?'</a>':'');
    const n=t.content.firstElementChild;if(n){const key=signature(n);if(!locations.has(key))locations.set(key,[]);locations.get(key).push({line:source.slice(0,match.index).split('\n').length,markup:match[0],offset:match.index});}
   }
   if(['script','style','textarea','title'].includes(name))raw=name;
  }
  const position=new WeakMap();
  for(const n of template.content.querySelectorAll('img,input,textarea,select,a')){const q=locations.get(signature(n));if(q?.length)position.set(n,q.shift());}
  return {doc:template.content,position};
 }
 function visibleText(n){const copy=n.cloneNode(true);copy.querySelectorAll('script,style,[hidden],[aria-hidden="true"]').forEach(e=>e.remove());return copy.textContent.trim()||Array.from(copy.querySelectorAll('img[alt]')).map(i=>i.getAttribute('alt')).join(' ').trim();}
 function inspect(source,fileNames=['index.html'],checkedFile='index.html'){
  const {doc,position}=tree(source),out=[];
  const add=(id,n,identity,target)=>{const p=position.get(n);out.push({id,fingerprint:JSON.stringify([id,checkedFile,identity]),line:p?.line??null,markup:(p?.markup||n.outerHTML).slice(0,180),target});};
  doc.querySelectorAll('img:not([alt])').forEach(n=>add('SC-001',n,[n.id,n.getAttribute('src')]));
  const labelIds=new Set(Array.from(doc.querySelectorAll('label[for]')).filter(visibleText).map(l=>l.getAttribute('for')));
  const ids=new Map(Array.from(doc.querySelectorAll('[id]')).map(n=>[n.id,visibleText(n)]));
  doc.querySelectorAll('input,textarea,select').forEach(n=>{
   const type=(n.getAttribute('type')||'text').toLowerCase();if(['hidden','submit','reset','button'].includes(type)&&n.localName==='input')return;
   const wrapper=n.closest('label');
   const label=(n.id&&labelIds.has(n.id))||(wrapper&&visibleText(wrapper)&&(!wrapper.hasAttribute('for')||wrapper.getAttribute('for')===n.id));
   const aria=(n.getAttribute('aria-label')||'').trim()||(n.getAttribute('aria-labelledby')||'').split(/\s+/).some(id=>ids.get(id));
   const fallback=(n.getAttribute('title')||'').trim()||(type==='image'&&(n.getAttribute('alt')||'').trim());
   if(!label&&!aria&&!fallback)add('SC-002',n,[n.localName,n.id,n.getAttribute('name'),type]);
  });
  const files=new Set(fileNames);
  // A supplied base URL or root-relative server route cannot be resolved by a single-file static checker.
  if(!doc.querySelector('base[href]'))doc.querySelectorAll('a[href]').forEach(n=>{
   const href=n.getAttribute('href').trim();if(!href||/^(?:[#/]|[a-z][a-z0-9+.-]*:)/i.test(href))return;
   let path;try{path=decodeURIComponent(href.split(/[?#]/)[0]);}catch{return;}
   if(!path)return;
   const parts=checkedFile.split('/').slice(0,-1);for(const p of path.split('/')){if(p==='..')parts.pop();else if(p&&p!=='.')parts.push(p);}
   const target=parts.join('/');
   if(!files.has(target)&&!Array.from(files).some(f=>f.startsWith(target+'/')))add('SC-003',n,[href],target);
  });
  return out;
 }
 function compare(previous,current){
  if(!previous)return current.map(f=>({...f}));
  const remaining=new Map(),key=f=>f.fingerprint||JSON.stringify([f.id,f.file,(f.location||'').replace(/^(line|linha) \d+\s*[—:-]?\s*/, '')]);
  previous.forEach(f=>{const k=key(f);if(!remaining.has(k))remaining.set(k,[]);remaining.get(k).push(f);});
  const out=current.map(f=>{const q=remaining.get(key(f)),found=!!q?.length;if(found)q.shift();return {...f,state:found?'open':'regressed'};});
  remaining.forEach(q=>q.forEach(f=>out.push({...f,state:'fixed'})));return out;
 }
 global.SiteCheckEngine={inspect,compare};
})(window);
