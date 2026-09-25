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
                "Reverificação não detectou mais esta falha. "
                "O checker passou sem encontrar o padrão anterior."
            )
            merged.append(f)

        elif in_after and not in_before:
            # novo achado: surgiu depois da correção e deve ficar visível
            # como regressão, em vez de ser misturado aos itens já abertos.
            f = copy.deepcopy(after_by_id[fid])
            f["state"] = "regressed"
            f["recheck_result"] = (
                "A reverificação detectou esta falha somente no estado posterior. "
                "Revise a mudança antes de aceitar a correção."
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
  display: flex; gap: 1.5rem; margin-bottom: 2rem;
  padding: 1rem 1.25rem;
  background: #f7f8fa; border: 1px solid #e5e7eb; border-radius: 6px;
}
.summary-item { font-size: 0.85rem; }
.summary-label { color: #57606a; margin-right: 0.35rem; }
.summary-value { font-weight: 600; }
.fixed-section-label {
  font-size: 0.75rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.05em; color: #57606a;
  margin: 1.5rem 0 0.75rem; padding-bottom: 0.35rem;
  border-bottom: 1px solid #e5e7eb;
}
.scope-note {
  margin-top: 1.5rem; padding: 0.75rem 1rem;
  background: #f7f8fa; border: 1px solid #e5e7eb; border-radius: 6px;
  font-size: 0.82rem; color: #57606a;
}
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
        f'    <span class="summary-label">Ainda abertos:</span>'
        f'    <span class="summary-value">{still_open}</span>'
        f'  </div>'
        f'  <div class="summary-item">'
        f'    <span class="summary-label">Corrigidos nesta sessão:</span>'
        f'    <span class="summary-value">{fixed}</span>'
        f'  </div>'
        f'  <div class="summary-item">'
        f'    <span class="summary-label">Novos / regredidos:</span>'
        f'    <span class="summary-value">{regressed}</span>'
        f'  </div>'
        f'</div>'
    )

    open_html = ""
    if open_findings:
        open_html = (
            '<p class="fixed-section-label">Achados ainda abertos</p>'
            + "\n".join(_finding_html(f, i) for i, f in enumerate(open_findings))
        )

    regressed_html = ""
    if regressed_findings:
        regressed_html = (
            '<p class="fixed-section-label">Novos achados ou regressões</p>'
            + "\n".join(_finding_html(f, i) for i, f in enumerate(regressed_findings))
        )

    fixed_html = ""
    if fixed_findings:
        fixed_html = (
            '<p class="fixed-section-label">Corrigidos nesta sessão</p>'
            + "\n".join(_finding_html(f, i) for i, f in enumerate(fixed_findings))
        )

    scope_note = (
        '<div class="scope-note">'
        'Esta comparação cobre apenas os testes executados. '
        'Achados abertos foram priorizados pelo autor — não estão aqui por descuido.'
        '</div>'
    )

    combined_css = _CSS + _COMPARISON_EXTRA_CSS

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SiteCheck — comparação antes/depois</title>
  <style>{combined_css}</style>
</head>
<body>
  <h1>SiteCheck — comparação antes/depois</h1>
  <p class="meta">Arquivo verificado: <code>{checked}</code> &nbsp;·&nbsp; {ts}</p>
  {summary_html}
  {open_html}
  {regressed_html}
  {fixed_html}
  {scope_note}
  <footer>Gerado por SiteCheck · stdlib Python 3 · sem serviços externos</footer>
</body>
</html>"""

    Path(out_path).write_text(html, encoding="utf-8")
