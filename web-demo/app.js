(function () {
  "use strict";

  const locale = window.SITECHECK_LOCALE || "en";
  const DYNAMIC_COPY = {
    en: { sc1:"Image missing alternative text", sc2:"Form field missing an associated label", sc3:"Internal link points to a missing destination", noAlt:"has no alt attribute.", addAlt:"Add a useful alt description. If the image is purely decorative, use alt=\"\".", noLabel:"has no matching label or accessible name.", addLabel:"Add an associated label before the field.", addName:"Give the field an id and matching label, or add aria-label.", missingTarget:"which is not in the supplied file set.", fixTarget:"Upload or create the destination, or update the href to an existing file.", verified:"verified", fixed:"fixed", location:"Location", evidence:"Evidence", next:"Next step", recheck:"The recheck no longer detects the previous pattern.", checks:"checks", noUpload:"no upload", issues:"issues", issue:"issue", clear:"Clear", files:"local files", file:"local file", ready:"Ready", sample:"Sample file set: index.html, about.html", email:"Email address" },
    "pt-br": { sc1:"Imagem sem texto alternativo", sc2:"Campo de formulário sem rótulo associado", sc3:"Link interno aponta para destino inexistente", noAlt:"não possui atributo alt.", addAlt:"Adicione uma descrição alternativa útil. Se a imagem for decorativa, use alt=\"\".", noLabel:"não possui rótulo correspondente nem nome acessível.", addLabel:"Adicione um rótulo associado antes do campo.", addName:"Dê um id ao campo e associe um rótulo, ou adicione aria-label.", missingTarget:"não existe no conjunto de arquivos fornecido.", fixTarget:"Carregue ou crie o destino, ou altere o href para um arquivo existente.", verified:"verificado", fixed:"corrigido", location:"Localização", evidence:"Evidência", next:"Próximo passo", recheck:"A reverificação não detecta mais o padrão anterior.", checks:"verificações", noUpload:"sem envio", issues:"problemas", issue:"problema", clear:"Sem achados", files:"arquivos locais", file:"arquivo local", ready:"Pronto", sample:"Amostra: index.html, about.html", email:"Endereço de e-mail" },
    es: { sc1:"Imagen sin texto alternativo", sc2:"Campo de formulario sin etiqueta asociada", sc3:"Enlace interno con destino inexistente", noAlt:"no tiene atributo alt.", addAlt:"Añade una descripción alternativa útil. Si es decorativa, usa alt=\"\".", noLabel:"no tiene etiqueta asociada ni nombre accesible.", addLabel:"Añade una etiqueta asociada antes del campo.", addName:"Asigna un id y una etiqueta, o añade aria-label.", missingTarget:"no está en el conjunto de archivos proporcionado.", fixTarget:"Carga o crea el destino, o actualiza el href a un archivo existente.", verified:"verificado", fixed:"corregido", location:"Ubicación", evidence:"Evidencia", next:"Siguiente paso", recheck:"La nueva revisión ya no detecta el patrón anterior.", checks:"controles", noUpload:"sin carga", issues:"problemas", issue:"problema", clear:"Sin hallazgos", files:"archivos locales", file:"archivo local", ready:"Listo", sample:"Muestra: index.html, about.html", email:"Correo electrónico" },
    fr: { sc1:"Image sans texte alternatif", sc2:"Champ de formulaire sans libellé associé", sc3:"Lien interne vers une destination absente", noAlt:"n’a pas d’attribut alt.", addAlt:"Ajoutez une description alternative utile. Si l’image est décorative, utilisez alt=\"\".", noLabel:"n’a ni libellé associé ni nom accessible.", addLabel:"Ajoutez un libellé associé avant le champ.", addName:"Ajoutez un id et un libellé, ou un aria-label.", missingTarget:"ne figure pas dans les fichiers fournis.", fixTarget:"Chargez ou créez la destination, ou corrigez le href.", verified:"vérifié", fixed:"corrigé", location:"Emplacement", evidence:"Preuve", next:"Étape suivante", recheck:"La nouvelle vérification ne détecte plus le motif précédent.", checks:"contrôles", noUpload:"aucun envoi", issues:"problèmes", issue:"problème", clear:"Aucun résultat", files:"fichiers locaux", file:"fichier local", ready:"Prêt", sample:"Exemple : index.html, about.html", email:"Adresse e-mail" },
    de: { sc1:"Bild ohne Alternativtext", sc2:"Formularfeld ohne zugeordnetes Label", sc3:"Interner Link verweist auf ein fehlendes Ziel", noAlt:"hat kein alt-Attribut.", addAlt:"Fügen Sie eine passende Alternativbeschreibung hinzu. Bei dekorativen Bildern verwenden Sie alt=\"\".", noLabel:"hat kein zugeordnetes Label oder zugänglichen Namen.", addLabel:"Fügen Sie vor dem Feld ein zugeordnetes Label ein.", addName:"Vergeben Sie eine id mit Label oder ergänzen Sie aria-label.", missingTarget:"ist nicht im bereitgestellten Dateisatz enthalten.", fixTarget:"Laden oder erstellen Sie das Ziel oder ändern Sie den href.", verified:"bestätigt", fixed:"behoben", location:"Fundstelle", evidence:"Nachweis", next:"Nächster Schritt", recheck:"Die Nachprüfung erkennt das vorherige Muster nicht mehr.", checks:"Prüfungen", noUpload:"kein Upload", issues:"Probleme", issue:"Problem", clear:"Keine Befunde", files:"lokale Dateien", file:"lokale Datei", ready:"Bereit", sample:"Beispiel: index.html, about.html", email:"E-Mail-Adresse" },
    it: { sc1:"Immagine senza testo alternativo", sc2:"Campo del modulo senza etichetta associata", sc3:"Link interno verso una destinazione mancante", noAlt:"non ha l’attributo alt.", addAlt:"Aggiungi una descrizione alternativa utile. Se l’immagine è decorativa, usa alt=\"\".", noLabel:"non ha un’etichetta associata o un nome accessibile.", addLabel:"Aggiungi un’etichetta associata prima del campo.", addName:"Assegna un id con etichetta o aggiungi aria-label.", missingTarget:"non è presente nei file forniti.", fixTarget:"Carica o crea la destinazione, oppure aggiorna l’href.", verified:"verificato", fixed:"corretto", location:"Posizione", evidence:"Prova", next:"Passaggio successivo", recheck:"La nuova verifica non rileva più il pattern precedente.", checks:"controlli", noUpload:"nessun invio", issues:"problemi", issue:"problema", clear:"Nessun rilievo", files:"file locali", file:"file locale", ready:"Pronto", sample:"Esempio: index.html, about.html", email:"Indirizzo e-mail" }
  };
  const d = DYNAMIC_COPY[locale] || DYNAMIC_COPY.en;

  const SAMPLE_HTML = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Studio Notes</title>
</head>
<body>
  <nav>
    <a href="index.html">Home</a>
    <a href="about.html">About</a>
    <a href="contact.html">Contact</a>
  </nav>

  <main>
    <img src="project-cover.jpg">
    <form>
      <input type="email" id="email-input" placeholder="you@email.com">
      <button type="submit">Subscribe</button>
    </form>
  </main>
</body>
</html>`;

  const state = {
    fileNames: new Set(["index.html", "about.html"]),
    checkedFile: "index.html",
    previousFindings: null,
    report: null,
  };

  const htmlInput = document.querySelector("#html-input");
  const fileInput = document.querySelector("#file-input");
  const fileStatus = document.querySelector("#file-status");
  const runButton = document.querySelector("#run-button");
  const fixButton = document.querySelector("#fix-button");
  const sampleButton = document.querySelector("#sample-button");
  const downloadButton = document.querySelector("#download-button");
  const emptyState = document.querySelector("#empty-state");
  const resultsContent = document.querySelector("#results-content");
  const findingsNode = document.querySelector("#findings");
  const runStatus = document.querySelector("#run-status");

  htmlInput.value = SAMPLE_HTML;

  function inspect(source) {
    return SiteCheckEngine.inspect(source, state.fileNames, state.checkedFile).map(f => ({
      id:f.id, fingerprint:f.fingerprint, title:d[f.id==='SC-001'?'sc1':f.id==='SC-002'?'sc2':'sc3'],
      severity:f.id==='SC-003'?'medium':'high', file:state.checkedFile,
      location:f.line ? `L${f.line}` : 'HTML',
      evidence:f.markup+' '+(f.id==='SC-001'?d.noAlt:f.id==='SC-002'?d.noLabel:`→ ${f.target}: ${d.missingTarget}`),
      recommendation:f.id==='SC-001'?d.addAlt:f.id==='SC-002'?d.addName:d.fixTarget,
      state:'open'
    }));
  }
  function compare(previous,current) { return SiteCheckEngine.compare(previous,current); }

  function countByState(findings, name) {
    return findings.filter((finding) => finding.state === name).length;
  }

  function renderFinding(finding) {
    const article = document.createElement("article");
    article.className = `finding ${finding.state}`;

    const header = document.createElement("div");
    header.className = "finding-header";
    const id = document.createElement("span");
    id.className = "finding-id";
    id.textContent = finding.id;
    const title = document.createElement("h3");
    title.textContent = finding.state === "fixed" ? `${finding.title} — ${d.verified}` : finding.title;
    const severity = document.createElement("span");
    severity.className = `severity ${finding.severity}`;
    severity.textContent = finding.state === "fixed" ? d.fixed : finding.severity;
    header.append(id, title, severity);

    const body = document.createElement("div");
    body.className = "finding-body";
    const list = document.createElement("dl");
    [[d.location, `${finding.file}, ${finding.location}`], [d.evidence, finding.evidence], [d.next, finding.recommendation]].forEach(([term, value]) => {
      const dt = document.createElement("dt");
      const dd = document.createElement("dd");
      dt.textContent = term;
      dd.textContent = value;
      list.append(dt, dd);
    });
    body.append(list);
    article.append(header, body);
    return article;
  }

  function runReview() {
    const startedAt = performance.now();
    let current; try { current=inspect(htmlInput.value); } catch { runStatus.textContent=extra.limit; return; }
    const compared = compare(state.previousFindings, current);
    const duration = Math.max(0.1, performance.now() - startedAt);

    state.report = {
      schema_version: "web-demo-2",
      checked_file: state.checkedFile,
      generated_at: new Date().toISOString(),
      execution: "local-browser",
      checks_run: 3,
      scope: "Static patterns only; external URLs, root-relative routes and base URLs are not tested. Missing targets mean absent from supplied files, not confirmed HTTP 404.",
      duration_ms: Number(duration.toFixed(1)),
      total_findings: compared.length,
      comparison_summary: {
        open: countByState(compared, "open"),
        fixed: countByState(compared, "fixed"),
        regressed: countByState(compared, "regressed"),
      },
      findings: compared,
    };

    state.previousFindings = current;
    document.querySelector("#open-count").textContent = state.report.comparison_summary.open;
    document.querySelector("#fixed-count").textContent = state.report.comparison_summary.fixed;
    document.querySelector("#regression-count").textContent = state.report.comparison_summary.regressed;
    document.querySelector("#result-time").textContent = `3 ${d.checks} · ${duration.toFixed(1)} ms · ${d.noUpload}`;
    runStatus.textContent = current.length ? `${current.length} ${current.length === 1 ? d.issue : d.issues}` : d.clear;
    findingsNode.replaceChildren(...compared.map(renderFinding));
    emptyState.hidden = true;
    resultsContent.hidden = false;
    fixButton.disabled = htmlInput.value !== SAMPLE_HTML;
  }

  function applyLabelFix() {
    if(htmlInput.value!==SAMPLE_HTML)return;
    if(!state.previousFindings)runReview();
    htmlInput.value=SAMPLE_HTML.replace('<input type="email"', '<label for="email-input">'+d.email+'</label>\n      <input type="email"');
    runReview(); htmlInput.focus();
  }
  function clearResult(){
    state.previousFindings=null;state.report=null;fixButton.disabled=true;
    emptyState.hidden=false;resultsContent.hidden=true;runStatus.textContent=d.ready;
  }
  let loadedFiles=new Map();
  async function selectFile(name){
    const f=loadedFiles.get(name);if(!f)return;
    if(f.size>2_000_000){runStatus.textContent=extra.limit;return;}
    state.checkedFile=name;htmlInput.value=await f.text();clearResult();
    fileStatus.textContent=`${state.fileNames.size} ${d.files} · ${name}`;
    document.querySelector('.editor-panel .panel-bar span').textContent=name;
  }
  async function loadFiles(files){
    const all=Array.from(files);if(!all.length)return;
    if(all.length>3000){runStatus.textContent=extra.limit;return;}
    const fromFolder=!!all[0].webkitRelativePath;
    const paths=all.map(f=>[fromFolder?f.webkitRelativePath.split('/').slice(1).join('/'):f.name,f]);
    const html=paths.filter(([path])=>/\.html?$/i.test(path));
    if(!html.length){runStatus.textContent=extra.noHtml;return;}
    loadedFiles=new Map(html);state.fileNames=new Set(paths.map(([path])=>path));
    fileSelect.replaceChildren(...html.map(([path])=>new Option(path,path)));
    fileSelect.hidden=false;
    const primary=html.find(([path])=>/^index\.html?$/i.test(path))||html[0];
    fileSelect.value=primary[0];await selectFile(primary[0]);
  }

  function resetSample() {
    fileSelect.hidden=true;loadedFiles.clear();
    document.querySelector(".editor-panel .panel-bar span").textContent="index.html";
    state.fileNames = new Set(["index.html", "about.html"]);
    state.checkedFile = "index.html";
    state.previousFindings = null;
    state.report = null;
    htmlInput.value = SAMPLE_HTML;
    fileInput.value = "";
    fileStatus.textContent = d.sample;
    fixButton.disabled = true;
    emptyState.hidden = false;
    resultsContent.hidden = true;
    runStatus.textContent = d.ready;
  }

  function downloadReport() {
    if (!state.report) return;
    const blob = new Blob([JSON.stringify(state.report, null, 2)], { type: "application/json" });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = "sitecheck-browser-report.json";
    link.click();
    URL.revokeObjectURL(link.href);
  }

  const extraValues={"en": ["Open project folder", "HTML page", "2 MB of HTML maximum; up to 3,000 project files.", "Choose at least one HTML file.", "Only relative links are checked against supplied files. External URLs, root-relative routes and pages with a base URL are not tested. The label fix applies to the sample only."], "pt-br": ["Abrir pasta do projeto", "Página HTML", "Limite de 2 MB de HTML e 3.000 arquivos por projeto.", "Escolha ao menos um arquivo HTML.", "Somente links relativos são comparados aos arquivos fornecidos. URLs externas, rotas iniciadas por / e páginas com base URL ficam fora desta verificação. A correção automática de rótulo vale só para o exemplo."], "es": ["Abrir carpeta del proyecto", "Página HTML", "Máximo 2 MB de HTML y 3.000 archivos.", "Selecciona al menos un archivo HTML.", "Solo se comprueban enlaces relativos con los archivos elegidos. URLs externas, rutas / y páginas con URL base quedan fuera. La corrección de etiqueta solo se aplica al ejemplo."], "fr": ["Ouvrir le dossier du projet", "Page HTML", "Maximum 2 Mo de HTML et 3 000 fichiers.", "Choisissez au moins un fichier HTML.", "Seuls les liens relatifs sont comparés aux fichiers choisis. URLs externes, routes / et pages avec URL de base sont exclues. La correction du libellé concerne uniquement l’exemple."], "de": ["Projektordner öffnen", "HTML-Seite", "Maximal 2 MB HTML und 3.000 Dateien.", "Wählen Sie mindestens eine HTML-Datei.", "Nur relative Links werden mit den gewählten Dateien verglichen. Externe URLs, /-Routen und Seiten mit Basis-URL sind ausgenommen. Die Label-Korrektur gilt nur für das Beispiel."], "it": ["Apri cartella del progetto", "Pagina HTML", "Massimo 2 MB di HTML e 3.000 file.", "Scegli almeno un file HTML.", "Solo i link relativi vengono confrontati con i file scelti. URL esterni, percorsi / e pagine con URL di base sono esclusi. La correzione dell’etichetta vale solo per l’esempio."]};
  const e=extraValues[locale]||extraValues.en;
  const extra={limit:e[2],noHtml:e[3]};
  const folderInput=document.createElement('input');folderInput.type='file';folderInput.multiple=true;folderInput.webkitdirectory=true;folderInput.hidden=true;
  const folderButton=document.createElement('button');folderButton.type='button';folderButton.className='text-button';folderButton.textContent=e[0];folderButton.onclick=()=>folderInput.click();
  const fileSelect=document.createElement('select');fileSelect.setAttribute('aria-label',e[1]);fileSelect.hidden=true;
  const note=document.createElement('p');note.className='scope-detail';note.textContent=e[4];
  document.querySelector('.file-row').append(folderButton,folderInput,fileSelect,note);
  fileInput.removeAttribute('accept');
  folderInput.addEventListener('change',ev=>loadFiles(ev.target.files));
  fileSelect.addEventListener('change',()=>selectFile(fileSelect.value));
  htmlInput.addEventListener('input',()=>{fixButton.disabled=htmlInput.value!==SAMPLE_HTML;runStatus.textContent=d.ready;});

  runButton.addEventListener("click", runReview);
  fixButton.addEventListener("click", applyLabelFix);
  sampleButton.addEventListener("click", resetSample);
  downloadButton.addEventListener("click", downloadReport);
  fileInput.addEventListener("change", (event) => loadFiles(event.target.files));
  const languageSelect = document.querySelector("#language-select");
  languageSelect?.addEventListener("change", (event) => {
    const next = event.target.value;
    localStorage.setItem("sitecheck-language", next);
    window.location.assign(`/contribuicoes/sitecheck/${next}/`);
  });

  window.SiteCheckDemo = { inspect, compare, sample: SAMPLE_HTML };
})();
