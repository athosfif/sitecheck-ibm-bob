# Sessão 01 — compreensão e plano

**Modo:** Agent  
**Escopo:** leitura de `README.md` e `docs/`; nenhuma implementação autorizada.  
**Evidência:** [`evidence/bob-session-01-planning.png`](evidence/bob-session-01-planning.png)

## Direção dada ao Bob

O contexto partiu de uma experiência real entre direção de arte, UX e execução de sites: auditorias automáticas costumam produzir listas longas e genéricas, difíceis de explicar para quem cria ou aprova uma página. O pedido foi transformar esse recorte em um fluxo demonstrável, separar decisões humanas de tarefas delegáveis e propor medições sem inventar resultados.

## O que o Bob devolveu

O plano manteve o escopo curto: projeto de demonstração com falhas conhecidas, verificações determinísticas, relatório com evidência, correção escolhida e reverificação. Também propôs registrar tempo do ciclo, intervenções manuais e resultado antes/depois.

## Decisão humana após a leitura

O plano foi aceito com estas escolhas:

- executar tudo localmente, sem serviço pago;
- usar Node.js com o menor número possível de dependências;
- começar por três falhas fáceis de explicar visualmente: imagem sem texto alternativo, campo sem rótulo associado e link interno apontando para destino inexistente;
- limitar a saída a três achados e nunca dizer que o site está perfeito;
- deixar a escolha da correção e a validação final sob revisão humana.

Essa sessão não alterou código. A próxima sessão pode implementar o primeiro fluxo ponta a ponta respeitando essas decisões.
