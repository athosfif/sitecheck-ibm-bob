"""
checkers.py — verificações determinísticas para o demo-site.

Cada função recebe (tree: _HTMLParser, html_path: str) e devolve
list[dict] com zero ou mais achados no formato de schema.make_finding.

As verificações são intencionalmente estreitas: detectam exatamente
os padrões plantados no demo-site. Não prometem cobertura completa.
"""

from html.parser import HTMLParser
from pathlib import Path
from .schema import make_finding


# ── parser auxiliar ──────────────────────────────────────────────────────────

class _Collector(HTMLParser):
    """Coleta tags e atributos em listas simples para inspeção."""

    def __init__(self):
        super().__init__()
        self.tags: list[dict] = []  # {"tag", "attrs": dict, "line": int}

    def handle_starttag(self, tag: str, attrs):
        self.tags.append({
            "tag": tag.lower(),
            "attrs": dict(attrs),
            "line": self.getpos()[0],
        })


def _collect(html_source: str) -> list[dict]:
    c = _Collector()
    c.feed(html_source)
    return c.tags


# ── checker 1: imagem sem texto alternativo ───────────────────────────────────

FINDING_ID_IMG_ALT = "SC-001"


def check_img_alt(html_source: str, html_path: str) -> list[dict]:
    """
    Detecta elementos <img> sem atributo alt ou com alt vazio.

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
            if alt is None:
                src = t["attrs"].get("src", "(sem src)")
                findings.append(make_finding(
                    id=FINDING_ID_IMG_ALT,
                    title="Imagem sem texto alternativo",
                    severity="high",
                    file=html_path,
                    location=f"linha {t['line']} — <img src=\"{src}\">",
                    reproduction=(
                        "Abra o arquivo com um leitor de tela ou valide em "
                        "https://validator.w3.org. O atributo alt está ausente."
                    ),
                    evidence=f"<img src=\"{src}\"> sem atributo alt na linha {t['line']}.",
                    recommendation=(
                        "Adicione alt com uma descrição útil da imagem, "
                        "por exemplo: alt=\"Imagem principal do portfólio\". "
                        "Se a imagem for puramente decorativa, use alt=\"\"."
                    ),
                    state="open",
                ))
    return findings


# ── checker 2: campo de formulário sem rótulo associado ──────────────────────

FINDING_ID_LABEL = "SC-002"


def check_label_for(html_source: str, html_path: str) -> list[dict]:
    """
    Detecta <input> cujo id não é referenciado por nenhum <label for="...">.

    Por que é 'high': sem rótulo programático, leitores de tela lêem apenas
    o placeholder (quando presente), que desaparece ao digitar. Usuários de
    teclado também perdem o alvo de clique ampliado.
    """
    tags = _collect(html_source)
    labeled_ids: set[str] = set()
    inputs: list[dict] = []

    for t in tags:
        if t["tag"] == "label" and t["attrs"].get("for"):
            labeled_ids.add(t["attrs"]["for"])
        if t["tag"] == "input" and t["attrs"].get("type", "text") not in ("hidden", "submit", "button", "reset"):
            inputs.append(t)

    findings = []
    for inp in inputs:
        inp_id = inp["attrs"].get("id", "")
        has_label = inp_id and inp_id in labeled_ids
        has_aria  = "aria-label" in inp["attrs"] or "aria-labelledby" in inp["attrs"]
        if not has_label and not has_aria:
            inp_type = inp["attrs"].get("type", "text")
            findings.append(make_finding(
                id=FINDING_ID_LABEL,
                title="Campo de formulário sem rótulo associado",
                severity="high",
                file=html_path,
                location=f"linha {inp['line']} — <input type=\"{inp_type}\" id=\"{inp_id}\">",
                reproduction=(
                    "Inspecione o campo no DevTools: nenhum <label for> aponta "
                    "para este id. Leitores de tela não anunciam um rótulo descritivo."
                ),
                evidence=(
                    f"<input id=\"{inp_id}\"> na linha {inp['line']} não possui "
                    f"<label for=\"{inp_id}\"> correspondente nem aria-label."
                ),
                recommendation=(
                    f"Adicione <label for=\"{inp_id}\">Endereço de e-mail</label> "
                    "antes do campo, ou use o atributo aria-label diretamente no input."
                ),
                state="open",
            ))
    return findings


# ── checker 3: link interno apontando para destino inexistente ───────────────

FINDING_ID_BROKEN_LINK = "SC-003"


def check_broken_links(html_source: str, html_path: str) -> list[dict]:
    """
    Detecta <a href> que apontam para arquivos locais inexistentes.

    Ignora: âncoras (#), mailto:, tel:, http(s):// e href vazio.
    Por que é 'medium': o site exibe um link que não funciona; o usuário
    recebe um erro 404 ou equivalente local ao clicar.
    """
    base_dir = Path(html_path).parent
    tags = _collect(html_source)
    findings = []

    for t in tags:
        if t["tag"] != "a":
            continue
        href = t["attrs"].get("href", "").strip()
        if not href:
            continue
        # ignora referências externas e especiais
        if href.startswith(("#", "mailto:", "tel:", "http://", "https://")):
            continue
        # remove fragmento interno para verificar apenas o arquivo
        href_path = href.split("#")[0]
        if not href_path:
            continue
        target = base_dir / href_path
        if not target.exists():
            findings.append(make_finding(
                id=FINDING_ID_BROKEN_LINK,
                title="Link interno apontando para destino inexistente",
                severity="medium",
                file=html_path,
                location=f"linha {t['line']} — <a href=\"{href}\">",
                reproduction=(
                    f"Clique no link ou abra {href} a partir do diretório "
                    "do site. O arquivo de destino não existe."
                ),
                evidence=(
                    f"<a href=\"{href}\"> na linha {t['line']}; "
                    f"arquivo esperado em {str(target)} não encontrado."
                ),
                recommendation=(
                    f"Crie o arquivo {href} ou corrija o href para um "
                    "destino que existe."
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
