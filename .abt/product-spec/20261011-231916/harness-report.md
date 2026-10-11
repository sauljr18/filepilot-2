# Relatorio do Detalhe dos Itens: filepilot-mypy

**Data:** 2026-10-11
**Modo:** so SPEC + itens
**Stack:** Python 3.12 (comandos de pyproject.toml da SPEC 4, da tabela por stack e do comando de 17.2; .abt/WORKFLOW.md nao traz secao de comandos)

## 1. Secao da SPEC

Secao 17 de `.abt/SPEC.md`, linhas 747-799 (total: 799), com `[DELTA 2026-10-11, mypy e Windows 10 e 11 em 64 bits]`. Subsecoes de conteudo: 17.1 (L749-757), 17.2 (L758-773), 17.3 (L774-786). `Pendencias para decisao` (L787-790) e `Traceability Matrix` (L791-799) nao sao alvo de `Linhas da SPEC`.

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-mypy-1 | Checagem de tipos com mypy no pyproject | 2 | filepilot-v1-1 | 1 |

Total: 1 item, 2 pontos.

## 3. Linhas da SPEC por feature

| Feature | Linhas da SPEC | Subsecao |
|---|---|---|
| filepilot-mypy-1-f1 | .abt/SPEC.md L758-773 | 17.2 Ferramentas de desenvolvimento: mypy |

## 4. Checklist mecanico

1. ok - um detalhe por item do `itens.md`, em `.abt/items/filepilot-mypy/filepilot-mypy-1.md`, com linha 1, cabecalho e as quatro secoes (`## Objetivo`, `## Contexto herdado`, `## Features`, `## Gates do item`).
2. ok - `Ordem: 1`, `Pontos: 2` e `Depende de: filepilot-v1-1` iguais aos do `itens.md`.
3. ok - a feature tem `Linhas da SPEC`, `Arquivos:`, 4 criterios de aceite, `Verificacao:` com typecheck e `Dicas:`.
4. ok - L758-773 tem 16 linhas, esta entre 1 e 799 (total do awk) e fica dentro de 17.2; nao toca matriz, `Pendencias para decisao` nem `## §N`.
5. ok - `epic_id` filepilot-mypy (14 caracteres) e `item_id` filepilot-mypy-1 no formato, livres (`abt epic list --ids` e `abt queue list --ids` nao os listam); `Depende de` aponta so para filepilot-v1-1, que ja existe na fila; sem ciclo.
6. ok - nenhum marcador do modelo sobrando (o grep saiu vazio).
7. ok - nenhum `§EPIC-` fora de bloco cercado (o awk saiu vazio).

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-mypy/filepilot-mypy-1.md | criado | ok |

## 6. Pendencias e ajustes

- Sem `Bloqueante`: `abt scaffold --check` com `.abt/RULES.md`, `.abt/WORKFLOW.md` e `.abt/SPEC.md` mantidos.
- Achado nesta fase, decidido pela pessoa (opcao A): o detalhe de `filepilot-v1-1` (`.abt/items/filepilot-v1/filepilot-v1-1.md`, linhas 24, 31, 33 e 90) ja declara `mypy` sem versao, usa `mypy . --no-error-summary` e roda mypy no workflow do GitHub Actions. Isso contradiz a afirmacao do `sprint-validation-report.md` e do `itens.md` (riscos) de que os 13 itens existentes nao citam mypy, e a frase de 17.2 de que esta especificacao nao acrescenta mypy ao fluxo do GitHub Actions (a frase fala da secao 17; o workflow ja vem de `filepilot-v1-1`). Nada foi editado: `filepilot-v1-1`, o `itens.md`, a SPEC e os relatorios anteriores ficam como estao. O item `filepilot-mypy-1` mantem trabalho proprio: fixar `mypy==2.4.0` e adotar `python -m mypy --platform win32 filepilot`.
- Typecheck do item: o comando e o de 17.2, e nao o `mypy . --no-error-summary` da tabela por stack, porque a SPEC fixa o comando e o `--platform win32`. A diferenca com os itens existentes e consequencia disso.
- `Arquivos:` traz `pyproject.toml (novo)` porque o arquivo ainda nao existe (criado por `filepilot-v1-1`); o item so altera uma linha dele, como a primeira `Dicas:` explica.
- Smoke omitido: o item nao conclui backend e nao tem processo, porta nem rota de saude (Passo 3 nota 5 do prompt do agente).
- Recomendacao: `.abt/WORKFLOW.md` nao traz comandos de verificacao; a pessoa decide se acrescenta os de Python (`python -m mypy --platform win32 filepilot` e `pytest`). Hugo nao o edita.
- Pendencia para decidir depois (fora desta execucao): `filepilot-v1-1` roda `mypy .` sem `--platform win32` no runner Windows, onde isso e equivalente; fora do Windows o comando antigo acusaria erro nos trechos so de Windows.

Retorno: harness
