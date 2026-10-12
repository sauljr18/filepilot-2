# Relatorio do Detalhe dos Itens: filepilot-fix2

**Data:** 2026-10-12
**Modo:** so SPEC + itens
**Stack:** Python 3.12 com PySide6 6.12.0, pytest 9.1.1 e mypy 2.4.0 (comandos da tabela por stack do Hugo, com o mypy pelo comando unico de 19.2 da SPEC; `.abt/WORKFLOW.md` nao traz secao de comandos)

## 1. Secao da SPEC

Secao `## 37. Correcao de quatro defeitos de desfazer, aba Organizar, instancia unica e planejamento [DELTA 2026-10-12, defeitos da main antes das proximas telas]`, linhas 1082 a 1225 de `.abt/SPEC.md` (total: 1225). Subsecoes de conteudo: 37.1 (L1084-1103), 37.2 (L1104-1125), 37.3 (L1126-1146), 37.4 (L1147-1168), 37.5 (L1169-1194). `37.6 Pendencias para decisao` (L1195-1205) e `37.7 Traceability Matrix` (L1206-1225) nao sao alvo de `Linhas da SPEC`.

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-fix2-1 | Desfazer com banco indisponivel faz rollback e permite novo desfazer | 3 | filepilot-v1-7 | 1 |
| 2 | filepilot-fix2-2 | Aba Organizar sai de carregando quando a leitura da pasta falha com erro do sistema | 2 | filepilot-v1-9 | 1 |
| 3 | filepilot-fix2-3 | Instancia unica avisa quando nao consegue saber se ha outra janela aberta | 3 | filepilot-v1-8 | 1 |
| 4 | filepilot-fix2-4 | Planejamento com laco de atalhos vira PASTA_INVALIDA | 3 | filepilot-fix-1,filepilot-v1-4 | 2 |

Total: 4 itens, 11 pontos, 5 features.

## 3. Linhas da SPEC por feature

| Feature | Linhas da SPEC | Subsecao |
|---|---|---|
| filepilot-fix2-1-f1 | .abt/SPEC.md L1104-1125 | 37.2 E1: banco indisponivel no meio do desfazer |
| filepilot-fix2-2-f1 | .abt/SPEC.md L1126-1146 | 37.3 E2: aba Organizar presa em carregando |
| filepilot-fix2-3-f1 | .abt/SPEC.md L1147-1168 | 37.4 E3: instancia unica sem fechar em silencio |
| filepilot-fix2-4-f1 | .abt/SPEC.md L1169-1194 | 37.5 E4: planejamento com laco de atalhos |
| filepilot-fix2-4-f2 | .abt/SPEC.md L1169-1194 | 37.5 E4: planejamento com laco de atalhos |

## 4. Checklist mecanico

1. ok: um detalhe por item do `itens.md`, em `.abt/items/filepilot-fix2/<item_id>.md`, com linha 1, cabecalho e as quatro secoes `## Objetivo`, `## Contexto herdado`, `## Features` e `## Gates do item` (4 de 4 arquivos com as 4 secoes).
2. ok: `Ordem`, `Pontos` e `Depende de` iguais aos do `itens.md` (1/3, 2/2, 3/3 e 4/3); pontos de 1 a 8.
3. ok: toda feature com `Linhas da SPEC`, `Arquivos:`, de 2 a 5 criterios (5, 5, 5, 5 e 3), `Verificacao:` com typecheck e `Dicas:`.
4. ok: todo intervalo dentro de 1 a 1225, de no maximo 60 linhas (22, 21, 22 e 26) e igual a uma subsecao de conteudo da secao nova; nenhum na matriz, na `Pendencias para decisao` nem num `## §N`.
5. ok: ids no formato `^[a-z0-9][a-z0-9-]{1,39}$`, livres na reconferencia de `abt epic list --ids` e `abt queue list --ids` (nenhum dos 4 itens nem o epico `filepilot-fix2` existe); dependencias so com itens ja `pronto`; sem ciclo.
6. ok: nenhum marcador do modelo sobrando nos detalhes (o `grep -nE` do Passo 6 devolveu saida vazia).
7. ok: nenhum `§EPIC-` fora de bloco cercado (o awk sobre `.abt/SPEC.md` e `.abt/items/filepilot-fix2/*.md` devolveu saida vazia).

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-fix2/filepilot-fix2-1.md | criado | gravado nesta execucao |
| .abt/items/filepilot-fix2/filepilot-fix2-2.md | criado | gravado nesta execucao |
| .abt/items/filepilot-fix2/filepilot-fix2-3.md | criado | gravado nesta execucao |
| .abt/items/filepilot-fix2/filepilot-fix2-4.md | criado | gravado nesta execucao |

A pasta `.abt/items/filepilot-fix2/` nao existia; nenhum detalhe existente foi sobrescrito. Convencao de nomes seguida: `<epic_id>-<n>` com `<n>` a ordem (como em `.abt/items/filepilot-fix/`); o epico se chama `filepilot-fix2` porque `filepilot-fix-2` ja e um item do epico `filepilot-fix`.

## 6. Pendencias e ajustes

Nenhuma pendencia `Bloqueante`: `abt scaffold --check --json` devolveu `ok: true` com `.abt/RULES.md`, `.abt/WORKFLOW.md` e `.abt/SPEC.md` mantidos. Nenhum ajuste do `itens.md` foi necessario.

- Smoke omitido nos quatro itens: o FilePilot e um aplicativo desktop do PySide6, sem servidor, porta nem rota de saude no codigo nem na SPEC (Passo 3, nota 5). A evidencia de execucao fica nos testes de interface com `pytest-qt`.
- Gate de testes: a tabela por stack pede `pytest`; os itens usam `pytest <arquivos>` por feature e `pytest` inteiro em `## Gates do item`, como os itens existentes em `.abt/items/filepilot-fix/`.
- Gate de typecheck: `python -m mypy --platform win32 filepilot`, o comando unico de 19.2 (diferente de `mypy . --no-error-summary` da tabela por stack, que 19.2 proibe). A pasta `tests/` fica fora da checagem de tipos.
- Recomendacao: `.abt/WORKFLOW.md` nao tem secao de comandos; a pessoa pode acrescentar os de pytest e mypy de 19.2. Hugo nao a edita.
- Risco Medio (do relatorio de prontidao): `filepilot-fix2-2` e `filepilot-fix2-4` editam arquivos que as proximas telas (`filepilot-v1-10`, `filepilot-v1-11` e `filepilot-v1-13`, na fila) tambem editam; entregar os quatro itens antes delas.
- Os testes novos dependem do PySide6 (`filepilot-fix2-2`, `-3` e o teste de interface de `-4`), que nao estava instalado no ambiente de especificacao; nao foram rodados aqui.
- O item `filepilot-fix2-4` e a feature `-f2` tem arquivo de teste proprio (`tests/ui/test_organize_tab_plan_loop.py`), sem depender dos testes de `filepilot-fix2-2`, para os itens serem entregues em qualquer ordem.

Retorno: harness
