# Relatorio de Validacao da SPEC - Round 2/3

**Data:** 2026-10-12
**Modo:** so SPEC + itens
**Secao auditada:** ## 37. Correcao de quatro defeitos de desfazer, aba Organizar, instancia unica e planejamento [DELTA 2026-10-12, defeitos da main antes das proximas telas]

## Resumo

Contagens da Round 2 (a Round 1 achou 3 itens, todos corrigidos; as correcoes estao abaixo).

| Categoria | Encontrados | Corrigidos auto | Requer decisao |
|---|---|---|---|
| Erros | 0 | 0 | 0 |
| Inconsistencias | 0 | 0 | 0 |
| Scope Creep | 0 | 0 | 0 |
| Lacunas vs. PRD | 0 | 0 | 0 |
| Definicoes Vagas | 0 | 0 | 0 |
| Inconsistencia de Nomenclatura | 0 | 0 | 0 |
| Total | 0 | 0 | 0 |

## Correcoes Aplicadas Automaticamente

Aplicadas na Round 1 e conferidas na Round 2.

### INC-001: o teste 5 de 37.2 afirmava o que nao provava

- **Problema:** o teste 5 dizia que `test_banco_fechado_levanta_banco_indisponivel` provava que o `rollback` numa conexao fechada nao troca o erro. Esse teste fecha a conexao antes de `undo_last`, e a falha acontece antes, em `last_undoable` (`filepilot/services/history.py:136`), fora do caminho do `_rollback`.
- **Referencia:** F1 (discovery-notes.md); 37.2, teste 5.
- **Localizacao na SPEC:** `### 37.2`, testes obrigatorios, item 5.
- **Evidencia:** `filepilot/services/undo.py:150` a `:156` (`last_undoable` roda antes do `try` que chama `_run`); `tests/services/test_undo.py:365` a `:372`.
- **Correcao aplicada:** o item 5 virou um teste novo que fecha a conexao dentro de `_record_status` trocado por `monkeypatch`, levantando `sqlite3.OperationalError`; confere `BANCO_INDISPONIVEL`, ausencia de `ProgrammingError` e o arquivo de volta em `Documentos/a.pdf`. O teste existente ficou citado como regressao, com a ressalva de que nao prova o `rollback`.

### INC-002: um teste de E4 morava no arquivo de teste de E2

- **Problema:** o teste 6 de 37.5 era gravado em `tests/ui/test_organize_tab_read_error.py`, arquivo criado pelo item de E2. 37.1 diz que os defeitos sao independentes e a ordem de entrega e livre; entregar E4 antes de E2 deixaria o teste sem arquivo.
- **Referencia:** F5 (discovery-notes.md); 37.1 ("Os defeitos sao independentes"); 37.5, teste 6.
- **Localizacao na SPEC:** `### 37.5`, testes obrigatorios, item 6.
- **Evidencia:** `### 37.3` cria `tests/ui/test_organize_tab_read_error.py`; `### 37.5` o reaproveitava.
- **Correcao aplicada:** o teste 6 passou para o arquivo novo `tests/ui/test_organize_tab_plan_loop.py`, proprio de E4, com `_tab`, `_pick`, `_folder_with` e `conn` copiados de `tests/ui/test_organize_tab_folder.py:15` a `:43`.

### VAG-001: condicao de `skip` do teste 5 de 37.4 sem criterio verificavel

- **Problema:** "quando a tentativa de `tryLock` na pasta ainda funcionar" nao dizia como o teste decide pular nem como a permissao e desfeita.
- **Referencia:** F3 (discovery-notes.md); 37.4, teste 5.
- **Localizacao na SPEC:** `### 37.4`, testes obrigatorios, item 5.
- **Evidencia:** o teste usa `chmod 0o500`, que e ignorado sob `root`; `tests/ui/test_single_instance.py:44` a `:70` mostra o uso da `QLockFile` real.
- **Correcao aplicada:** a condicao ficou "no Windows e quando a permissao e ignorada", verificada por uma `QLockFile` de teste na mesma pasta com `tryLock(0)` verdadeiro, depois liberada com `unlock()`; o `chmod` e desfeito num `finally`.

## Itens Aguardando Decisao

Nenhum. `### 37.6 Pendencias para decisao` diz que nao ha decisao pendente; os tres registros fora de escopo dali nao sao pendencias.

## Decisoes registradas

Decisoes aprovadas pela pessoa, vistas e nao tratadas como achado:

- `[DECISAO: aprovada no enriquecimento; sugestao 1]`: so o destino de arquivo com categoria ou regra e resolvido (37.5, teste 8).
- `[DECISAO: aprovada no enriquecimento; sugestao 2]`: texto `_LOCK_UNAVAILABLE` da falha de acesso a pasta de dados (37.4).
- `[DECISAO: aprovada no enriquecimento; recusada a sugestao 3, so os quatro defeitos pedidos]`: laco de atalhos no desfazer registrado fora de escopo (37.6, item 4).

`[DECISAO: <motivo>]` do Gabriel, isentas so de Scope Creep (auditadas e sem Erro nem Lacuna): `rollback` suprimido em `_rollback` (37.2); so `OSError` vira `PASTA_ILEGIVEL`, com o texto de 6 repetido como constante (37.3); "Atualizar" e "Escolher pasta..." habilitados em `erro` (37.3); qualquer motivo diferente de `LockFailedError` vira falha de acesso (37.4); `resolve_folder` publico (37.5); laco no planejamento vira `PASTA_INVALIDA` com a mensagem de 6 (37.5); registros fora de escopo 1 a 3 de 37.6.

Nenhuma linha `CORTADO` (modo so SPEC + itens, sem `stack-decision.md`).

Conferido contra o codigo desta execucao, sem achado: `filepilot/services/undo.py:66` a `:77`, `:103` a `:137`, `:140` a `:158`; `filepilot/ui/organize_tab.py:40`, `:93` a `:96`, `:128` a `:141`; `filepilot/__main__.py:36` a `:51`; `filepilot/services/planner.py:48` a `:49`, `:73`, `:76`, `:85`; `filepilot/services/scanner.py:52` a `:61`, `:115`; `filepilot/db/connection.py:44` a `:62` (transacao implicita do `sqlite3`, medida com Python 3.12.3); `tests/services/test_scanner_loop.py:15` a `:21`; `tests/ui/test_single_instance.py`. Nenhuma secao existente nem `## §N` foi editada (0 linhas removidas no `git diff`); nenhum `§EPIC-` fora de bloco cercado; nenhuma subsecao acima de 60 linhas (maior: 37.5, com 26). A skill de Vuetify nao foi lida (o projeto usa PySide6).

## Status apos Round 2

APROVAVEL: SPEC sem erros, inconsistencias ou lacunas; pronta para aprovacao.

Retorno: validacao-spec
