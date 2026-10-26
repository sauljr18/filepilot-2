# Itens - Arquivo de prova do smoke 74e

Epico: zz-74e
Titulo do epico: Arquivo de prova do smoke 74e
**Data:** 2026-10-26
**Modo:** so SPEC + itens

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|-------|---------|--------|--------|------------|----------|
| 1 | zz-74e-descartavel | Arquivo de prova rascunho/74e-prova.md do smoke 74e | 1 | - | O repositorio passa a ter rascunho/74e-prova.md com a linha prova do smoke 74e e nenhuma outra mudanca de produto |

## 2. Criterios de aceite

- zz-74e-descartavel:
  - `git show HEAD:rascunho/74e-prova.md | cmp - <(printf 'prova do smoke 74e\n')` sai com 0 na branch do item.
  - `git diff --name-only origin/main...HEAD` na branch do item lista `rascunho/74e-prova.md` e, alem dele, no maximo o relatorio de validacao do item, `.abt/reviews/zz-74e-descartavel.md`.
  - `git diff --name-only origin/main...HEAD -- filepilot tests packaging pyproject.toml .github` nao imprime nada.

## 3. Mapa para a SPEC

- zz-74e-descartavel: 60.1 Objetivo e fora de escopo; 60.2 Arquivo rascunho/74e-prova.md.

## 4. Riscos

| Risco | Severidade | Acao |
|-------|------------|------|
| ERR-001 pendente no relatorio do Rafael: 60.2 pede so `rascunho/74e-prova.md` no diff, mas o PR do item leva tambem `.abt/reviews/zz-74e-descartavel.md` | Medio | O criterio de aceite aceita so esse relatorio do abt como mudanca extra (Opcao A do ERR-001); nenhum arquivo de produto alem do de prova |

## 5. Cobertura

| Item do escopo | Item |
|----------------|------|
| Item `zz-74e-descartavel` cria `rascunho/74e-prova.md` com a linha `prova do smoke 74e` | zz-74e-descartavel |
| Fora de escopo: codigo de qualquer tipo | zz-74e-descartavel (3o criterio) |
| Fora de escopo: testes | zz-74e-descartavel (3o criterio) |
| Fora de escopo: mudanca em qualquer outro arquivo | zz-74e-descartavel (2o e 3o criterios) |
| Metrica: solicitacao de mesclagem do item aberta com so rascunho/74e-prova.md no diff | zz-74e-descartavel (2o criterio, com o risco Medio) |
| Metrica: conteudo do arquivo e exatamente uma linha | zz-74e-descartavel (1o criterio) |
