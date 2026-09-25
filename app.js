(function () {
  "use strict";

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

  function lineForNode(source, node) {
    if (!node || !node.outerHTML) return 1;
    const start = source.indexOf(node.outerHTML);
    if (start < 0) return 1;
    return source.slice(0, start).split("\n").length;
  }

  function conciseMarkup(node) {
    return node.outerHTML.replace(/\s+/g, " ").slice(0, 140);
  }

  function makeFinding(id, title, severity, line, evidence, recommendation) {
    return {
      id,
      title,
      severity,
      file: state.checkedFile,
      location: `line ${line}`,
      evidence,
      recommendation,
      state: "open",
    };
  }

  function inspect(source) {
    const documentTree = new DOMParser().parseFromString(source, "text/html");
    const findings = [];

    documentTree.querySelectorAll("img:not([alt])").forEach((image) => {
      const line = lineForNode(source, image);
      findings.push(makeFinding(
        "SC-001",
        "Image missing alternative text",
        "high",
        line,
        `${conciseMarkup(image)} has no alt attribute.`,
        "Add a useful alt description. If the image is purely decorative, use alt=\"\".",
      ));
    });

    const labeledIds = new Set(
      Array.from(documentTree.querySelectorAll("label[for]"))
        .map((label) => label.getAttribute("for"))
        .filter(Boolean),
    );
    documentTree.querySelectorAll("input").forEach((input) => {
      const ignoredTypes = new Set(["hidden", "submit", "button", "reset"]);
      const type = (input.getAttribute("type") || "text").toLowerCase();
      if (ignoredTypes.has(type)) return;
      const id = input.getAttribute("id") || "";
      const hasAria = input.hasAttribute("aria-label") || input.hasAttribute("aria-labelledby");
      if ((!id || !labeledIds.has(id)) && !hasAria) {
        const line = lineForNode(source, input);
        findings.push(makeFinding(
          "SC-002",
          "Form field missing an associated label",
          "high",
          line,
          `${conciseMarkup(input)} has no matching label or accessible name.`,
          id
            ? `Add <label for="${id}">Email address</label> before the field.`
            : "Give the field an id and matching label, or add aria-label.",
        ));
      }
    });

    documentTree.querySelectorAll("a[href]").forEach((link) => {
      const href = link.getAttribute("href").trim();
      if (!href || /^(#|mailto:|tel:|https?:\/\/)/i.test(href)) return;
      const target = href.split("#")[0].split("?")[0];
      if (target && !state.fileNames.has(target)) {
        const line = lineForNode(source, link);
        findings.push(makeFinding(
          "SC-003",
          "Internal link points to a missing destination",
          "medium",
          line,
          `${conciseMarkup(link)} targets “${target}”, which is not in the supplied file set.`,
          `Upload or create ${target}, or update the href to an existing destination.`,
        ));
      }
    });

    return findings;
  }

  function compare(previous, current) {
    if (!previous) return current;
    const previousById = new Map(previous.map((finding) => [finding.id, finding]));
    const currentById = new Map(current.map((finding) => [finding.id, finding]));
    const compared = current.map((finding) => ({
      ...finding,
      state: previousById.has(finding.id) ? "open" : "regressed",
    }));
    previousById.forEach((finding, id) => {
      if (!currentById.has(id)) {
        compared.push({
          ...finding,
          state: "fixed",
          evidence: "The recheck no longer detects the previous pattern.",
        });
      }
    });
    return compared;
  }

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
    title.textContent = finding.state === "fixed" ? `${finding.title} — verified` : finding.title;
    const severity = document.createElement("span");
    severity.className = `severity ${finding.severity}`;
    severity.textContent = finding.state === "fixed" ? "fixed" : finding.severity;
    header.append(id, title, severity);

    const body = document.createElement("div");
    body.className = "finding-body";
    const list = document.createElement("dl");
    [["Location", `${finding.file}, ${finding.location}`], ["Evidence", finding.evidence], ["Next step", finding.recommendation]].forEach(([term, value]) => {
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
    const current = inspect(htmlInput.value);
    const compared = compare(state.previousFindings, current);
    const duration = Math.max(0.1, performance.now() - startedAt);

    state.report = {
      schema_version: "web-demo-1",
      checked_file: state.checkedFile,
      generated_at: new Date().toISOString(),
      execution: "local-browser",
      checks_run: 3,
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
    document.querySelector("#result-time").textContent = `3 checks · ${duration.toFixed(1)} ms · no upload`;
    runStatus.textContent = current.length ? `${current.length} issue${current.length === 1 ? "" : "s"}` : "Clear";
    findingsNode.replaceChildren(...compared.map(renderFinding));
    emptyState.hidden = true;
    resultsContent.hidden = false;
    fixButton.disabled = !current.some((finding) => finding.id === "SC-002");
  }

  function applyLabelFix() {
    const source = htmlInput.value;
    const documentTree = new DOMParser().parseFromString(source, "text/html");
    const input = Array.from(documentTree.querySelectorAll("input")).find((candidate) => {
      const type = (candidate.getAttribute("type") || "text").toLowerCase();
      if (["hidden", "submit", "button", "reset"].includes(type)) return false;
      const id = candidate.getAttribute("id") || "";
      const hasLabel = id && documentTree.querySelector(`label[for="${CSS.escape(id)}"]`);
      return !hasLabel && !candidate.hasAttribute("aria-label") && !candidate.hasAttribute("aria-labelledby");
    });
    if (!input) return;

    const original = input.outerHTML;
    let id = input.getAttribute("id");
    let replacement = original;
    if (!id) {
      id = "sitecheck-field";
      replacement = original.replace(/^<input/, `<input id="${id}"`);
    }
    const lineStart = source.lastIndexOf("\n", source.indexOf(original)) + 1;
    const indentation = source.slice(lineStart, source.indexOf(original)).match(/^\s*/)[0];
    htmlInput.value = source.replace(original, `<label for="${id}">Email address</label>\n${indentation}${replacement}`);
    runReview();
    htmlInput.focus();
  }

  async function loadFiles(files) {
    const htmlFiles = Array.from(files).filter((file) => /\.html?$/i.test(file.name));
    if (!htmlFiles.length) return;
    state.fileNames = new Set(htmlFiles.map((file) => file.name));
    const primary = htmlFiles.find((file) => /^index\.html?$/i.test(file.name)) || htmlFiles[0];
    state.checkedFile = primary.name;
    htmlInput.value = await primary.text();
    state.previousFindings = null;
    state.report = null;
    fileStatus.textContent = `${htmlFiles.length} local file${htmlFiles.length === 1 ? "" : "s"}: ${htmlFiles.map((file) => file.name).join(", ")}`;
    fixButton.disabled = true;
    emptyState.hidden = false;
    resultsContent.hidden = true;
    runStatus.textContent = "Ready";
  }

  function resetSample() {
    state.fileNames = new Set(["index.html", "about.html"]);
    state.checkedFile = "index.html";
    state.previousFindings = null;
    state.report = null;
    htmlInput.value = SAMPLE_HTML;
    fileInput.value = "";
    fileStatus.textContent = "Sample file set: index.html, about.html";
    fixButton.disabled = true;
    emptyState.hidden = false;
    resultsContent.hidden = true;
    runStatus.textContent = "Ready";
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

  runButton.addEventListener("click", runReview);
  fixButton.addEventListener("click", applyLabelFix);
  sampleButton.addEventListener("click", resetSample);
  downloadButton.addEventListener("click", downloadReport);
  fileInput.addEventListener("change", (event) => loadFiles(event.target.files));

  window.SiteCheckDemo = { inspect, compare, sample: SAMPLE_HTML };
})();
