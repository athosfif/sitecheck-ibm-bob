# SiteCheck — roteiro de demonstração

**Duração estimada:** 90 a 120 segundos  
**Tom:** direto, calmo e autoral. Mostrar a tela enquanto fala; não decorar palavra por palavra.

## Roteiro em inglês

Hi, I’m Athos. I work at the intersection of design, communication and practical AI
workflows.

For this challenge, I built SiteCheck with IBM Bob. It is a small review loop for people who
maintain a website and need evidence they can actually act on.

This demo page has three intentional problems: an image without alternative text, a form
field without a proper label, and a broken internal link. SiteCheck runs deterministic local
checks and turns each problem into a finding with a stable ID, severity, location, evidence
and a recommendation.

The important part is the recheck. I chose the missing form label as the first fix because it
directly affects how a user understands the field, and the correction is small and easy to
verify.

After the change, I run the same checks again. The comparison shows one verified fix, two
findings still open by decision, and zero new regressions. The project currently has 42
passing tests.

IBM Bob helped me plan and implement the Python workflow across three documented sessions.
I kept the product scope, prioritization, code review and art direction under human control.
That review mattered: I found and corrected a state-handling issue that could have hidden a
new regression.

SiteCheck is intentionally modest. It does not claim to audit an entire website. It creates a
clear, reproducible loop: find a problem, decide what matters, fix it, and prove the result.

## Apoio em português

- Abrir pela página FIGUEIRA para estabelecer autoria visual.
- Mostrar rapidamente os três problemas plantados.
- Rodar ou mostrar o relatório anterior com três achados.
- Exibir o label corrigido no HTML.
- Abrir a comparação e apontar os números `2 / 1 / 0`.
- Mostrar `Ran 42 tests — OK`.
- Encerrar no relatório, não no terminal.

## Capturas sugeridas

1. `demo-site/index.html` — 6 s
2. `sitecheck-output/before/report.html` — 15 s
3. diff ou trecho do label — 10 s
4. `sitecheck-output/comparison/comparison.html` — 25 s
5. terminal com os 42 testes — 8 s
6. telas das sessões do IBM Bob — 12 s
7. retorno ao comparativo para a frase final — 8 s
