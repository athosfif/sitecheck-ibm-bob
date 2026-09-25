"""
test_checkers.py — testes dos três checkers com casos positivos e negativos.

Execução:
    python -m pytest test/test_checkers.py   (se pytest instalado)
    python -m unittest test.test_checkers    (stdlib)
    python -m unittest discover test         (todos os testes)
"""

import sys
import unittest
from pathlib import Path

# permite execução a partir da raiz do projeto
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.checkers import (
    check_img_alt,
    check_label_for,
    check_broken_links,
    run_all,
    FINDING_ID_IMG_ALT,
    FINDING_ID_LABEL,
    FINDING_ID_BROKEN_LINK,
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _html(body: str) -> str:
    return f'<!DOCTYPE html><html><head></head><body>{body}</body></html>'


DUMMY_PATH = "/tmp/test.html"


# ── SC-001: imagem sem alt ─────────────────────────────────────────────────────

class TestImgAlt(unittest.TestCase):

    def test_img_without_alt_is_found(self):
        src = _html('<img src="photo.jpg">')
        result = check_img_alt(src, DUMMY_PATH)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], FINDING_ID_IMG_ALT)
        self.assertEqual(result[0]["state"], "open")
        self.assertEqual(result[0]["severity"], "high")

    def test_img_with_empty_alt_is_valid_for_decorative_image(self):
        src = _html('<img src="photo.jpg" alt="">')
        result = check_img_alt(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_img_with_valid_alt_is_clean(self):
        src = _html('<img src="photo.jpg" alt="Portfólio do estúdio">')
        result = check_img_alt(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_img_with_whitespace_alt_is_not_missing(self):
        # A ferramenta verifica presença, não julga a qualidade editorial.
        src = _html('<img src="bg.jpg" alt="  ">')
        result = check_img_alt(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_no_images_returns_empty(self):
        src = _html('<p>Sem imagens.</p>')
        result = check_img_alt(src, DUMMY_PATH)
        self.assertEqual(result, [])

    def test_finding_contains_required_fields(self):
        src = _html('<img src="x.png">')
        f = check_img_alt(src, DUMMY_PATH)[0]
        for field in ("id", "title", "severity", "file", "location",
                      "reproduction", "evidence", "recommendation", "state"):
            self.assertIn(field, f, msg=f"campo ausente: {field}")

    def test_demo_site_has_flaw(self):
        """O demo-site real deve disparar SC-001."""
        demo = Path(__file__).parent.parent / "demo-site" / "index.html"
        src = demo.read_text(encoding="utf-8")
        result = check_img_alt(src, str(demo))
        self.assertGreater(len(result), 0, "demo-site deveria ter SC-001")


# ── SC-002: campo sem rótulo ──────────────────────────────────────────────────

class TestLabelFor(unittest.TestCase):

    def test_input_without_label_is_found(self):
        src = _html('<input type="email" id="em">')
        result = check_label_for(src, DUMMY_PATH)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], FINDING_ID_LABEL)

    def test_input_with_label_is_clean(self):
        src = _html('<label for="em">E-mail</label><input type="email" id="em">')
        result = check_label_for(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_input_with_aria_label_is_clean(self):
        src = _html('<input type="text" id="nm" aria-label="Nome">')
        result = check_label_for(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_input_with_aria_labelledby_is_clean(self):
        src = _html('<span id="lbl">Nome</span><input type="text" aria-labelledby="lbl">')
        result = check_label_for(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_hidden_input_ignored(self):
        src = _html('<input type="hidden" name="csrf">')
        result = check_label_for(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_submit_button_ignored(self):
        src = _html('<input type="submit" value="Enviar">')
        result = check_label_for(src, DUMMY_PATH)
        self.assertEqual(len(result), 0)

    def test_demo_site_sc002_fixed(self):
        """SC-002 foi corrigido na sessão 03: demo-site não deve mais disparar este checker."""
        demo = Path(__file__).parent.parent / "demo-site" / "index.html"
        src = demo.read_text(encoding="utf-8")
        result = check_label_for(src, str(demo))
        self.assertEqual(len(result), 0, "SC-002 foi corrigido — checker não deve disparar")


# ── SC-003: link quebrado ─────────────────────────────────────────────────────

class TestBrokenLinks(unittest.TestCase):

    def test_link_to_missing_file_is_found(self, tmp_path=None):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            html_path = os.path.join(d, "index.html")
            src = _html('<a href="contato.html">Contato</a>')
            Path(html_path).write_text(src, encoding="utf-8")
            result = check_broken_links(src, html_path)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], FINDING_ID_BROKEN_LINK)
        self.assertEqual(result[0]["severity"], "medium")

    def test_link_to_existing_file_is_clean(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            html_path = os.path.join(d, "index.html")
            target    = os.path.join(d, "sobre.html")
            Path(html_path).write_text("", encoding="utf-8")
            Path(target).write_text("", encoding="utf-8")
            src = _html('<a href="sobre.html">Sobre</a>')
            result = check_broken_links(src, html_path)
        self.assertEqual(len(result), 0)

    def test_anchor_link_ignored(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            html_path = os.path.join(d, "index.html")
            src = _html('<a href="#secao">Seção</a>')
            Path(html_path).write_text(src, encoding="utf-8")
            result = check_broken_links(src, html_path)
        self.assertEqual(len(result), 0)

    def test_external_link_ignored(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            html_path = os.path.join(d, "index.html")
            src = _html('<a href="https://example.com">Site</a>')
            Path(html_path).write_text(src, encoding="utf-8")
            result = check_broken_links(src, html_path)
        self.assertEqual(len(result), 0)

    def test_mailto_ignored(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            html_path = os.path.join(d, "index.html")
            src = _html('<a href="mailto:a@b.com">E-mail</a>')
            Path(html_path).write_text(src, encoding="utf-8")
            result = check_broken_links(src, html_path)
        self.assertEqual(len(result), 0)

    def test_demo_site_has_flaw(self):
        """O demo-site real deve disparar SC-003 (contato.html inexistente)."""
        demo = Path(__file__).parent.parent / "demo-site" / "index.html"
        src = demo.read_text(encoding="utf-8")
        result = check_broken_links(src, str(demo))
        self.assertGreater(len(result), 0, "demo-site deveria ter SC-003")


# ── run_all ───────────────────────────────────────────────────────────────────

class TestRunAll(unittest.TestCase):

    def test_demo_site_produces_exactly_two_findings_after_sc002_fix(self):
        """Após a correção do SC-002 na sessão 03, o demo-site tem dois achados abertos."""
        demo = Path(__file__).parent.parent / "demo-site" / "index.html"
        src = demo.read_text(encoding="utf-8")
        result = run_all(src, str(demo))
        self.assertEqual(len(result), 2, f"esperado 2 achados, obtido {len(result)}")

    def test_demo_site_findings_have_distinct_ids(self):
        demo = Path(__file__).parent.parent / "demo-site" / "index.html"
        src = demo.read_text(encoding="utf-8")
        result = run_all(src, str(demo))
        ids = [f["id"] for f in result]
        self.assertEqual(len(ids), len(set(ids)), "IDs dos achados devem ser únicos")

    def test_same_input_same_output(self):
        """Determinismo: mesma entrada produz o mesmo relatório."""
        demo = Path(__file__).parent.parent / "demo-site" / "index.html"
        src = demo.read_text(encoding="utf-8")
        r1 = run_all(src, str(demo))
        r2 = run_all(src, str(demo))
        self.assertEqual(r1, r2)

    def test_clean_html_returns_empty(self):
        import tempfile, os
        with tempfile.TemporaryDirectory() as d:
            html_path = os.path.join(d, "clean.html")
            # HTML sem nenhuma das três falhas
            src = _html(
                '<img src="x.jpg" alt="Descrição">'
                '<label for="e">E-mail</label><input type="email" id="e">'
            )
            Path(html_path).write_text(src, encoding="utf-8")
            result = run_all(src, html_path)
        self.assertEqual(result, [])


# ── schema ────────────────────────────────────────────────────────────────────

class TestSchema(unittest.TestCase):

    def test_invalid_severity_raises(self):
        from src.schema import make_finding
        with self.assertRaises(ValueError):
            make_finding(
                id="X", title="X", severity="critical",
                file="f", location="l", reproduction="r",
                evidence="e", recommendation="c",
            )

    def test_invalid_state_raises(self):
        from src.schema import make_finding
        with self.assertRaises(ValueError):
            make_finding(
                id="X", title="X", severity="high",
                file="f", location="l", reproduction="r",
                evidence="e", recommendation="c",
                state="pending",
            )


if __name__ == "__main__":
    unittest.main()
