"""
reporter.py — gera relatório JSON e página HTML a partir de uma lista de achados.

Regras:
- Máximo de 3 achados exibidos (os primeiros da lista, ordenados por severidade).
- Relatório sem achados mostra mensagem neutra; não afirma que o site está perfeito.
- HTML é autocontido (CSS inline) e não depende de nenhum recurso externo.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}
_SEVERITY_LABEL = {"high": "Alta", "medium": "Média", "low": "Baixa"}
_STATE_LABEL    = {"open": "Aberto", "fixed": "Corrigido",
                   "regressed": "Regrediu", "unverified": "Não verificado"}

MAX_FINDINGS = 3


def _sorted_findings(findings: list[dict]) -> list[dict]:
    """Ordena por severidade e limita a MAX_FINDINGS."""
    ordered = sorted(findings, key=lambda f: _SEVERITY_ORDER.get(f["severity"], 9))
    return ordered[:MAX_FINDINGS]


# ── JSON ──────────────────────────────────────────────────────────────────────

def write_json(report: dict, out_path: str | Path) -> None:
    Path(out_path).write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── HTML ──────────────────────────────────────────────────────────────────────

_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --ink: #11130f; --paper: #f2eee4; --acid: #d8ff55;
  --cobalt: #5b63ff; --coral: #ff735f; --line: rgba(17,19,15,.17);
  --sans: "Avenir Next", Avenir, "Helvetica Neue", Arial, sans-serif;
  --serif: "Iowan Old Style", Baskerville, Georgia, serif;
  --mono: "SFMono-Regular", Consolas, monospace;
}
body { font-family: var(--sans); font-size: 15px; line-height: 1.55; color: var(--ink); background: #0c0e0c; padding: 28px; }
.report-shell { width: min(1160px, 100%); margin: 0 auto; padding: 28px 44px 38px; background: var(--paper); }
.report-header { display: flex; align-items: center; justify-content: space-between; padding-bottom: 22px; border-bottom: 1px solid var(--line); }
.brand { font-size: .8rem; font-weight: 750; letter-spacing: .18em; text-transform: uppercase; }
.brand::before { content: "●"; color: var(--cobalt); margin-right: 9px; }
.edition { font: 650 .68rem/1 var(--mono); letter-spacing: .08em; text-transform: uppercase; }
.report-intro { display: grid; grid-template-columns: 1.2fr .8fr; align-items: end; gap: 40px; padding: 58px 0 46px; }
.eyebrow { margin-bottom: 14px; font-size: .68rem; font-weight: 750; letter-spacing: .16em; text-transform: uppercase; }
h1 { font: 400 clamp(3.2rem, 7vw, 6.7rem)/.88 var(--serif); letter-spacing: -.055em; }
.meta { align-self: end; color: #4d5049; font-size: .82rem; }
.meta code { display: block; margin-bottom: 10px; color: var(--ink); }
.empty { padding: 28px; border: 1px solid var(--line); background: rgba(255,255,255,.35); font: 400 1.45rem/1.35 var(--serif); }
.finding { margin-bottom: 16px; border: 1px solid var(--line); background: rgba(255,255,255,.22); overflow: hidden; }
.finding-header { display: grid; grid-template-columns: 76px 1fr auto auto; align-items: center; gap: 14px; min-height: 76px; padding: 14px 18px; border-bottom: 1px solid var(--line); }
.finding-id { font: 700 .7rem/1 var(--mono); letter-spacing: .08em; }
.finding-title { font: 400 1.48rem/1.1 var(--serif); }
.badge { padding: 7px 10px 6px; border: 1px solid currentColor; border-radius: 999px; font-size: .62rem; font-weight: 750; letter-spacing: .09em; text-transform: uppercase; white-space: nowrap; }
.sev-high { color: #b5302d; }.sev-medium { color: #7d5c00; }.sev-low { color: #256349; }
.state-open { color: #b5302d; background: #ffe2dc; }.state-fixed { color: #1c533d; background: var(--acid); }
.state-regressed { color: #11130f; background: var(--coral); }.state-unverified { color: #4d5049; background: #dedbd2; }
.finding-body { display: grid; grid-template-columns: 1fr 1fr; gap: 0; }
.field { min-height: 112px; padding: 18px; border-right: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.field:nth-child(even) { border-right: 0; }
.field-label { margin-bottom: 7px; color: #62665d; font-size: .62rem; font-weight: 750; letter-spacing: .13em; text-transform: uppercase; }
.field-value { font-size: .86rem; }
code { padding: 3px 6px; border: 1px solid var(--line); background: rgba(255,255,255,.4); font: .78rem var(--mono); }
footer { display: flex; justify-content: space-between; margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--line); color: #62665d; font-size: .66rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; }
@media (max-width: 760px) {
  body { padding: 0; }.report-shell { padding: 22px; }.report-intro { grid-template-columns: 1fr; }.finding-header { grid-template-columns: 58px 1fr; }.badge { justify-self: start; }.finding-body { grid-template-columns: 1fr; }.field { border-right: 0; }
}
"""


def _esc(text: str) -> str:
    """Escapa caracteres HTML básicos."""
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


def _finding_html(f: dict, index: int) -> str:
    sev_class   = f"sev-{f['severity']}"
    state_class = f"state-{f['state']}"
    sev_label   = _SEVERITY_LABEL.get(f["severity"], f["severity"])
    state_label = _STATE_LABEL.get(f["state"], f["state"])

    fields = [
        ("Arquivo / localização", _esc(f["location"])),
        ("Como reproduzir",       _esc(f["reproduction"])),
        ("Evidência",             _esc(f["evidence"])),
        ("Correção recomendada",  _esc(f["recommendation"])),
    ]
    if f.get("recheck_result"):
        fields.append(("Resultado da reverificação", _esc(f["recheck_result"])))

    fields_html = "".join(
        f'<div class="field">'
        f'<div class="field-label">{label}</div>'
        f'<div class="field-value">{value}</div>'
        f'</div>'
        for label, value in fields
    )

    return (
        f'<div class="finding">'
        f'  <div class="finding-header">'
        f'    <span class="finding-id">{_esc(f["id"])}</span>'
        f'    <span class="finding-title">{_esc(f["title"])}</span>'
        f'    <span class="badge {sev_class}">Severidade {sev_label}</span>'
        f'    <span class="badge {state_class}">{state_label}</span>'
        f'  </div>'
        f'  <div class="finding-body">{fields_html}</div>'
        f'</div>'
    )


def write_html(report: dict, out_path: str | Path) -> None:
    findings = _sorted_findings(report.get("findings", []))
    checked  = _esc(report.get("checked_file", ""))
    ts       = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if findings:
        body_content = "\n".join(_finding_html(f, i) for i, f in enumerate(findings))
        summary = (
            f"{len(findings)} achado{'s' if len(findings) != 1 else ''} "
            f"encontrado{'s' if len(findings) != 1 else ''} "
            f"pelos testes executados."
        )
    else:
        body_content = (
            '<div class="empty">'
            'Nenhuma falha encontrada pelos testes executados. '
            'Isso não equivale a uma declaração de que o site está livre de problemas.'
            '</div>'
        )
        summary = "Nenhum achado encontrado pelos testes executados."

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SiteCheck — relatório</title>
  <style>{_CSS}</style>
</head>
<body><main class="report-shell">
  <header class="report-header"><span class="brand">SiteCheck</span><span class="edition">Relatório / 01</span></header>
  <section class="report-intro"><div><p class="eyebrow">Revisão verificável</p><h1>Relatório<br>de achados.</h1></div><p class="meta"><code>{checked}</code>{ts}<br>{summary}</p></section>
{body_content}
  <footer><span>SiteCheck · Python 3</span><span>Local · sem serviços externos</span></footer>
</main>
</body>
</html>"""

    Path(out_path).write_text(html, encoding="utf-8")
