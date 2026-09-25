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
body {
  font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
  font-size: 14px; line-height: 1.6;
  color: #1f2328; background: #ffffff;
  padding: 2rem;
}
h1 { font-size: 1.25rem; font-weight: 600; margin-bottom: 0.25rem; }
.meta { color: #57606a; font-size: 0.85rem; margin-bottom: 2rem; }
.empty {
  background: #f7f8fa; border: 1px solid #e5e7eb;
  border-radius: 6px; padding: 1.25rem 1.5rem;
  color: #57606a;
}
.finding {
  border: 1px solid #e5e7eb; border-radius: 6px;
  margin-bottom: 1.25rem; overflow: hidden;
}
.finding-header {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: #f7f8fa; border-bottom: 1px solid #e5e7eb;
}
.finding-id   { font-size: 0.75rem; color: #57606a; font-family: monospace; }
.finding-title{ font-weight: 600; flex: 1; }
.badge {
  font-size: 0.7rem; font-weight: 600;
  padding: 0.15rem 0.5rem; border-radius: 99px;
  text-transform: uppercase; letter-spacing: 0.04em;
}
.sev-high     { background: #fee2e2; color: #b91c1c; }
.sev-medium   { background: #fef3c7; color: #92400e; }
.sev-low      { background: #d1fae5; color: #065f46; }
.state-open       { background: #fee2e2; color: #b91c1c; }
.state-fixed      { background: #d1fae5; color: #065f46; }
.state-regressed  { background: #fef3c7; color: #92400e; }
.state-unverified { background: #f7f8fa; color: #57606a; }
.finding-body { padding: 1rem; }
.field { margin-bottom: 0.75rem; }
.field-label {
  font-size: 0.75rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.05em;
  color: #57606a; margin-bottom: 0.15rem;
}
.field-value { font-size: 0.875rem; }
code {
  font-family: "SFMono-Regular", Consolas, monospace;
  font-size: 0.82rem; background: #f7f8fa;
  padding: 0.1rem 0.35rem; border-radius: 3px;
  border: 1px solid #e5e7eb;
}
footer {
  margin-top: 2.5rem; padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
  font-size: 0.8rem; color: #57606a; text-align: center;
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
<body>
  <h1>SiteCheck — relatório</h1>
  <p class="meta">Arquivo verificado: <code>{checked}</code> &nbsp;·&nbsp; {ts} &nbsp;·&nbsp; {summary}</p>
  {body_content}
  <footer>Gerado por SiteCheck · stdlib Python 3 · sem serviços externos</footer>
</body>
</html>"""

    Path(out_path).write_text(html, encoding="utf-8")
