# Relatorio do Detalhe dos Itens: zz-74e

**Data:** 2026-10-26
**Modo:** so SPEC + itens
**Stack:** Python (comandos da tabela do Passo 3, ajustados ao gate ja usado no projeto: `python -m mypy --platform win32 filepilot tests` de `.github/workflows/tests.yml:22`)

## 1. Secao da SPEC

`## 60. Arquivo de prova do smoke 74e [DELTA 2026-10-26, rascunho/74e-prova.md]`, linhas 1746 a 1784 de `.abt/SPEC.md`: 60.1 (linhas 1748-1758), 60.2 (1760-1766), 60.3 Pendencias para decisao e 60.4 Traceability Matrix (nao citadas).

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|-------|---------|--------|--------|------------|----------|
| 1 | zz-74e-descartavel | Arquivo de prova rascunho/74e-prova.md do smoke 74e | 1 | - | 1 |

## 3. Ancoras da SPEC por feature

| Feature | Ancora | sha12 | Linhas | Subsecao |
|---------|--------|-------|--------|----------|
| zz-74e-descartavel-f1 | 60.2 | ca4d3b5c2b6b | 7 | Arquivo rascunho/74e-prova.md |
| zz-74e-descartavel-f1 | 60.1 | d05810934e3e | 11 | Objetivo e fora de escopo |

## 4. Checklist mecanico

1. Um detalhe por item, em `.abt/items/zz-74e/zz-74e-descartavel.md`, com linha 1, cabecalho e as quatro secoes: ok.
2. `Ordem` 1, `Pontos` 1 e `Depende de` `-`, iguais ao `itens.md`: ok.
3. A feature tem `Âncoras da SPEC`, `Arquivos:`, 3 criterios, `Verificacao:` com typecheck e `Dicas:`: ok.
4. `abt spec check --item-file`: `ok: true`, `legacy: false`, 2 ancoras `ok`, trechos de 7 e 11 linhas: ok.
5. Ids no formato (`zz-74e`, 6 caracteres; `zz-74e-descartavel`, 18), livres em `abt epic list --ids` e `abt queue list --ids`; sem dependencias: ok.
6. Nenhum marcador do modelo sobrando (grep com saida vazia, status 1): ok.
7. Nenhum `§EPIC-` fora de bloco cercado (awk sobre `.abt/SPEC.md` e `.abt/items/zz-74e/*.md`, saida vazia): ok.

## 5. Destino e acao

| Destino | Acao | Status |
|---------|------|--------|
| .abt/items/zz-74e/zz-74e-descartavel.md | criado | ok |

## 6. Pendencias e ajustes

- ERR-001 do relatorio de validacao da SPEC, aprovado como pendencia: o detalhe aceita `.abt/reviews/zz-74e-descartavel.md` como unica mudanca alem do arquivo de prova (Opcao A); a SPEC aprovada (60.2) nao foi editada.
- Sem `smoke:`: o item nao toca o backend nem sobe processo.
- `.abt/WORKFLOW.md` nao tem secao de comandos; recomendo acrescentar o typecheck (`python -m mypy --platform win32 filepilot tests`) e os testes (`pytest`) que o CI ja usa. A pessoa decide; o Hugo nao edita o arquivo.
- O id do item segue o pedido da pessoa (`zz-74e-descartavel`), nao a forma `<epic_id>-<n>` dos itens anteriores, confirmado no plano do fatiamento.
- `abt scaffold --check`: `.abt/RULES.md`, `.abt/WORKFLOW.md` e `.abt/SPEC.md` mantidos; nada faltando.
- Skill ignorada por nao ser da stack: `vuetify-sneat-ui-patterns`.

Retorno: harness
