#!/usr/bin/env python3
"""
sitecheck.py — ponto de entrada da CLI.

Uso:
    python sitecheck.py <arquivo.html> [--out-dir DIR]

Saídas:
    <out-dir>/report.json  — achados em formato estruturado
    <out-dir>/report.html  — relatório legível em navegador

Padrão de out-dir: ./sitecheck-output
"""

import sys
import json
import argparse
from pathlib import Path

# permite execução sem instalação de pacote
sys.path.insert(0, str(Path(__file__).parent))

from src.checkers import run_all
from src.schema   import make_report
from src.reporter import write_json, write_html, _sorted_findings, _SEVERITY_LABEL, _STATE_LABEL


def _print_summary(report: dict) -> None:
    findings = _sorted_findings(report["findings"])
    checked  = report["checked_file"]

    print(f"\nSiteCheck — {checked}")
    print("─" * 52)

    if not findings:
        print(
            "Nenhuma falha encontrada pelos testes executados.\n"
            "Isso não equivale a uma declaração de que o site está livre de problemas."
        )
        print("─" * 52)
        return

    for f in findings:
        sev   = _SEVERITY_LABEL.get(f["severity"], f["severity"])
        state = _STATE_LABEL.get(f["state"], f["state"])
        print(f"\n[{f['id']}] {f['title']}")
        print(f"  Severidade : {sev}")
        print(f"  Estado     : {state}")
        print(f"  Local      : {f['location']}")
        print(f"  Evidência  : {f['evidence']}")
        print(f"  Correção   : {f['recommendation']}")

    print("\n" + "─" * 52)
    n = len(findings)
    print(f"{n} achado{'s' if n != 1 else ''} encontrado{'s' if n != 1 else ''}.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Verifica um arquivo HTML e gera relatório de achados.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("html_file", help="Caminho para o arquivo HTML a verificar.")
    parser.add_argument(
        "--out-dir",
        default="sitecheck-output",
        help="Diretório de saída para report.json e report.html (padrão: sitecheck-output).",
    )
    args = parser.parse_args(argv)

    # Preserve o caminho informado no relatório. Isso deixa a evidência
    # compartilhável e evita gravar o caminho pessoal da máquina do autor.
    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"Erro: arquivo não encontrado — {html_path}", file=sys.stderr)
        sys.exit(1)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    html_source = html_path.read_text(encoding="utf-8")
    findings    = run_all(html_source, str(html_path))
    report      = make_report(findings, str(html_path))

    json_out = out_dir / "report.json"
    html_out = out_dir / "report.html"

    write_json(report, json_out)
    write_html(report, html_out)

    _print_summary(report)

    print(f"\nRelatório salvo em:")
    print(f"  JSON  → {json_out}")
    print(f"  HTML  → {html_out}\n")

    # exit code 1 se há achados (útil em pipelines CI)
    sys.exit(1 if findings else 0)


if __name__ == "__main__":
    main()
