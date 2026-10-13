# Validacao do item filepilot-fix3-6 - Barra de progresso some ao desfazer a organizacao

**Item:** filepilot-fix3-6 | **Epico:** filepilot-fix3 | **Data:** 2026-10-13
Execucao: 20261013-180057
Veredito: APROVADO - Gate UI-1 DEFERIDO (smoke ao vivo pendente)
Transicoes a cobrir no smoke: organizado -> desfazendo (barra escondida ao comecar), desfazendo -> listado (desfeito, barra continua escondida), desfazendo -> listado (falha, barra continua escondida), listado -> organizando (barra volta e termina cheia)
**Tipo do item:** interface

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `mypy --platform win32 filepilot tests/ui/test_undo_progress.py` exit 0, "no issues found in 26 source files"; `comm -13` contra a baseline do Carlos sem erro novo |
| 2 Criterios de aceite | PASS | 8/8 atendidos, 0 NAO VERIFICAVEL |
| 3 Qualidade de codigo | PASS | grep de TODO/placeholder/not implemented/FIXME, aspas tipograficas e `print(` sem ocorrencia nos dois arquivos do diff; `asyncio.new_event_loop` sem ocorrencia |
| 4 Autorizacao e seguranca | PASS | nenhum endpoint novo ou alterado (n/a) |
| 5 Testes | PASS | suite inteira `515 passed, 2 skipped`, exit 0; os 2 skips sao de plataforma (`tests/services/test_destination_checks.py:153` e `tests/services/test_scanner_protected.py:185`), fora dos criterios do item; mutacoes refeitas por mim (ver abaixo) |
| 6 Consistencia entre documentos | PASS | codigo e testes batem com `.abt/SPEC.md` L1341-1354 e com `## Contexto herdado` (nenhum nome reimplementado) |
| 7b Varredura adversarial | PASS | sem coluna nova; helpers de teste copiados de `tests/ui/test_undo_button.py` por determinacao explicita da SPEC L1347 |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim" as 5 perguntas; achado de cobertura abaixo (nao decide) |
| 7d Matriz (interface) | DEFERIDO | UI-1 DEFERIDO; UI-2 e UI-3 n/a (nenhum componente novo); UI-4 listada em `Transicoes a cobrir no smoke:` |
| 7e Funcao irma e comando citado | PASS | `refresh`, `simulate` e `organize` escondem a barra no inicio (`organize_tab.py:251`, `:260`, `:269`); `undo` esconde depois das guardas (`:357`), divergencia prevista na SPEC L1342 `[DECISAO]`; nenhuma mensagem nova cita comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix3-6-f1 | Depois de organizar e desfazer, `isHidden()` e True; antes do desfazer, depois de organizar, e False com `value() == maximum()` | PASS | `tests/ui/test_undo_progress.py:93-98`; `filepilot/ui/organize_tab.py:357` |
| filepilot-fix3-6-f1 | Desfazer sem `_db_path` e com `_undoable is None` nao escondem a barra | PASS | guardas com `return` antes do `setVisible`: `organize_tab.py:352-356`; `_undoable is None` provado em `tests/ui/test_undo_progress.py:173-177`; `_db_path` None so por leitura (ver achado 1) |
| filepilot-fix3-6-f1 | A barra fica escondida nos desfechos de falha, porque o `setVisible(False)` roda no inicio | PASS | `organize_tab.py:357` roda antes de `UndoWorker` (`:358`); falha inesperada em `tests/ui/test_undo_progress.py:136-146` |
| filepilot-fix3-6-f1 | Nova organizacao depois do desfazer mostra a barra e termina com `value() == maximum()` | PASS | `tests/ui/test_undo_progress.py:186-190`; `organize_tab.py:298-300` inalterado |
| filepilot-fix3-6-f2 | `pytest tests/ui/test_undo_progress.py` termina com exit 0 e cobre os seis testes de 45.5 | PASS | 6 testes em `tests/ui/test_undo_progress.py:86,101,131,149,167,180`; suite inteira 515 passed |
| filepilot-fix3-6-f2 | Todo teste que prova o sumico roda `_organize` antes | PASS | `isHidden() is False` afirmado logo depois do `_organize` em `:93`, `:109`, `:136`, `:154`, `:186` (o ultimo, depois do segundo `_organize`) |
| filepilot-fix3-6-f2 | Guarda: `tab._undoable = None` depois de `_organize`, `tab.undo()`, barra continua visivel | PASS | `tests/ui/test_undo_progress.py:173-177` |
| filepilot-fix3-6-f2 | A visibilidade e lida com `isHidden()` | PASS | 13 ocorrencias de `isHidden` em `tests/ui/test_undo_progress.py`; grep deve casar: ok |

## Mutacoes refeitas (escopo: suite inteira, 517 testes; reversao por copia de arquivo)

| # | Diff da mutacao em `filepilot/ui/organize_tab.py` | Resultado |
|---|---------------------------------------------------|-----------|
| 1 | remove a linha 357 `self.progress.setVisible(False)` | 5 falhas, 510 passed, 2 skipped: os testes de `:86`, `:101`, `:131`, `:149`, `:180` |
| 2 | move o `setVisible(False)` para antes da guarda de `_undoable` (depois da linha 351) | 1 falha, 514 passed: o teste de `:167` (guarda) |
| 3 | move o `setVisible(False)` para antes da checagem de `_db_path` (depois da linha 353) | SOBREVIVE: 515 passed, 2 skipped |

No fim das mutacoes: `git status --short` e `git diff --stat` iguais aos do inicio (` M filepilot/ui/organize_tab.py`, `?? tests/ui/test_undo_progress.py`, 1 insercao).

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | tests/ui/test_undo_progress.py | 167 | Nenhum teste prova a metade do criterio "desfazer sem `_db_path` nao esconde a barra" (f1, criterio 2): a mutacao 3 sobrevive; o codigo esta correto por leitura (`organize_tab.py:354-357`) | Opcional: teste que cria `OrganizeTab(conn)` sem `db_path`, forca a barra visivel (`tab.progress.setVisible(True)`), clica em desfazer e confere que a barra continua visivel e o resumo e "Não foi possível acessar o histórico do FilePilot." | nao |
| 2 | filepilot/ui/organize_tab.py | 357 | Gate UI-1: o smoke da skill `smoke-e2e-playwright` e de navegador e este app e desktop PySide6; o smoke ao vivo pelo Ivan precisa de outro meio | A pessoa decide como cumprir o UI-1 (rodar o app e conferir as transicoes listadas) antes do commit | nao |
