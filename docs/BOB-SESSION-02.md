# BOB SESSION 02 — Primeira implementação ponta a ponta

**Data:** 2026-09-25
**Participante:** Athos Figueiredo
**Objetivo da sessão:** construir o primeiro fluxo ponta a ponta do SiteCheck: demo-site com três falhas intencionais, verificadores determinísticos, gerador de relatório JSON e HTML, CLI, testes automatizados.

---

## Decisão de runtime

O plano inicial era Node.js. Durante a sessão, antes de qualquer instalação, verificamos que Node.js não estava disponível no Mac de desenvolvimento e que introduzir um runtime só para o protótipo adicionaria uma dependência sem valor real para a demonstração. Decisão tomada pelo autor: Python 3 com stdlib pura. Nenhuma dependência externa. O `package.json` criado no início da sessão foi removido antes de qualquer commit de código.

Python encontrado: `Python 3.12.3`.

---

## O que foi construído

### Estrutura de arquivos criados

```
demo-site/
  index.html      — página com as três falhas intencionais plantadas
  sobre.html      — página auxiliar (destino válido para link de navegação)
  style.css       — estilos básicos sem dependências externas

src/
  __init__.py
  schema.py       — contrato de um achado e do relatório; validação de campos
  checkers.py     — três verificadores determinísticos (SC-001, SC-002, SC-003)
  reporter.py     — gerador de report.json e report.html autocontido

sitecheck.py      — CLI: lê HTML, roda checkers, escreve saídas, imprime resumo

test/
  test_checkers.py — 26 testes unitários (unittest, stdlib)

sitecheck-output/
  report.json     — saída estruturada da primeira execução sobre o demo-site
  report.html     — relatório legível em navegador
```

### As três falhas do demo-site

Plantadas intencionalmente em `demo-site/index.html`; nenhuma foi corrigida nesta sessão para preservar o estado inicial da demonstração antes/depois.

| ID     | Falha                                        | Severidade | Linha |
|--------|----------------------------------------------|------------|-------|
| SC-001 | `<img src="hero.jpg">` sem atributo `alt`    | Alta       | 24    |
| SC-002 | `<input id="email-input">` sem `<label for>` | Alta       | 32    |
| SC-003 | `<a href="contato.html">` — arquivo inexistente | Média   | 17    |

---

## Resultados dos testes

```
Ran 26 tests in 0.020s
OK
```

Cobertura dos testes:

- SC-001: imagem sem alt detectada; imagem com alt válido passa; `alt=""` decorativo passa; sem imagens devolve lista vazia; campos obrigatórios do achado verificados; demo-site dispara o checker.
- SC-002: campo sem label detectado; label correto passa; aria-label passa; aria-labelledby passa; input hidden e submit ignorados; demo-site dispara o checker.
- SC-003: link para arquivo inexistente detectado; link para arquivo existente passa; âncoras ignoradas; links externos ignorados; mailto ignorado; demo-site dispara o checker.
- `run_all`: demo-site produz exatamente 3 achados; IDs são únicos; mesma entrada produz mesma saída (determinismo); HTML sem falhas devolve lista vazia.
- `schema`: severidade inválida lança `ValueError`; estado inválido lança `ValueError`.

---

## Execução ponta a ponta — saída real

```
SiteCheck — demo-site/index.html
────────────────────────────────────────────────────

[SC-001] Imagem sem texto alternativo
  Severidade : Alta
  Estado     : Aberto
  Local      : linha 24 — <img src="hero.jpg">
  Evidência  : <img src="hero.jpg"> sem atributo alt na linha 24.
  Correção   : Adicione alt com descrição do conteúdo da imagem, por exemplo:
               alt="Portfólio do Estúdio Folha". Se a imagem for puramente
               decorativa, use alt="".

[SC-002] Campo de formulário sem rótulo associado
  Severidade : Alta
  Estado     : Aberto
  Local      : linha 32 — <input type="email" id="email-input">
  Evidência  : <input id="email-input"> na linha 32 não possui
               <label for="email-input"> correspondente nem aria-label.
  Correção   : Adicione <label for="email-input">Endereço de e-mail</label>
               antes do campo, ou use aria-label diretamente no input.

[SC-003] Link interno apontando para destino inexistente
  Severidade : Média
  Estado     : Aberto
  Local      : linha 17 — <a href="contato.html">
  Evidência  : <a href="contato.html"> na linha 17; arquivo esperado em
               demo-site/contato.html não encontrado.
  Correção   : Crie o arquivo contato.html ou corrija o href para um
               destino que existe.

────────────────────────────────────────────────────
3 achados encontrados.
```

Saída validada com uma fixture temporária sem as três falhas:

```
Nenhuma falha encontrada pelos testes executados.
Isso não equivale a uma declaração de que o site está livre de problemas.
```

Exit code: `1` quando há achados, `0` quando não há — útil em pipelines CI.

---

## Uso do IBM Bob nesta sessão

- Leu e cruzou `KICKOFF-BRIEF.md` e `SITECHECK-SPEC.md` antes de escrever qualquer arquivo.
- Tomou a decisão de estrutura de módulos (schema / checkers / reporter / CLI) com base no contrato de achado da spec.
- Escreveu todos os arquivos de código, testes e documentação.
- Identificou e corrigiu o bug de 4 achados (→ 3) antes de fechar: `sobre.html` ausente disparava SC-003 duas vezes; criação do arquivo resolveu sem alterar nenhum checker.
- Propôs e aguardou confirmação humana sobre o que vai para `.gitignore` (o autor decidiu manter `sitecheck-output/` rastreado como evidência de demonstração).

## Revisão humana após a sessão

Athos revisou o resultado fora do Bob antes do commit. A revisão:

- manteve os relatórios JSON e HTML no repositório como evidência da demonstração;
- corrigiu a data e o nome do participante neste registro;
- rejeitou `sobre.html` como prova de página limpa, porque ela ainda preserva o link quebrado do menu;
- corrigiu o falso positivo que tratava `alt=""` como ausência de texto alternativo;
- aproximou o conteúdo do demo-site do trabalho real da FIGUEIRA, sem transformar o exemplo em uma peça promocional.

Os 26 testes e as duas validações manuais foram executados novamente depois dessas mudanças.

Captura da sessão: `docs/evidence/bob-session-02-implementation.png`.

---

## Limitações honestas desta sessão

**O que os checkers não fazem:**

- SC-001 verifica apenas a presença do atributo. `alt=""` é aceito como escolha decorativa, mas a ferramenta não julga se essa escolha editorial foi adequada.
- SC-002 não detecta labels implícitas (`<label><input></label>` sem `for`). Não lida com `title` como substituto de label.
- SC-003 só verifica existência do arquivo no sistema de arquivos local. Não segue redirecionamentos, não verifica fragmentos (`#secao`) dentro do arquivo de destino, não verifica `href` com query string.
- Nenhum checker lida com HTML malformado além do que `html.parser` tolera nativamente.

**O que o fluxo antes/depois ainda não tem:**

- O estado `fixed` e `recheck_result` existem no schema e no HTML, mas o ciclo de reverificação (aplicar correção → rodar novamente → comparar) não foi implementado. Está planejado para a próxima sessão.

**Escopo:**

- Os verificadores são intencionalmente estreitos: detectam exatamente os padrões plantados. Não é uma auditoria de acessibilidade completa nem uma promessa de cobertura.
