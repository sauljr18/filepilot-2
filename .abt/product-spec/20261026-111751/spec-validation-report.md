# Relatorio de Validacao da SPEC - Round 1/3

**Data:** 2026-10-26
**Modo:** so SPEC + itens
**Secao auditada:** ## 60. Arquivo de prova do smoke 74e [DELTA 2026-10-26, rascunho/74e-prova.md]

## Resumo

| Categoria | Encontrados | Corrigidos auto | Requer decisao |
|-----------|-------------|-----------------|----------------|
| Erros | 1 | 0 | 1 |
| Inconsistencias | 0 | 0 | 0 |
| Scope Creep | 0 | 0 | 0 |
| Lacunas vs. PRD | 0 | 0 | 0 |
| Definicoes Vagas | 0 | 0 | 0 |
| Inconsistencia de Nomenclatura | 0 | 0 | 0 |
| Total | 1 | 0 | 1 |

Conferido no codigo nesta execucao: `pyproject.toml:23` (`include = ["filepilot*"]`) e `.github/workflows/tests.yml:22` (`python -m mypy --platform win32 filepilot tests`), citados em 60.2, conferem. A raiz do repositorio nao tem `rascunho/` nem `.gitattributes` (60.1, 60.2), confere. Os 6 itens do escopo de `discovery-notes.md` tem linha na Traceability Matrix e elemento em 60.1 ou 60.2. Skill ignorada por nao ser da stack: `vuetify-sneat-ui-patterns` (o manifesto nao tem Vuetify).

## Correcoes Aplicadas Automaticamente

Nenhuma.

## Itens Aguardando Decisao

### ERR-001: o diff do item tera tambem o relatorio de validacao do item

- **Problema:** 60.1 poe fora de escopo a mudanca em qualquer outro arquivo, e 60.2 exige que `git diff --name-only origin/main...HEAD` liste so `rascunho/74e-prova.md`. Mas a solicitacao de mesclagem de todo item deste projeto leva tambem o relatorio de validacao do item em `.abt/reviews/<item_id>.md`, gravado pelo fluxo de implementacao do abt. Como esta, o criterio de 60.2 e a metrica falham no proprio item.
- **Referencia:** item do escopo "Metrica: solicitacao de mesclagem do item aberta com so rascunho/74e-prova.md no diff" e "Fora de escopo: mudanca em qualquer outro arquivo" (discovery-notes.md).
- **Localizacao:** 60.1 (fora de escopo, 3o item) e 60.2 (verificacao objetiva).
- **Evidencia:** `git show --stat` dos commits de item mesclados: `83cd94f` (filepilot-opcao-v-1) traz `.abt/reviews/filepilot-opcao-v-1.md`; `c0f195f` (filepilot-help-1) traz `.abt/reviews/filepilot-help-1.md`; o de filepilot-version-1 traz `.abt/reviews/filepilot-version-1.md`.
- Opcao A: 60.1 e 60.2 passam a aceitar, alem de `rascunho/74e-prova.md`, so o `.abt/reviews/zz-74e-descartavel.md` do fluxo do abt; a verificacao lista esses dois e nada mais.
- Opcao B: manter "so rascunho/74e-prova.md" no diff; o item fica sem o relatorio de validacao versionado, fora do padrao dos itens anteriores.

## Decisoes registradas

- `[DECISAO: arquivo de texto termina em quebra de linha, como os demais do repositorio; uma linha so, como no pedido]` (60.2, Gabriel): isenta de Scope Creep; nao contradiz o escopo.
- `[DECISAO: aprovada no enriquecimento; sugestao 1]` (60.2): verificacao pelo arquivo versionado, LF, sem `.gitattributes`. Decisao da pessoa, nao e achado.
- Nenhuma linha `CORTADO`.

## Status apos Round 1

PENDENTE - 1 itens aguardando decisao

- ERR-001: o diff do item aceita tambem `.abt/reviews/zz-74e-descartavel.md` (Opcao A) ou continua so com `rascunho/74e-prova.md` (Opcao B).

Retorno: validacao-spec
