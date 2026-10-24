# Relatorio do Detalhe dos Itens: filepilot-help

**Data:** 2026-10-24
**Modo:** delta focado
**Stack:** Python 3.12 com PySide6 (comandos da tabela do Passo 3 ajustados ao projeto: mypy e pytest do `pyproject.toml`, typecheck `python -m mypy --platform win32 filepilot tests` de 45.7)

## 1. Secao da SPEC

`## 56. Opcao --help na linha de comando [DELTA 2026-10-24, python -m filepilot --help]`, linhas 1558 a 1638 de `.abt/SPEC.md`, com 56.1 a 56.6 (56.2 e errata `{acrescenta: 54.1}`; 56.5 e 56.6 sao pendencias e matriz).

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-help-1 | Opcao --help e -h imprimem o uso e saem sem abrir a janela | 2 | filepilot-version-1 | 1 |

## 3. Ancoras da SPEC por feature

| Feature | Ancora | sha12 | Linhas | Subsecao |
|---|---|---|---|---|
| filepilot-help-1-f1 | 56.3 | d60428c6a57a | 28 | Ponto de entrada com --help e -h |
| filepilot-help-1-f1 | 56.4 | 063c03802e66 | 9 | Testes do ponto de entrada com --help |
| filepilot-help-1-f1 | 56.1 | eeb13e6e66e2 | 12 | Objetivo e fora de escopo |

## 4. Checklist mecanico

1. Um detalhe por item, com linha 1, cabecalho e as quatro secoes: ok (`.abt/items/filepilot-help/filepilot-help-1.md`).
2. `Ordem`, `Pontos` e `Depende de` iguais aos do `itens.md` (1, 2, `filepilot-version-1`): ok.
3. Feature com a linha de ancoras, `Arquivos:`, 4 criterios, `Verificacao:` com typecheck e `Dicas:`: ok.
4. `abt spec check --item-file .abt/items/filepilot-help/filepilot-help-1.md --json`: ok, 3 ancoras conferem, `legacy` false; trechos de 28, 9 e 12 linhas, todos na secao nova.
5. Ids no formato e livres (`abt epic list --ids` e `abt queue list --ids`); dependencia so para item existente (`filepilot-version-1`, pronto), sem ciclo: ok.
6. Marcadores do modelo sobrando (grep do Passo 6 item 6): ok, saida vazia.
7. `§EPIC-` fora de bloco cercado (awk em `.abt/SPEC.md` e `.abt/items/filepilot-help/*.md`): ok, saida vazia.

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-help/filepilot-help-1.md | criado | ok |

## 6. Pendencias e ajustes

- Estrutura `.abt/`: `abt scaffold --check` nesta execucao com `RULES.md`, `WORKFLOW.md` e `SPEC.md` mantidos; nenhuma pendencia `Bloqueante`.
- `.abt/WORKFLOW.md` nao tem secao de comandos: recomendado acrescentar o typecheck (`python -m mypy --platform win32 filepilot tests`) e os testes (`pytest`); a pessoa decide.
- Smoke: o item nao tem servidor nem rota de saude; o `smoke:` e o proprio comando `python -m filepilot --help`, processo real, ate 30 s.
- Nenhum ajuste no `itens.md`; nenhum contrato compartilhado sem resolucao.
- Skill ignorada por nao ser da stack: `vuetify-sneat-ui-patterns` (projeto Python com PySide6).

Retorno: harness
