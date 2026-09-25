# SiteCheck — roteiro de demonstração

**Duração estimada:** 105 a 120 segundos<br>
**Formato:** captura de tela em 16:9, narração em inglês e legendas em inglês.<br>
**Tom:** direto, calmo e autoral. A voz acompanha a demonstração; não parece um comercial.

## Escolha de voz

**Primeira opção: voz do Athos.** Ela reforça autoria e combina com a história real do projeto.
Grave a locução separadamente depois de montar o corte visual; assim é possível refazer uma
frase sem repetir a captura de tela.

**Alternativa: Envato VoiceGen.** Usar uma voz masculina quente, contida e confiante, em
inglês internacional ou americano. Evitar timbre de trailer, entusiasmo artificial e pausas
dramáticas. Velocidade sugerida: `0.94x` a `0.97x`.

## Roteiro em inglês

Hi, I’m Athos. I work where design, communication, and practical AI workflows meet.

For this challenge, I built SiteCheck with IBM Bob: a focused review loop for people who
maintain small websites and need evidence they can actually act on.

This demo has three intentional problems: an image without alternative text, a form field
without a proper label, and a broken internal link. SiteCheck runs deterministic local checks
and turns each problem into a finding with a stable ID, severity, location, evidence, and a
recommendation.

The important part is the recheck. I chose the missing form label first because it directly
affects how a user understands the field, and the correction is small and easy to verify.

After the change, I run the same checks again. The comparison shows one verified fix, two
findings still open by decision, and zero new regressions. The project has forty-two passing
tests.

IBM Bob helped me plan and implement the Python workflow across three documented sessions.
I kept product scope, prioritization, code review, and art direction under human control.
That review mattered: I found and corrected a state-handling issue that could have hidden a
new regression.

SiteCheck is intentionally focused. It does not claim to audit an entire website. It creates
a clear, reproducible loop: find a problem, decide what matters, fix it, and prove the result.

## Plano de tela e tempo

| Tempo | Tela | Ação |
|---:|---|---|
| 00:00–00:08 | Página FIGUEIRA | Mostrar a composição inteira; começar a apresentação. |
| 00:08–00:28 | HTML da demo + relatório anterior | Apontar os três problemas e os IDs. |
| 00:28–00:48 | Relatório anterior | Mostrar localização, evidência e recomendação de um achado. |
| 00:48–01:02 | Trecho do formulário | Destacar o `label` associado ao campo. |
| 01:02–01:24 | Comparativo | Enquadrar os números `2 / 1 / 0` e o SC-002 corrigido. |
| 01:24–01:36 | Terminal | Mostrar `Ran 42 tests` e `OK`; não digitar ao vivo. |
| 01:36–01:50 | Evidências do IBM Bob | Passar pelas três sessões em ritmo rápido. |
| 01:50–02:00 | Comparativo | Voltar ao resultado e encerrar com a última frase. |

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

## Produção e exportação

1. Capturar as telas primeiro, sem voz, em `1920 × 1080`.
2. Esconder favoritos, notificações e abas sem relação com o projeto.
3. Fazer movimentos de cursor lentos; usar cortes secos em vez de acelerar a navegação.
4. Gravar a voz em um ambiente macio, a 15–20 cm do microfone, ou gerar a faixa no VoiceGen.
5. Limpar ruído e nivelar a voz; música é opcional e deve ficar pelo menos 18 dB abaixo dela.
6. Inserir legendas em inglês, duas linhas no máximo, com alto contraste e margens generosas.
7. Exportar em H.264, `1920 × 1080`, 30 fps, áudio AAC 48 kHz. Manter abaixo de cinco
   minutos e 300 MB.

## Direção da locução

- Pausa curta depois de “with IBM Bob”.
- Dar ênfase leve a “evidence”, “same checks”, “one verified fix” e “human control”.
- Ler “42” como “forty-two”, nunca como dígitos separados.
- Não exagerar “AI”, “powerful” ou “revolutionary”; o diferencial é a verificação.
- Encerrar com queda de entonação em “prove the result”.
