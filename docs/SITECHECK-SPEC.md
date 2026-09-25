# SiteCheck — especificação pré-kickoff

Estado: conceito preparado; implementação competitiva ainda não iniciada.

## Proposta

SiteCheck ajuda uma pessoa responsável por um pequeno site a transformar falhas verificáveis em uma lista curta de correções priorizadas. O valor está na rastreabilidade: cada achado mostra o que falhou, como reproduzir, qual evidência sustenta a conclusão e como validar a correção.

## Usuário e necessidade

**Usuário:** designer, desenvolvedor independente ou pequeno time responsável por uma página web.

**Necessidade:** descobrir rapidamente problemas observáveis que prejudicam uso, clareza ou qualidade técnica, sem receber uma auditoria extensa ou afirmações genéricas.

## Fluxo mínimo

1. Abrir um projeto próprio com falhas intencionais conhecidas.
2. Executar verificações determinísticas locais.
3. Exibir até três achados com severidade, evidência e reprodução.
4. Escolher um achado.
5. Usar IBM Bob para planejar e aplicar a correção.
6. Executar as mesmas verificações e mostrar o antes/depois.

## Contrato de um achado

- identificador estável;
- título claro;
- severidade justificada;
- arquivo e localização;
- passos de reprodução;
- evidência observada;
- correção recomendada;
- estado `open`, `fixed` ou `regressed`;
- resultado da verificação posterior.

## Critérios de aceitação

- Os três achados correspondem a falhas colocadas deliberadamente no projeto de demonstração.
- A mesma entrada produz o mesmo relatório.
- Pelo menos uma correção muda um teste de falha para aprovação.
- A interface diferencia `não verificado`, `falhou` e `passou`.
- Um relatório vazio explica que nenhuma falha foi encontrada pelos testes executados, sem declarar que o site está perfeito.
- A demonstração funciona localmente sem serviço pago.

## Fora do escopo

Login, pagamentos, análise de sites de terceiros, crawling amplo, promessa de acessibilidade ou segurança completas, correções automáticas sem revisão e qualquer dado real de cliente.

## Porta de aderência

Após o kickoff, comparar esta proposta com a track e a rubrica oficiais. Implementar somente se houver aderência clara e uso real do IBM Bob puder ser demonstrado.
