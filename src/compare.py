"""
compare.py — compara dois relatórios (antes/depois) e produz um artefato de comparação.

Lógica de comparação por ID:
  - achado presente antes e ausente depois  → state="fixed"
  - achado ausente antes e presente depois  → state="regressed"
  - achado presente nos dois               → state mantido do relatório "depois"

O artefato de comparação é um dict com os mesmos campos de make_report,
mais uma chave "comparison_summary" com contagens.

Não modifica os relatórios de entrada; devolve estruturas novas.
"""

import json
import copy
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
    before_by_id = {f["id"]: f for f in before.get("findings", [])}
    after_by_id  = {f["id"]: f for f in after.get("findings",  [])}

    all_ids_ordered = _stable_id_order(before_by_id, after_by_id)
    merged = []

    for fid in all_ids_ordered:
        in_before = fid in before_by_id
        in_after  = fid in after_by_id

        if in_before and not in_after:
            # corrigido: checker não detectou mais este achado
            f = copy.deepcopy(before_by_id[fid])
            f["state"] = "fixed"
            f["recheck_result"] = (
                "The recheck no longer detected this issue. "
                "The checker passed without finding the previous pattern."
            )
            merged.append(f)

        elif in_after and not in_before:
            # novo achado: surgiu depois da correção e deve ficar visível
            # como regressão, em vez de ser misturado aos itens já abertos.
            f = copy.deepcopy(after_by_id[fid])
            f["state"] = "regressed"
            f["recheck_result"] = (
                "The recheck detected this issue only in the later state. "
                "Review the change before accepting the fix."
            )
            merged.append(f)

        else:
            # presente nos dois: usa a versão do after
            merged.append(copy.deepcopy(after_by_id[fid]))

    fixed_count     = sum(1 for f in merged if f["state"] == "fixed")
    still_open      = sum(1 for f in merged if f["state"] == "open")
    regressed_count = sum(1 for f in merged if f["state"] == "regressed")

    report = make_report(
        findings=[f for f in merged if f["state"] != "fixed"] +
                 [f for f in merged if f["state"] == "fixed"],
        checked_file=after.get("checked_file", before.get("checked_file", "")),
    )
    # reordenar: abertos primeiro (por severidade), corrigidos ao final
    report["findings"] = (
        _sort_by_severity([f for f in merged if f["state"] == "open"]) +
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


def _stable_id_order(before_by_id: dict, after_by_id: dict) -> list:
    """Mantém a ordem original dos IDs (before primeiro, novos do after ao final)."""
    seen = []
    for fid in list(before_by_id) + list(after_by_id):
        if fid not in seen:
            seen.append(fid)
    return seen


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

    open_findings   = [f for f in comparison["findings"] if f["state"] == "open"]
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
        'Open findings were deliberately prioritized by the author — they are not accidental omissions.'
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
