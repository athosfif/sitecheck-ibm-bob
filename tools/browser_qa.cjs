const {chromium}=require('playwright');
const fs=require('fs');
const BASE=process.env.SITECHECK_WEB_BASE||'http://127.0.0.1:18768/contribuicoes/sitecheck/';
(async()=>{const b=await chromium.launch({channel:'chrome',headless:true});const p=await b.newPage();const errors=[];p.on('pageerror',e=>errors.push(e.message));await p.goto(BASE+'en/');
const results=await p.evaluate(()=>{const E=SiteCheckDemo,r=[];function test(n,fn){if(!fn())throw Error(n);r.push(n);}
test('sample 3 findings',()=>E.inspect(E.sample).length===3);
test('query and protocol-relative links',()=>E.inspect('<a href="about.html?q=1">a</a><a href="//example.org">x</a>').length===0);
test('implicit form label',()=>E.inspect('<label>Name<input></label>').length===0);
test('aria text reference',()=>E.inspect('<span id="n">Name</span><input aria-labelledby="n">').length===0);
test('empty or dangling names',()=>E.inspect('<input aria-label=""><textarea aria-labelledby="none"></textarea>').length===2);
test('same rule partial fix',()=>{let c=E.compare(E.inspect('<img src="a"><img src="b">'),E.inspect('<img src="a" alt=""><img src="b">'));return c.filter(f=>f.state==='fixed').length===1&&c.filter(f=>f.state==='open').length===1;});
test('duplicate instances',()=>E.compare(E.inspect('<img src="a"><img src="a">'),E.inspect('<img src="a">')).length===2);
test('line locations with single quotes',()=>E.inspect("\n\n<img src='a'>")[0].location==='L3');
test('no script/comment false source line',()=>E.inspect('<script>var s="<img src=\"a\">"</script>\n<!--<img src="a">-->\n<img src="a">')[0].location==='L3');
test('new same-rule issue',()=>E.compare(E.inspect('<img src="a">'),E.inspect('<img src="a"><img src="b">')).some(f=>f.state==='regressed'));
test('source size bounded',()=>{try{E.inspect('x'.repeat(2000001));return false}catch{return true}});
return r;});
await p.locator('#run-button').click();await p.locator('#fix-button').click();if(await p.locator('#fixed-count').textContent()!=='1')throw Error('sample fix');if(await p.locator('#open-count').textContent()!=='2')throw Error('sample remaining');results.push('UI sample 3 -> 2');
await p.locator('#html-input').fill('<label>Name<input></label>');if(!(await p.locator('#fix-button').isDisabled()))throw Error('custom fix gate');await p.locator('#run-button').click();results.push('custom fix limited');
const external=[];p.on('request',r=>{if(/example\.invalid/.test(r.url()))external.push(r.url())});await p.evaluate(()=>SiteCheckDemo.inspect('<img src="https://example.invalid/a"><iframe src="https://example.invalid/b"></iframe><script>window.hacked=true</script>'));await p.waitForTimeout(200);if(external.length||await p.evaluate(()=>!!window.hacked))throw Error('input executed/fetched');results.push('inert untrusted HTML');
await p.locator('#file-input').setInputFiles([{name:'index.html',mimeType:'text/html',buffer:Buffer.from('<a href="guide.pdf">PDF</a>')},{name:'guide.pdf',mimeType:'application/pdf',buffer:Buffer.from('unused fixture')}]);await p.locator('#run-button').click();if(await p.locator('#open-count').textContent()!=='0')throw Error('resource set');results.push('non-HTML destination');
for(const locale of ['en','pt-br','es','fr','de','it']){await p.goto(BASE+''+locale+'/');await p.locator('#run-button').click();await p.locator('#fix-button').click();if(await p.locator('#fixed-count').textContent()!=='1')throw Error(locale);}
results.push('six languages');
for(const width of [390,768,1440]){await p.setViewportSize({width,height:900});if(await p.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1))throw Error('overflow '+width);await p.screenshot({path:'/tmp/sitecheck-qa-'+width+'.png',fullPage:true});}results.push('responsive 390/768/1440');
if(errors.length)throw Error(errors.join('\n'));fs.writeFileSync('/tmp/sitecheck-browser-qa.json',JSON.stringify({passed:results.length,results},null,2));console.log(results);await b.close();})();
