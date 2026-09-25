# SiteCheck — direção de arte

## Ideia central

**Evidência com linguagem editorial.**

SiteCheck trata um relatório técnico como uma peça que precisa ser lida, entendida e usada
para decidir. A interface evita a estética genérica de dashboard: o enquadramento escuro,
o papel quente e a escala tipográfica aproximam o artefato de um caderno de revisão.

## Sistema visual

| Papel | Valor | Uso |
|---|---:|---|
| Ink | `#11130f` | texto, estrutura e contraste |
| Paper | `#f2eee4` | campo principal de leitura |
| Acid | `#d8ff55` | confirmação e decisão validada |
| Cobalt | `#5b63ff` | assinatura visual e identidade |
| Coral | `#ff735f` | regressão e atenção |

### Tipografia

- **Display:** Iowan Old Style, Baskerville ou Georgia. Títulos grandes, entrelinha curta e
  contraste editorial.
- **Interface:** Avenir Next, Avenir, Helvetica Neue ou Arial. Navegação, campos e textos de
  apoio com leitura direta.
- **Dados:** SFMono Regular ou Consolas. IDs, caminhos e informações verificáveis.

As fontes são pilhas do sistema. Isso mantém a demonstração autocontida, funciona offline e
evita que uma falha de rede mude a apresentação no momento do pitch.

## Composição

- Escala grande nos títulos para dar uma entrada clara à leitura.
- Linhas finas e áreas de respiro em vez de sombras decorativas.
- Cor ligada a estado: acid para correção, coral para regressão, cobalt para identidade.
- Cards mantêm evidência, reprodução e recomendação no mesmo plano visual.
- A arte `demo-site/hero-art.svg` foi desenhada para o projeto com formas geométricas,
  contraste alto e a assinatura `FIGUEIRA / 26`.

## Voz

Clara, sóbria e específica. O texto evita promessas de auditoria total e mantém visível o
limite real: SiteCheck verifica três padrões determinísticos e mostra o que mudou. A decisão
de corrigir primeiro o formulário foi humana; os demais achados continuam rastreáveis.

## Autoria e uso do IBM Bob

IBM Bob foi usado como parceiro de implementação nas sessões documentadas. Athos definiu o
problema, o recorte do produto, a prioridade da correção, a revisão crítica e a direção de
arte. Após a geração do fluxo de comparação, a revisão humana encontrou e corrigiu um caso
em que uma regressão poderia ficar visualmente escondida.

Essa divisão é parte da proposta: IA acelera execução, enquanto intenção, critério e aceite
continuam humanos.

## Evidências

- `docs/evidence/sitecheck-demo-designed.png`
- `docs/evidence/sitecheck-comparison-designed.png`
- `docs/evidence/bob-session-01-planning.png`
- `docs/evidence/bob-session-02-implementation.png`
- `docs/evidence/bob-session-03-recheck.png`
