"""
test_compare.py — testes para src/compare.py.

Execução:
    python3 -m unittest discover test
"""

import sys
import json
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.compare import compare_reports
from src.schema  import make_finding, make_report


# ── fixtures reutilizáveis ────────────────────────────────────────────────────

def _finding(fid="SC-001", state="open", severity="high"):
    return make_finding(
        id=fid, title=f"Título {fid}", severity=severity,
        file="demo-site/index.html", location="linha 1",
        reproduction="Reprodução.", evidence="Evidência.",
        recommendation="Correção.", state=state,
    )

def _report(findings, checked="demo-site/index.html"):
    return make_report(findings, checked)


# ── casos de comparação ───────────────────────────────────────────────────────

class TestCompareReports(unittest.TestCase):

    def test_finding_in_before_and_not_after_becomes_fixed(self):
        before = _report([_finding("SC-001")])
        after  = _report([])
        comp   = compare_reports(before, after)
        self.assertEqual(len(comp["findings"]), 1)
        self.assertEqual(comp["findings"][0]["state"], "fixed")
        self.assertEqual(comp["findings"][0]["id"], "SC-001")

    def test_fixed_finding_has_recheck_result(self):
        before = _report([_finding("SC-001")])
        after  = _report([])
        comp   = compare_reports(before, after)
        self.assertIsNotNone(comp["findings"][0]["recheck_result"])
        self.assertGreater(len(comp["findings"][0]["recheck_result"]), 0)

    def test_finding_in_after_and_not_before_is_regressed(self):
        before = _report([])
        after  = _report([_finding("SC-004")])
        comp   = compare_reports(before, after)
        self.assertEqual(len(comp["findings"]), 1)
        self.assertEqual(comp["findings"][0]["state"], "regressed")
        self.assertEqual(comp["findings"][0]["id"], "SC-004")
        self.assertIsNotNone(comp["findings"][0]["recheck_result"])

    def test_new_finding_increments_regressed_count(self):
        before = _report([])
        after = _report([_finding("SC-004")])
        comp = compare_reports(before, after)
        self.assertEqual(comp["comparison_summary"]["regressed"], 1)
        self.assertEqual(comp["comparison_summary"]["still_open"], 0)

    def test_finding_in_both_uses_after_version(self):
        f_before = _finding("SC-001", state="open")
        f_after  = make_finding(
            id="SC-001", title="Título atualizado", severity="high",
            file="demo-site/index.html", location="linha 1",
            reproduction="Reprodução.", evidence="Evidência nova.",
            recommendation="Correção.", state="open",
        )
        before = _report([f_before])
        after  = _report([f_after])
        comp   = compare_reports(before, after)
        self.assertEqual(comp["findings"][0]["evidence"], "Evidência nova.")

    def test_summary_counts_are_correct(self):
        """Três antes, um corrigido, dois permanecem abertos."""
        before = _report([
            _finding("SC-001"), _finding("SC-002"), _finding("SC-003", severity="medium"),
        ])
        after = _report([
            _finding("SC-001"), _finding("SC-003", severity="medium"),
        ])
        comp = compare_reports(before, after)
        summary = comp["comparison_summary"]
        self.assertEqual(summary["fixed"],      1)
        self.assertEqual(summary["still_open"], 2)
        self.assertEqual(summary["regressed"],  0)

    def test_open_findings_come_before_fixed_in_output(self):
        before = _report([_finding("SC-001"), _finding("SC-002")])
        after  = _report([_finding("SC-001")])  # SC-002 corrigido
        comp   = compare_reports(before, after)
        states = [f["state"] for f in comp["findings"]]
        # todos os "open" devem vir antes dos "fixed"
        open_indices  = [i for i, s in enumerate(states) if s == "open"]
        fixed_indices = [i for i, s in enumerate(states) if s == "fixed"]
        if open_indices and fixed_indices:
            self.assertLess(max(open_indices), min(fixed_indices))

    def test_no_changes_returns_all_open(self):
        findings = [_finding("SC-001"), _finding("SC-002")]
        before = _report(findings)
        after  = _report(findings)
        comp   = compare_reports(before, after)
        self.assertTrue(all(f["state"] == "open" for f in comp["findings"]))
        self.assertEqual(comp["comparison_summary"]["fixed"], 0)

    def test_all_fixed_returns_empty_open(self):
        before = _report([_finding("SC-001"), _finding("SC-002")])
        after  = _report([])
        comp   = compare_reports(before, after)
        open_findings = [f for f in comp["findings"] if f["state"] == "open"]
        self.assertEqual(len(open_findings), 0)
        self.assertEqual(comp["comparison_summary"]["fixed"], 2)

    def test_comparison_report_has_schema_version(self):
        before = _report([_finding("SC-001")])
        after  = _report([])
        comp   = compare_reports(before, after)
        self.assertIn("schema_version", comp)

    def test_comparison_does_not_mutate_inputs(self):
        """compare_reports não deve alterar os relatórios de entrada."""
        f = _finding("SC-001")
        before = _report([f])
        after  = _report([])
        before_copy = json.loads(json.dumps(before))
        after_copy  = json.loads(json.dumps(after))
        compare_reports(before, after)
        self.assertEqual(before, before_copy)
        self.assertEqual(after,  after_copy)


# ── integração com relatórios reais gerados na sessão 03 ─────────────────────

class TestCompareRealReports(unittest.TestCase):

    def setUp(self):
        root = Path(__file__).parent.parent
        self.before_path = root / "sitecheck-output" / "before" / "report.json"
        self.after_path  = root / "sitecheck-output" / "after"  / "report.json"

    def test_real_reports_exist(self):
        self.assertTrue(self.before_path.exists(), "before/report.json não encontrado")
        self.assertTrue(self.after_path.exists(),  "after/report.json não encontrado")

    def test_real_comparison_has_one_fixed(self):
        before = json.loads(self.before_path.read_text(encoding="utf-8"))
        after  = json.loads(self.after_path.read_text(encoding="utf-8"))
        comp   = compare_reports(before, after)
        self.assertEqual(comp["comparison_summary"]["fixed"], 1)

    def test_real_comparison_sc002_is_fixed(self):
        before = json.loads(self.before_path.read_text(encoding="utf-8"))
        after  = json.loads(self.after_path.read_text(encoding="utf-8"))
        comp   = compare_reports(before, after)
        fixed = [f for f in comp["findings"] if f["state"] == "fixed"]
        self.assertEqual(len(fixed), 1)
        self.assertEqual(fixed[0]["id"], "SC-002")

    def test_real_comparison_sc001_and_sc003_remain_open(self):
        before = json.loads(self.before_path.read_text(encoding="utf-8"))
        after  = json.loads(self.after_path.read_text(encoding="utf-8"))
        comp   = compare_reports(before, after)
        open_ids = {f["id"] for f in comp["findings"] if f["state"] == "open"}
        self.assertIn("SC-001", open_ids)
        self.assertIn("SC-003", open_ids)

    def test_real_comparison_still_open_count(self):
        before = json.loads(self.before_path.read_text(encoding="utf-8"))
        after  = json.loads(self.after_path.read_text(encoding="utf-8"))
        comp   = compare_reports(before, after)
        self.assertEqual(comp["comparison_summary"]["still_open"], 2)


if __name__ == "__main__":
    unittest.main()
