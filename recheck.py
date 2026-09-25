#!/usr/bin/env python3
"""
recheck.py — gera artefato de comparação antes/depois.

Uso:
    python3 recheck.py <before-report.json> <after-report.json> [--out-dir DIR]

Saídas em <out-dir> (padrão: sitecheck-output/comparison):
    comparison.json  — relatório de comparação estruturado
    comparison.html  — página legível com achados separados por estado
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.compare import compare_reports, write_comparison_html
from src.reporter import write_json, _SEVERITY_LABEL, _STATE_LABEL, _sorted_findings


def _print_comparison(comp: dict) -> None:
    summary = comp.get("comparison_summary", {})
    checked = comp.get("checked_file", "")

    print(f"\nSiteCheck — before/after comparison")
    print(f"File: {checked}")
    print("─" * 52)
    print(f"  Fixed this session : {summary.get('fixed', 0)}")
    print(f"  Still open         : {summary.get('still_open', 0)}")
    print(f"  New / regressed    : {summary.get('regressed', 0)}")
    print("─" * 52)

    for f in comp["findings"]:
        sev   = _SEVERITY_LABEL.get(f["severity"], f["severity"])
        state = _STATE_LABEL.get(f["state"], f["state"])
        print(f"\n[{f['id']}] {f['title']}")
        print(f"  Severity : {sev}")
        print(f"  State    : {state}")
        if f.get("recheck_result"):
            print(f"  Recheck  : {f['recheck_result']}")

    print()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Compares two SiteCheck reports and generates a before/after artifact.",
    )
    parser.add_argument("before_json", help="Path to the earlier report.json.")
    parser.add_argument("after_json",  help="Path to the later report.json.")
    parser.add_argument(
        "--out-dir",
        default="sitecheck-output/comparison",
        help="Output directory (default: sitecheck-output/comparison).",
    )
    args = parser.parse_args(argv)

    before_path = Path(args.before_json)
    after_path  = Path(args.after_json)

    for p in (before_path, after_path):
        if not p.exists():
            print(f"Error: file not found — {p}", file=sys.stderr)
            sys.exit(1)

    before = json.loads(before_path.read_text(encoding="utf-8"))
    after  = json.loads(after_path.read_text(encoding="utf-8"))

    comp = compare_reports(before, after)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    json_out = out_dir / "comparison.json"
    html_out = out_dir / "comparison.html"

    write_json(comp, json_out)
    write_comparison_html(comp, html_out)

    _print_comparison(comp)

    print(f"Comparison saved to:")
    print(f"  JSON  → {json_out}")
    print(f"  HTML  → {html_out}\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
