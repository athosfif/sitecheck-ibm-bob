# SiteCheck

SiteCheck ajuda designers, desenvolvedores independentes e pequenos times a transformar problemas verificáveis de um site em uma lista curta de correções que pode ser compreendida, aplicada e testada novamente.

## Princípio

Poucos achados, boa evidência e uma correção comprovada valem mais do que uma auditoria extensa e genérica.

## Requisitos

Python 3.8 ou superior. Sem dependências externas — apenas a biblioteca padrão.

## Uso

```sh
# verificar o demo-site incluído no repositório
python3 sitecheck.py demo-site/index.html

# especificar diretório de saída
python3 sitecheck.py demo-site/index.html --out-dir meu-relatorio
```

O comando escreve dois arquivos no diretório de saída (padrão: `sitecheck-output/`):

- `report.json` — achados em formato estruturado
- `report.html` — relatório legível em navegador

Exit code `1` quando há achados, `0` quando não há.

## Testes

```sh
python3 -m unittest discover test
```

26 testes unitários cobrindo os três checkers, o schema e o comportamento de relatório vazio.

## Demo

O diretório `demo-site/` contém uma página com três falhas intencionais:

| ID     | Falha                                           | Severidade |
|--------|-------------------------------------------------|------------|
| SC-001 | Imagem sem texto alternativo                    | Alta       |
| SC-002 | Campo de formulário sem rótulo associado        | Alta       |
| SC-003 | Link interno apontando para destino inexistente | Média      |

As falhas estão preservadas para demonstrar o fluxo antes/depois na próxima sessão.

O diretório `sitecheck-output/` contém a saída da primeira execução sobre o demo-site — JSON e HTML — como evidência do estado inicial.

## Estrutura

```
src/
  schema.py       contrato de um achado e do relatório
  checkers.py     três verificadores determinísticos
  reporter.py     gerador de report.json e report.html
sitecheck.py      CLI
demo-site/        site de demonstração com falhas intencionais
sitecheck-output/ saída da primeira execução (evidência)
test/             testes unitários (unittest, stdlib)
docs/             especificação, brief e registros de sessão
```

## Escopo

Sem login, sem serviços externos, sem telemetria, sem dados de cliente.
Os verificadores detectam padrões específicos — não prometem cobertura completa de acessibilidade nem de qualidade.

## Estado

Sessão 02 concluída: fluxo ponta a ponta funcionando, 26 testes passando.
Próxima sessão: ciclo de reverificação (aplicar correção → rodar novamente → comparar antes/depois).
