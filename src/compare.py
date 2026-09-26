"""
compare.py — compara dois relatórios (antes/depois) e produz um artefato de comparação.

Lógica de comparação por instancia (fingerprint; fallback de localizacao):
  - achado presente antes e ausente depois  → state="fixed"
  - achado ausente antes e presente depois  → state="regressed"
  - achado presente nos dois               → state mantido do relatório "depois"

O artefato de comparação é um dict com os mesmos campos de make_report,
mais uma chave "comparison_summary" com contagens.

Não modifica os relatórios de entrada; devolve estruturas novas.
"""

import json
import copy
import re
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

from .schema import make_report
from .reporter import write_json, _esc, _SEVERITY_LABEL, _STATE_LABEL, _CSS


# ── lógica principal ──────────────────────────────────────────────────────────

def compare_reports(before: dict, after: dict) -> dict:
    """
    Recebe dois relatórios no formato de make_report e devolve um
    relatório de comparação.

    Regra de mesclagem:
      - Achado no before mas não no after  → cópia do before com state="fixed"
        e recheck_result indicando que o checker não detectou mais a falha.
      - Achado no after mas não no before  → incluído como "regressed" (novo).
      - Achado nos dois                   → versão do after (estado atualizado).
    """
    # New reports match by instance fingerprint. Legacy reports keep a bounded
    # fallback based on rule + normalized location, including mixed old/new pairs.
    def legacy(f):
        location = re.sub(r"^(?:line|linha) \d+\s*[—:-]?\s*", "", f.get("location", ""))
        return (f["id"], location)

    previous = before.get("findings", [])
    fingerprints, locations, old_locations = defaultdict(deque), defaultdict(deque), defaultdict(deque)
    for index, f in enumerate(previous):
        locations[legacy(f)].append(index)
        if f.get("fingerprint"):
            fingerprints[f["fingerprint"]].append(index)
        else:
            old_locations[legacy(f)].append(index)
    used = set()
    def take(queue):
        while queue and queue[0] in used:
            queue.popleft()
        if queue:
            used.add(queue.popleft())
            return True
        return False
    merged = []
    for finding in after.get("findings", []):
        f = copy.deepcopy(finding)
        if f.get("fingerprint"):
            matched = take(fingerprints[f["fingerprint"]]) or take(old_locations[legacy(f)])
        else:
            matched = take(locations[legacy(f)])
        if not matched:
            f["state"] = "regressed"
            f["recheck_result"] = "The recheck detected this instance only in the later report. Review the change."
        merged.append(f)
    for index, finding in enumerate(previous):
        if index not in used:
            f = copy.deepcopy(finding)
            f["state"] = "fixed"
            f["recheck_result"] = "The recheck no longer detected this instance of the previous pattern."
            merged.append(f)

    fixed_count     = sum(1 for f in merged if f["state"] == "fixed")
    still_open      = sum(1 for f in merged if f["state"] in ("open", "unverified"))
    regressed_count = sum(1 for f in merged if f["state"] == "regressed")

    report = make_report(
        findings=[f for f in merged if f["state"] != "fixed"] +
                 [f for f in merged if f["state"] == "fixed"],
        checked_file=after.get("checked_file", before.get("checked_file", "")),
    )
    # reordenar: abertos primeiro (por severidade), corrigidos ao final
    report["findings"] = (
        _sort_by_severity([f for f in merged if f["state"] in ("open", "unverified")]) +
        _sort_by_severity([f for f in merged if f["state"] == "regressed"]) +
        _sort_by_severity([f for f in merged if f["state"] == "fixed"])
    )
    report["total_findings"] = len(report["findings"])
    report["comparison_summary"] = {
        "fixed":      fixed_count,
        "still_open": still_open,
        "regressed":  regressed_count,
    }
    return report


def _sort_by_severity(findings: list) -> list:
    order = {"high": 0, "medium": 1, "low": 2}
    return sorted(findings, key=lambda f: order.get(f["severity"], 9))


# ── HTML de comparação ────────────────────────────────────────────────────────

_COMPARISON_EXTRA_CSS = """
.summary-bar {
  display: grid; grid-template-columns: repeat(3, 1fr); margin-bottom: 38px;
  border: 1px solid var(--line); background: var(--ink); color: var(--paper);
}
.summary-item { display: flex; flex-direction: column-reverse; gap: 10px; min-height: 126px; padding: 18px; border-right: 1px solid rgba(242,238,228,.22); }
.summary-item:last-child { border-right: 0; }
.summary-label { color: rgba(242,238,228,.72); font-size: .62rem; font-weight: 750; letter-spacing: .11em; text-transform: uppercase; }
.summary-value { font: 400 3.5rem/1 var(--serif); }
.fixed-section-label {
  margin: 38px 0 12px; padding-bottom: 9px; border-bottom: 1px solid var(--line);
  font-size: .66rem; font-weight: 750; letter-spacing: .14em; text-transform: uppercase;
}
.scope-note {
  margin-top: 38px; padding: 18px 20px 18px 56px; border: 1px solid var(--ink);
  background: var(--acid); font: 400 1.02rem/1.45 var(--serif); position: relative;
}
.scope-note::before { content: "↳"; position: absolute; left: 20px; top: 15px; font: 700 1.25rem var(--sans); }
@media (max-width: 760px) { .summary-bar { grid-template-columns: 1fr; }.summary-item { border-right: 0; border-bottom: 1px solid rgba(242,238,228,.22); } }
"""


def write_comparison_html(comparison: dict, out_path: str | Path) -> None:
    """Escreve o HTML de comparação antes/depois."""
    from .reporter import _finding_html

    summary = comparison.get("comparison_summary", {})
    fixed      = summary.get("fixed", 0)
    still_open = summary.get("still_open", 0)
    regressed  = summary.get("regressed", 0)
    checked    = _esc(comparison.get("checked_file", ""))
    ts         = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    open_findings   = [f for f in comparison["findings"] if f["state"] in ("open", "unverified")]
    regressed_findings = [f for f in comparison["findings"] if f["state"] == "regressed"]
    fixed_findings  = [f for f in comparison["findings"] if f["state"] == "fixed"]

    summary_html = (
        f'<div class="summary-bar">'
        f'  <div class="summary-item">'
        f'    <span class="summary-label">Still open:</span>'
        f'    <span class="summary-value">{still_open}</span>'
        f'  </div>'
        f'  <div class="summary-item">'
        f'    <span class="summary-label">Fixed this session:</span>'
        f'    <span class="summary-value">{fixed}</span>'
        f'  </div>'
        f'  <div class="summary-item">'
        f'    <span class="summary-label">New / regressed:</span>'
        f'    <span class="summary-value">{regressed}</span>'
        f'  </div>'
        f'</div>'
    )

    open_html = ""
    if open_findings:
        open_html = (
            '<p class="fixed-section-label">Findings still open</p>'
            + "\n".join(_finding_html(f, i) for i, f in enumerate(open_findings))
        )

    regressed_html = ""
    if regressed_findings:
        regressed_html = (
            '<p class="fixed-section-label">New findings or regressions</p>'
            + "\n".join(_finding_html(f, i) for i, f in enumerate(regressed_findings))
        )

    fixed_html = ""
    if fixed_findings:
        fixed_html = (
            '<p class="fixed-section-label">Fixed this session</p>'
            + "\n".join(_finding_html(f, i) for i, f in enumerate(fixed_findings))
        )

    scope_note = (
        '<div class="scope-note">'
        'This comparison covers only the checks that were run. '
        'Open findings still require review; disappearance means this pattern was not detected on the recheck, not that every site issue is fixed.'
        '</div>'
    )

    combined_css = _CSS + _COMPARISON_EXTRA_CSS

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SiteCheck — before/after comparison</title>
  <style>{combined_css}</style>
</head>
<body><main class="report-shell">
  <header class="report-header"><span class="brand">SiteCheck</span><span class="edition">Before / After</span></header>
  <section class="report-intro"><div><p class="eyebrow">Verified recheck</p><h1>What<br>changed.</h1></div><p class="meta"><code>{checked}</code>{ts}<br>Same checks, two comparable states.</p></section>
{summary_html}
{open_html}
{regressed_html}
{fixed_html}
{scope_note}
  <footer><span>SiteCheck · Python 3</span><span>Human decision · local evidence</span></footer>
</main>
</body>
</html>"""

    Path(out_path).write_text(html, encoding="utf-8")
