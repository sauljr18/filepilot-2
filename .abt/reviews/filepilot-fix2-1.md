# Validacao do item filepilot-fix2-1 - Desfazer com banco indisponivel faz rollback e permite novo desfazer

**Item:** filepilot-fix2-1 | **Epico:** filepilot-fix2 | **Data:** 2026-10-12
Execucao: 20261012-133743
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "no issues found in 23 source files"; `comm` contra a baseline (exit 0, sem erros) vazio: zero erros novos |
| 2 Criterios de aceite | PASS | 5/5 criterios atendidos |
| 3 Qualidade de codigo | PASS | grep de TODO, placeholder, not implemented e FIXME em undo.py e test_undo_rollback.py: zero; sem codigo comentado nem print |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint novo ou alterado (service local sem autenticacao) |
| 5 Testes | PASS | suite completa 385 passed, 2 skipped (os dois sao `so existe no Windows`: test_destination_checks.py:153 e test_scanner_protected.py:185; justificados e os mesmos da baseline de 380 + 5 novos); mutacoes refeitas abaixo |
| 6 Consistencia entre documentos | PASS | SPEC L1104-1125 (37.2): helper `_rollback` com `contextlib.suppress(sqlite3.Error)`, chamado em `_run` (undo.py:131) antes do `os.rename` e em `undo_last` (undo.py:169); os 5 testes obrigatorios existem; OPERATION_LOCK, mensagem e UndoResult intactos |
| 7b Varredura adversarial | PASS | `_record_status` e `undo_last` so tem consumidor em undo.py e na UI via undo_last; o rollback e interno; nenhuma coluna nova; reuso: organizer.py:106-107 e :123-124 usam o mesmo padrao suppress+rollback inline, o helper novo nao reinventa utilitario existente (nao havia helper) |
| 7c Degradacao e borda | PASS | 1) nenhuma entrada passa a chegar em codigo que levanta; 2) zero ou vazio nao inverte classificacao (zero linhas `movido` devolve restored_count 0 e fecha a organizacao); 3) `last_undoable` fora do try continua como antes (conexao fechada, ver test_undo.py:365-372); fora de escopo conforme SPEC 37.6; 4) comentarios novos corretos, o de undo.py:130 e verdadeiro |
| 7d Matriz (backend) | PASS | BE-1 n/a (nenhum criterio "nenhum ponto faz X"); BE-2 n/a (helper privado, sem service nem DI); BE-3 n/a (sem policies) |
| 7e Funcao irma e comando citado | PASS | 7e-1: irmas `_open_organization` (organizer.py:104-108), `_interrupt_organization` (:123-124) usam `contextlib.suppress(sqlite3.Error)` + `conn.rollback()`; `_rollback` replica isso; OPERATION_LOCK continua no finally de undo_last (undo.py:171-172); 7e-2 n/a (nenhuma mensagem nova manda rodar comando) |

Gates mecanicos da `Verificacao:` da feature rodados por mim: py_compile exit 0; `def _rollback` em undo.py:80; `conn.rollback` em undo.py:87; `asyncio.new_event_loop` sem resultado (grep exit 1); caracteres Unicode tipograficos sem resultado (grep exit 1); pytest dos dois arquivos 25 passed. Gate do item awk de placeholder: saida vazia. Skills de stack (EF Core, .NET, Go, Vuetify) ignoradas: projeto Python/PySide6.

Mutacoes refeitas por mim (suite inteira, reversao por copia de arquivo, `status` e `diff --stat` iguais ao inicial depois):

| # | Mutacao (diff) | Resultado |
|---|----------------|-----------|
| M1 | remove `_rollback(conn)` de undo.py:131 (`_run`) | 3 failed: test_falha_com_update_sem_commit..., test_segundo_desfazer..., test_falha_so_na_segunda_gravacao... |
| M2 | remove `_rollback(conn)` de undo.py:169 (`undo_last`) | 1 failed: test_falha_no_update_final_da_organizacao... (`in_transaction` True) |
| M3 | `_rollback` sem `contextlib.suppress` | 1 failed: test_conexao_fechada_na_falha... (`ProgrammingError`, undo.py:86) |
| M4 | move `_rollback(conn)` para DEPOIS do `os.rename` em `_run` | 385 passed: sobrevive; a ordem "antes do rename" da SPEC nao e observavel por comportamento (rename e rollback independentes), entra como observacao |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix2-1-f1 | Monkeypatch com UPDATE sem commit + OperationalError: BANCO_INDISPONIVEL, `in_transaction` False, arquivo em Documentos/a.pdf, status movido | PASS | tests/services/test_undo_rollback.py:65-80 (:74-75 e asserts de arquivo e status); undo.py:131 |
| filepilot-fix2-1-f1 | Com o monkeypatch desfeito, o segundo undo_last devolve restored_count 1, arquivo volta a folder/a.pdf, status restaurado, `last_undoable` None | PASS | test_undo_rollback.py:83-98 (:94, :98) |
| filepilot-fix2-1-f1 | Plano de 3 arquivos, falha so na segunda chamada: depois do segundo undo_last os tres arquivos estao nos originais e os tres status restaurado | PASS | test_undo_rollback.py:101-127 |
| filepilot-fix2-1-f1 | TRIGGER com RAISE(ABORT): BANCO_INDISPONIVEL, `in_transaction` False; sem gatilho, restored_count 0 e `last_undoable` None | PASS | test_undo_rollback.py:130-151 (:135, :142-143, :150-151); undo.py:169 |
| filepilot-fix2-1-f1 | `conn.close()` + OperationalError: BANCO_INDISPONIVEL sem ProgrammingError e arquivo em Documentos/a.pdf | PASS | test_undo_rollback.py:154-170; undo.py:86-87 |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | tests/services/test_undo_rollback.py | 65-127 | Desejavel: nenhum teste afirma que a organizacao NAO e marcada `desfeita` depois da falha de uma operacao (SPEC L1112) | Acrescentar uma leitura de `organizations.status` depois da falha, no teste 1 ou 2 | nao |
| 2 | filepilot/services/undo.py | 131 | Observacao: a ordem "rollback antes do os.rename" (SPEC L1111) sobrevive a mutacao M4 porque nao ha efeito observavel; nao e defeito | Nenhuma; manter o comentario como esta | nao |
| 3 | .gitignore (ausente) | - | Desejavel: o repositorio nao ignora `__pycache__/` nem `filepilot.egg-info/`; aparecem como nao rastreados | Commitar so undo.py e test_undo_rollback.py (o Ivan faz `git add` escopado) | nao |
