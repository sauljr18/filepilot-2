# Relatorio de Validacao da SPEC - Round 2/3

**Data:** 2026-10-12
**Modo:** so SPEC + itens
**Secao auditada:** ## 27. Correcao de quatro defeitos de leitura de pasta, ordem da lista e organizacao interrompida

## Resumo

| Categoria | Encontrados | Corrigidos auto | Requer decisao |
|---|---|---|---|
| Erros | 0 | 0 | 0 |
| Inconsistencias | 0 | 0 | 0 |
| Scope Creep | 0 | 0 | 0 |
| Lacunas vs. PRD | 0 | 0 | 0 |
| Definicoes Vagas | 0 | 0 | 0 |
| Inconsistencia de Nomenclatura | 0 | 0 | 0 |
| Total | 0 | 0 | 0 |

A Round 1 achou 7 itens (6 corrigidos sozinhos e GAP-001 aguardando decisao); esta rodada aplicou a decisao da pessoa (secao Decisoes registradas) e auditou de novo as seis categorias, sem achados novos.

Conferido nesta rodada contra o codigo lido nesta execucao: `filepilot/db/connection.py:12` a `:28` (`open_connection`: o `try` que a recuperacao reaproveita, o `except` que fecha a conexao e levanta `BANCO_INDISPONIVEL`); `filepilot/db/migrations.py:30` e `:110` a `:131` (tabelas criadas antes da recuperacao); `filepilot/services/organizer.py:130`, `:175` a `:187` (as contagens so sao gravadas no fechamento, o que justifica o recalculo a partir de `operations`), `:190` a `:221`; `tests/db/test_migrations.py:163` a `:170` e `tests/services/test_organizer.py:85` a `:104` (os dois testes existentes que leem `em_andamento` criam a linha depois de `open_connection` ou leem por `sqlite3.connect` direto, entao a recuperacao na abertura nao os altera).

## Correcoes Aplicadas Automaticamente

Nenhuma nesta rodada.

## Itens Aguardando Decisao

Nenhum. O GAP-001 da Round 1 foi decidido pela pessoa (opcao A) e o item saiu de `Pendencias para decisao` (a subsecao ficou com a linha dizendo que nao ha decisao pendente e com um registro fora de escopo).

## Decisoes registradas

- Linhas `CORTADO`: nenhuma.
- Decisoes da nota aplicadas nesta rodada: `[DECISAO: aprovada no ponto de checagem; opcao A do GAP-001, a recuperacao na abertura entra na correcao do defeito 4]`. Aplicada DENTRO da secao 27: 27.1 (escopo e linha D4 da tabela), 27.5 (nova funcao `_recover_interrupted` em `filepilot/db/connection.py`, chamada por `open_connection`; contagens recalculadas das operacoes; `finished_at` com a hora da recuperacao; premissa de nenhuma organizacao em curso; 4 testes novos em `tests/db/test_connection_recovery.py`), 27.6 (a pendencia 1 saiu) e 27.7 (F4 de `parcial` para `coberto`, com a marca na coluna `Origem`). Nenhuma secao existente nem cabecalho `## §N` foi editado; a recuperacao implementa o que 5.3 ja descreve.
- Decisoes aprovadas pela pessoa vistas (nao sao achados): `[DECISAO: aprovada no enriquecimento; sugestao 1]`, `[DECISAO: aprovada no enriquecimento; sugestao 2]` e `[DECISAO: aprovada no enriquecimento; sugestao 3]`, cada uma com linha em 27.7.
- `[DECISAO: <motivo>]` do Gabriel e as acrescentadas para cumprir a opcao A (isentas so de Scope Creep): 27.2 (so o laco vira `PASTA_INVALIDA`; resolver uma vez; texto de `PASTA_INVALIDA`), 27.3 (as tres variaveis; valor relativo fora de escopo; so espacos), 27.4 (desempate pelos pontos de codigo), 27.5 (`rollback` em `_open_organization`; status `interrompida`; recalculo das contagens; hora da recuperacao; premissa de nenhuma organizacao em curso).
- Registro fora de escopo em 27.6 (laco de atalhos no destino do planner, `planner.py:49`): confirmado na descoberta; nao e achado nem decisao pendente.

## Status apos Round 2

APROVAVEL - SPEC sem erros, inconsistências ou lacunas; pronta para aprovação.

Retorno: validacao-spec
