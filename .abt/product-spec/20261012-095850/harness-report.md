# Relatorio do Detalhe dos Itens: filepilot-fix

**Data:** 2026-10-12
**Modo:** so SPEC + itens
**Stack:** Python 3.12, pyproject.toml (comandos da tabela por stack do Passo 3, com o comando unico de mypy de 19.2 da SPEC)

## 1. Secao da SPEC

Secao nova `## 27. Correcao de quatro defeitos de leitura de pasta, ordem da lista e organizacao interrompida [DELTA 2026-10-12, defeitos da main antes da interface]`, linhas 897 a 1044 de `.abt/SPEC.md` (total de 1044 linhas):

| Subsecao | Linhas |
|---|---|
| 27.1 Objetivo e fora de escopo | 899 a 918 |
| 27.2 D1: pasta com laco de atalhos e pasta invalida | 919 a 939 |
| 27.3 D2: variavel de ambiente vazia vale como ausente | 940 a 957 |
| 27.4 D3: ordem total e repetivel da lista de arquivos | 958 a 975 |
| 27.5 D4: banco indisponivel no meio da organizacao | 976 a 1017 |
| 27.6 Pendencias para decisao e 27.7 Traceability Matrix | 1018 a 1044 (nunca alvo de `Linhas da SPEC`) |

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-fix-1 | Laco de atalhos na leitura da pasta vira PASTA_INVALIDA | 2 | filepilot-v1-2 | 1 |
| 2 | filepilot-fix-2 | Variavel de ambiente vazia nao torna a pasta atual protegida | 2 | filepilot-fix-1 | 1 |
| 3 | filepilot-fix-3 | Ordem estavel da lista de arquivos com nomes que so diferem por maiuscula | 1 | filepilot-v1-2 | 1 |
| 4 | filepilot-fix-4 | Organizacao interrompida e recuperacao ao abrir o banco | 8 | filepilot-v1-6 | 2 |

Total: 4 itens, 13 pontos, 5 features. Ids conferidos de novo nesta fase: o epico `filepilot-fix` e os itens `filepilot-fix-1` a `filepilot-fix-4` nao constam em `abt epic list --ids` nem em `abt queue list --ids`.

## 3. Linhas da SPEC por feature

| Feature | Linhas da SPEC | Subsecao |
|---|---|---|
| filepilot-fix-1-f1 | L919-939 | 27.2 |
| filepilot-fix-2-f1 | L940-957 | 27.3 |
| filepilot-fix-3-f1 | L958-975 | 27.4 |
| filepilot-fix-4-f1 | L978-989 | 27.5 (helper, pontos de chamada, `rollback` e comportamento das falhas) |
| filepilot-fix-4-f2 | L991-1005 | 27.5 (recuperacao ao abrir o banco e seus testes) |

Os testes de `filepilot-fix-4-f1` (27.5, "Testes obrigatorios", linhas 1007 a 1016) ficam na mesma subsecao, fora do intervalo apertado de L978-989; as `Dicas:` e os criterios da feature os reproduzem.

## 4. Checklist mecanico

1. Um detalhe por item, em `.abt/items/filepilot-fix/<item_id>.md`, com linha 1, cabecalho e as quatro secoes `## Objetivo`, `## Contexto herdado`, `## Features` e `## Gates do item`: ok (4 de 4).
2. `Ordem`, `Pontos` e `Depende de` iguais aos do `itens.md`; `Pontos` de 1 a 8: ok.
3. Toda feature com `Linhas da SPEC`, `Arquivos:`, de 2 a 5 criterios, `Verificacao:` com typecheck e `Dicas:`: ok (5 de 5; 4, 3, 3, 5 e 4 criterios).
4. Todo intervalo com `1 <= a <= b <= 1044` (o `total:` do awk do mapa), no maximo 60 linhas, dentro de subsecao de conteudo da secao nova, fora da matriz, de `Pendencias para decisao` e de `## §N`: ok (L919-939, L940-957, L958-975, L978-989, L991-1005).
5. Ids no formato; dependencias sem ciclo e so para item anterior ou existente (`filepilot-v1-2`, `filepilot-v1-6`, `filepilot-fix-1`): ok.
6. Nenhum marcador do modelo sobrando nos detalhes (o `grep -nE` do Passo 6): ok, saida vazia.
7. Nenhum marcador de placeholder de secao fora de bloco cercado (o awk de `.abt/SPEC.md` e `.abt/items/filepilot-fix/*.md`): ok, saida vazia.

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-fix/filepilot-fix-1.md | criado | gravado |
| .abt/items/filepilot-fix/filepilot-fix-2.md | criado | gravado |
| .abt/items/filepilot-fix/filepilot-fix-3.md | criado | gravado |
| .abt/items/filepilot-fix/filepilot-fix-4.md | criado | gravado |

Nenhum destino existia antes: a pasta `.abt/items/filepilot-fix/` foi criada por esta execucao. Convencao de nomes seguida: `<epic_id>-<n>`, como em `filepilot-v1-1` a `filepilot-v1-13`. Epicos com pasta ja existentes: `filepilot-mypy`, `filepilot-mypy-win32` e `filepilot-v1`.

## 6. Pendencias e ajustes

- Estrutura `.abt/`: `abt scaffold --check` devolveu `mantido` para `RULES.md`, `WORKFLOW.md` e `SPEC.md`; nenhuma pendencia `Bloqueante`.
- Comandos de verificacao: `.abt/WORKFLOW.md` nao traz secao de comandos. Recomendacao: acrescentar nele, a criterio da pessoa, o comando unico de tipos de 19.2 (`python -m mypy --platform win32 filepilot`) e `pytest`; Hugo nao escreve nesse arquivo. Nos detalhes, o typecheck usa a forma de 19.2, e nao a da tabela do Passo 3 (`mypy . --no-error-summary`), porque a SPEC proibe outra forma de chamar o mypy.
- Smoke omitido nos quatro itens: o FilePilot nao tem processo de servidor, porta nem rota de saude no codigo nem na SPEC (e uma aplicacao desktop com bibliotecas de servico), entao nao ha smoke a escrever.
- Ajuste em relacao a 27.5: os testes de 27.5 (4 e 7) e da recuperacao (1) citam `last_undoable(conn)`, que ainda nao existe no codigo (`filepilot/services/history.py` e do item `filepilot-v1-7`). Conforme o plano confirmado com a opcao A, o detalhe de `filepilot-fix-4` manda conferir pela condicao em SQL de 6.4 (`status IN ('concluida','interrompida') AND moved_count >= 1`), sem importar `history`. A SPEC nao foi editada.
- Sobreposicao com a fila: `filepilot-v1-7-f2` (na fila, disponivel) tambem descreve a recuperacao ao abrir o banco e nao recalcula as contagens. Pelo plano, `filepilot-fix-4` e o dono. Acao da pessoa, fora desta execucao: retirar de `filepilot-v1-7-f2` o criterio "Ao abrir o banco, toda linha `em_andamento` vira `interrompida`" e o `grep deve casar: interrompida em filepilot/db/connection.py`.
- `filepilot-fix-4` depende de `filepilot-v1-6`, que esta em andamento e move codigo de `organizer.py` para `destination_checks.py`: o detalhe cita as funcoes `_run`, `_open_organization` e `_close_organization`, nao so numeros de linha, e os numeros de `organizer.py` em `Arquivos:` podem deslocar depois da mesclagem de `filepilot-v1-6`.
- Ajustes do `itens.md`: nenhum.
- Contratos compartilhados: nenhum contrato novo entre camadas; a assinatura `_is_protected(folder, resolved)` fica so em `scanner.py` e nenhum teste existente a chama direto.

Retorno: harness
