# Relatorio do Detalhe dos Itens: filepilot-opcao-v

**Data:** 2026-10-25
**Modo:** delta focado
**Stack:** Python 3 com PySide6, pytest e mypy (comandos da tabela por stack do Passo 3, com o typecheck dos gates de 19.2 com 45.7: `python -m mypy --platform win32 filepilot tests`; `.abt/WORKFLOW.md` sem secao de comandos)

## 1. Secao da SPEC

`## 58. Opcao -V na linha de comando [DELTA 2026-10-25, python -m filepilot -V]`, linhas 1644 a 1740 de `.abt/SPEC.md`. Subsecoes de conteudo citadas: 58.1 e 58.6 pela propria ancora; 58.4 (`{acrescenta: 54.2}`) pela ancora alvo 54.2; 58.5 (`{substitui: 56.3}`) pela ancora alvo 56.3. As erratas 58.2 (`{acrescenta: 54.1}`) e 58.3 (`{acrescenta: 56.1}`) so mudam o fora de escopo e nao sao citadas por feature.

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-opcao-v-1 | Opcao -V imprime a versao e aparece na ajuda | 2 | filepilot-version-1,filepilot-help-1 | 2 (f1 desvio -V e testes; f2 texto de uso e teste do --help) |

## 3. Ancoras da SPEC por feature

| Feature | Ancora | sha12 | Linhas | Subsecao |
|---|---|---|---|---|
| filepilot-opcao-v-1-f1 | 54.2 | a90d9766fdf3 | 38 | 54.2 Ponto de entrada com --version (vigente, com a errata 58.4) |
| filepilot-opcao-v-1-f1 | 58.6 | 25f24e9b530b | 10 | 58.6 Testes do -V e do texto de uso |
| filepilot-opcao-v-1-f1 | 58.1 | 05fb06b3f6bf | 12 | 58.1 Objetivo e fora de escopo |
| filepilot-opcao-v-1-f2 | 56.3 | 7c0bdbff240f | 28 | 56.3 Ponto de entrada com --help e -h (vigente, substituida por 58.5) |
| filepilot-opcao-v-1-f2 | 58.6 | 25f24e9b530b | 10 | 58.6 Testes do -V e do texto de uso |

## 4. Checklist mecanico

1. Um detalhe por item em `.abt/items/filepilot-opcao-v/filepilot-opcao-v-1.md`, com linha 1, cabecalho e as secoes `## Objetivo`, `## Contexto herdado` (`-`), `## Features` e `## Gates do item`: ok.
2. `Ordem` 1, `Pontos` 2 e `Depende de` `filepilot-version-1,filepilot-help-1`, iguais ao `itens.md`: ok.
3. As 2 features com linha de ancoras, `Arquivos:`, criterios (4 e 3), `Verificacao:` com typecheck e `Dicas:`: ok.
4. `abt spec check --item-file .abt/items/filepilot-opcao-v/filepilot-opcao-v-1.md --json`: `ok: true`, `data.legacy` false, 4 ancoras `ok`; trechos de 10 a 38 linhas no `data.text`: ok.
5. Ids no formato (`filepilot-opcao-v`, 17 caracteres; `filepilot-opcao-v-1`), livres em `abt epic list --ids` e `abt queue list --ids`; dependencias so para itens existentes (`pronto`), sem ciclo: ok.
6. Marcadores do modelo: `grep -nE` sem saida (status 1): ok.
7. `§EPIC-` fora de bloco cercado: o awk sobre `.abt/SPEC.md` e `.abt/items/filepilot-opcao-v/*.md` sem saida: ok.

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-opcao-v/filepilot-opcao-v-1.md | criado | ok |

## 6. Pendencias e ajustes

- Nenhuma pendencia `Bloqueante`: `abt scaffold --check --json` com `.abt/RULES.md`, `.abt/WORKFLOW.md` e `.abt/SPEC.md` `mantido`.
- Smoke sem servidor: o FilePilot e aplicativo de janela sem porta nem rota de saude; o `smoke:` roda `python -m filepilot -V` e `python -m filepilot --help`, que saem sem abrir a janela.
- Recomendacao: acrescentar ao `.abt/WORKFLOW.md` uma secao de comandos (`python -m mypy --platform win32 filepilot tests`, `pytest`); a pessoa decide.
- Nenhum ajuste no `itens.md`. Skill ignorada por nao ser da stack: `vuetify-sneat-ui-patterns` (PySide6).

Retorno: harness
