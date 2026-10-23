# Relatorio do Detalhe dos Itens: filepilot-version

**Data:** 2026-10-23
**Modo:** so SPEC + itens
**Stack:** Python 3.12 com PySide6 (comandos de 19.2 com 45.7 da SPEC e da tabela por stack: mypy da stack do projeto, pytest)

## 1. Secao da SPEC

`## 54. Opcao --version na linha de comando [DELTA 2026-10-23, python -m filepilot --version]`, linhas 1490 a 1552 de `.abt/SPEC.md`: 54.1 (L1492-1504), 54.2 (L1506-1531), 54.3 Pendencias para decisao e 54.4 Traceability Matrix.

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-version-1 | Opcao --version imprime a versao e sai sem abrir a janela | 1 | - | 1 |

## 3. Ancoras da SPEC por feature

| Feature | Ancora | sha12 | Linhas | Subsecao |
|---|---|---|---|---|
| filepilot-version-1-f1 | 54.2 | eba99aa67823 | 26 | Ponto de entrada com --version |
| filepilot-version-1-f1 | 54.1 | 08ed0d63bb9d | 13 | Objetivo e fora de escopo |

## 4. Checklist mecanico

| Conferencia | Resultado |
|---|---|
| 1. Um detalhe por item, linha 1, cabecalho e as quatro secoes | ok |
| 2. Ordem, Pontos e Depende de iguais ao `itens.md`; pontos de 1 a 8 | ok (1, 1, -) |
| 3. Feature com linha de ancoras, Arquivos, 4 criterios, Verificacao com typecheck e Dicas | ok |
| 4. `abt spec check --item-file .abt/items/filepilot-version/filepilot-version-1.md` | ok: 2 ancoras conferem, `legacy` false, trechos de 26 e 13 linhas, so subsecoes de conteudo da secao 54 |
| 5. Ids no formato e livres (`abt epic list --ids`: 6 epicos; `abt queue list --ids`: 31 itens, nenhum `filepilot-version`); sem ciclo | ok |
| 6. Marcadores do modelo sobrando (grep) | ok: saida vazia (exit 1) |
| 7. Placeholder provisorio de secao fora de bloco cercado (awk) | ok: saida vazia |

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| `.abt/items/filepilot-version/filepilot-version-1.md` | criado | ok |

## 6. Pendencias e ajustes

- Nenhuma pendencia `Bloqueante`: `abt scaffold --check` com `.abt/RULES.md`, `.abt/WORKFLOW.md` e `.abt/SPEC.md` mantidos.
- Nenhum contrato compartilhado: o item toca so `filepilot/__main__.py` e um arquivo de teste novo.
- Smoke: comando de linha de comando (`python -m filepilot --version`), sem servidor, porta nem rota de saude.
- Recomendacao: `.abt/WORKFLOW.md` nao tem secao de comandos; a pessoa pode acrescentar `python -m mypy --platform win32 filepilot tests` e `pytest` (Hugo nao escreve nele).
- Nenhum ajuste no `itens.md`.
- Skill `vuetify-sneat-ui-patterns` (apoio da `product-spec-delta-mode`) nao lida: o projeto usa PySide6, sem Vuetify.

Retorno: harness
