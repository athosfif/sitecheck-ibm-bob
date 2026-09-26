"""
checkers.py — verificações determinísticas para o demo-site.

Cada função recebe (tree: _HTMLParser, html_path: str) e devolve
list[dict] com zero ou mais achados no formato de schema.make_finding.

As verificacoes cobrem tres familias de padroes estaticos.
Nao prometem cobertura completa de acessibilidade ou links da web.
"""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import hashlib
import json
from .schema import make_finding


# ── parser auxiliar ──────────────────────────────────────────────────────────

class _Collector(HTMLParser):
    """Collect structural label context without executing HTML or fetching resources."""
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.tags = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        node = {"tag": tag.lower(), "attrs": dict(attrs), "line": self.getpos()[0], "text": "", "labels": [n for n in self.stack if n["tag"] == "label"]}
        if tag == "img" and node["attrs"].get("alt"):
            self.handle_data(node["attrs"]["alt"])
        self.tags.append(node)
        if tag not in self.VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if any(n["tag"] in ("script", "style") or "hidden" in n["attrs"] or n["attrs"].get("aria-hidden") == "true" for n in self.stack):
            return
        for node in self.stack:
            node["text"] += data


def _collect(html_source):
    c = _Collector()
    c.feed(html_source)
    c.close()
    return c.tags


def _fingerprint(rule, identity):
    return rule + ":" + hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:20]


# ── checker 1: imagem sem texto alternativo ───────────────────────────────────

FINDING_ID_IMG_ALT = "SC-001"


def check_img_alt(html_source: str, html_path: str) -> list[dict]:
    """
    Detecta elementos <img> sem atributo alt; alt vazio e aceito para imagens decorativas.

    Por que é 'high': leitores de tela anunciam o nome do arquivo como
    substituto, tornando o conteúdo incompreensível para usuários que
    dependem de tecnologia assistiva.
    """
    findings = []
    tags = _collect(html_source)
    for t in tags:
        if t["tag"] == "img":
            alt = t["attrs"].get("alt")
            # alt="" e valido para imagens decorativas. A ausencia do
            # atributo e o caso objetivo que este checker consegue provar.
            if "alt" not in t["attrs"]:
                src = t["attrs"].get("src", "(missing src)")
                findings.append(make_finding(
                    id=FINDING_ID_IMG_ALT,
                    fingerprint=_fingerprint(FINDING_ID_IMG_ALT, {"id": t["attrs"].get("id"), "src": src}),
                    title="Image missing alternative text",
                    severity="high",
                    file=html_path,
                    location=f"line {t['line']} — <img src=\"{src}\">",
                    reproduction=(
                        "Open the file with a screen reader or validate it at "
                        "https://validator.w3.org. The alt attribute is missing."
                    ),
                    evidence=f"<img src=\"{src}\"> has no alt attribute on line {t['line']}.",
                    recommendation=(
                        "Add an alt attribute with a useful image description, "
                        "for example: alt=\"Main portfolio image\". "
                        "If the image is purely decorative, use alt=\"\"."
                    ),
                    state="open",
                ))
    return findings


# ── checker 2: campo de formulário sem rótulo associado ──────────────────────

FINDING_ID_LABEL = "SC-002"


def check_label_for(html_source: str, html_path: str) -> list[dict]:
    """
    Detecta input, select e textarea sem nome nas associacoes estaticas suportadas.

    Por que é 'high': sem rótulo programático, leitores de tela lêem apenas
    o placeholder (quando presente), que desaparece ao digitar. Usuários de
    teclado também perdem o alvo de clique ampliado.
    """
    tags = _collect(html_source)
    labeled_ids = {t["attrs"]["for"] for t in tags if t["tag"] == "label" and t["attrs"].get("for") and t["text"].strip()}
    names = {t["attrs"]["id"]: t["text"].strip() for t in tags if t["attrs"].get("id")}
    inputs = [t for t in tags if t["tag"] in ("input", "select", "textarea") and not (t["tag"] == "input" and (t["attrs"].get("type") or "text").lower() in ("hidden", "submit", "button", "reset"))]

    findings = []
    for inp in inputs:
        inp_id = inp["attrs"].get("id", "")
        has_label = (inp_id and inp_id in labeled_ids) or any(label["text"].strip() and (not label["attrs"].get("for") or label["attrs"].get("for") == inp_id) for label in inp["labels"])
        has_aria = bool((inp["attrs"].get("aria-label") or "").strip()) or any(names.get(ref) for ref in (inp["attrs"].get("aria-labelledby") or "").split())
        fallback = bool((inp["attrs"].get("title") or "").strip()) or ((inp["attrs"].get("type") or "").lower() == "image" and bool((inp["attrs"].get("alt") or "").strip()))
        if not has_label and not has_aria and not fallback:
            inp_type = inp["attrs"].get("type", "text")
            findings.append(make_finding(
                id=FINDING_ID_LABEL,
                fingerprint=_fingerprint(FINDING_ID_LABEL, {"tag": inp["tag"], "id": inp_id, "name": inp["attrs"].get("name"), "type": inp_type}),
                title="Form field missing an associated label",
                severity="high",
                file=html_path,
                location=f"line {inp['line']} — <{inp['tag']} type=\"{inp_type}\" id=\"{inp_id}\">",
                reproduction=(
                    "Inspect the field in DevTools: no <label for> targets "
                    "this id. Screen readers do not announce a descriptive label."
                ),
                evidence=(
                    f"<{inp['tag']} id=\"{inp_id}\"> on line {inp['line']} has no matching "
                    f"<label for=\"{inp_id}\"> and no aria-label."
                ),
                recommendation=(
                    ("Associate a descriptive label using the existing id, " if inp_id else "Give the field a unique id and associate a descriptive label, ")
                    + "or use a nonempty accessible name. Choose wording that describes this field."
                ),
                state="open",
            ))
    return findings


# ── checker 3: link interno apontando para destino inexistente ───────────────

FINDING_ID_BROKEN_LINK = "SC-003"


def check_broken_links(html_source: str, html_path: str) -> list[dict]:
    """
    Detecta <a href> que apontam para arquivos locais inexistentes.

    Ignora esquemas externos, URLs //host, ancoras e caminhos absolutos ao site.
    Nao conhece a raiz de publicacao nem regras de rotas de um servidor.
    Por que é 'medium': o site exibe um link que não funciona; o usuário
    recebe um erro 404 ou equivalente local ao clicar.
    """
    base_dir = Path(html_path).parent
    tags = _collect(html_source)
    findings = []
    if any(t["tag"] == "base" and t["attrs"].get("href") for t in tags):
        return findings  # Base URLs require web-root/server context, outside this static check.

    for t in tags:
        if t["tag"] != "a":
            continue
        href = (t["attrs"].get("href") or "").strip()
        if not href:
            continue
        # URL syntax is case-insensitive for schemes. Queries/fragments do not name files.
        try:
            parsed = urlsplit(href)
        except ValueError:
            continue
        if parsed.scheme or parsed.netloc or href.startswith("#"):
            continue
        href_path = unquote(parsed.path)
        if not href_path:
            continue
        # A single-file invocation has no web-root mapping. Root-relative URLs
        # are intentionally out of scope rather than compared with the OS root.
        if href_path.startswith("/"):
            continue
        target = base_dir / href_path
        if not target.exists():
            findings.append(make_finding(
                id=FINDING_ID_BROKEN_LINK,
                fingerprint=_fingerprint(FINDING_ID_BROKEN_LINK, {"href": href}),
                title="Internal link points to a missing destination",
                severity="medium",
                file=html_path,
                location=f"line {t['line']} — <a href=\"{href}\">",
                reproduction=(
                    f"Follow the link or open {href} from the site directory. "
                    "The destination file does not exist."
                ),
                evidence=(
                    f"<a href=\"{href}\"> on line {t['line']}; "
                    f"the expected file at {str(target)} was not found."
                ),
                recommendation=(
                    f"Create {href} or update the href to point to an "
                    "existing destination."
                ),
                state="open",
            ))
    return findings


# ── execução de todos os checkers ─────────────────────────────────────────────

ALL_CHECKERS = [check_img_alt, check_label_for, check_broken_links]


def run_all(html_source: str, html_path: str) -> list[dict]:
    """Executa todos os checkers e devolve a lista combinada de achados."""
    results = []
    for checker in ALL_CHECKERS:
        results.extend(checker(html_source, html_path))
    return results
