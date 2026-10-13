# Validacao do item filepilot-fix3-5 - Historico mostra a data como veio quando ela e invalida

**Item:** filepilot-fix3-5 | **Epico:** filepilot-fix3 | **Data:** 2026-10-13
Execucao: 20261013-174647
Veredito: APROVADO
**Tipo do item:** backend (correcao de logica pura em `format_local_time`, sem widget, layout nem texto novo; os testes de interface rodam por pytest-qt)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot tests/ui/test_history_invalid_date.py` exit 0, 26 arquivos; zero erro novo contra a baseline (exit 0) |
| 2 Criterios de aceite | PASS | 6/6 atendidos, 0 NAO VERIFICAVEL |
| 3 Qualidade de codigo | PASS | zero TODO/placeholder/FIXME; sem `asyncio.new_event_loop`; sem caractere Unicode proibido; `OverflowError` casa em history_tab.py:65 |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint; sem efeito no disco nem no banco |
| 5 Testes | PASS | suite completa 509 passed, 2 skipped (so Windows, history_tab nao depende deles); mutacoes refeitas |
| 6 Consistencia entre documentos | PASS | SPEC L1279-1290 conferida contra o diff: captura `(ValueError, OverflowError, OSError)`, devolve `started_at`, 4 testes obrigatorios cobertos |
| 7b Varredura adversarial | PASS | nenhuma coluna nova; `format_local_time` tem um unico consumidor (`_organization_cells`, history_tab.py:115); sem utilitario duplicado |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim": antes o `OverflowError` subia do slot, agora devolve o texto; a conversao e o `strftime` ficam dentro do `try`, so ha o retorno do texto original; comentario e docstring continuam verdadeiros |
| 7d Matriz (backend) | PASS | BE-1 a BE-3 n/a (sem service nem endpoint novo; sem registro de dependencia) |
| 7e Funcao irma e comando citado | PASS | nenhuma divergencia: `format_local_time` nao grava estado; nenhuma mensagem nova manda rodar comando |

Gate UI-1: n/a. O FilePilot e um aplicativo de desktop PySide6, a skill de smoke e de navegador, e o item nao muda widget, layout nem texto: o carregamento da aba com a data invalida e coberto por `test_pagina_com_data_invalida_carrega_as_duas_organizacoes` (pytest-qt). A decisao de nao deferir o smoke e minha e esta registrada para a pessoa revisar no ponto de checagem.

Skills de stack ignoradas por nao serem do projeto: optimizing-ef-core-queries, run-tests (.NET), test-anti-patterns (.NET), coverage-analysis (.NET), vuetify-sneat-ui-patterns, go-senior-engineer. Memoria: 0 resultados.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix3-5-f1 | `format_local_time("0001-01-01T00:00:00Z")` devolve o texto sem levantar | PASS | filepilot/ui/history_tab.py:62-66; tests/ui/test_history_invalid_date.py:60-61 (falha sem `OverflowError` na mutacao) |
| filepilot-fix3-5-f1 | data valida continua no formato `dd/MM/yyyy HH:mm` e `"ontem"` continua `"ontem"` | PASS | history_tab.py:64; tests/ui/test_history_invalid_date.py:88-93 e tests/ui/test_history_tab.py:112-127 sem alteracao |
| filepilot-fix3-5-f1 | `ValueError`, `OverflowError` e `OSError` na conversao devolvem o `started_at` | PASS | history_tab.py:65-66; mutacoes sem `OSError` ou sem `OverflowError` reprovam testes |
| filepilot-fix3-5-f2 | `pytest tests/ui/test_history_invalid_date.py` exit 0 com os quatro testes de 45.2 | PASS | tests/ui/test_history_invalid_date.py:60, 64, 70 e 88; pytest completo exit 0 |
| filepilot-fix3-5-f2 | duas organizacoes: `reload()` nao levanta, `rowCount() == 2`, primeira celula local da data valida, segunda `"0001-01-01T00:00:00Z"` | PASS | tests/ui/test_history_invalid_date.py:70-83 |
| filepilot-fix3-5-f2 | `status_label.text() == ""` e `retry_button` escondido | PASS | tests/ui/test_history_invalid_date.py:84-85 |

## Mutacoes refeitas por Rita (escopo: suite inteira, 509 testes; reversao por copia de arquivo)

| # | Diff em history_tab.py:65 | Resultado |
|---|---------------------------|-----------|
| 1 | `-except (ValueError, OverflowError, OSError):` `+except ValueError:` | 3 failed, 506 passed (os tres testes novos de data invalida) |
| 2 | `+except (ValueError, OverflowError):` | 1 failed, 508 passed (`test_oserror_na_conversao_devolve_a_data_como_esta`) |
| 3 | `+except (ValueError, OSError):` | 2 failed, 507 passed (`test_data_no_ano_1_aparece_como_esta` e `test_pagina_com_data_invalida_carrega_as_duas_organizacoes`) |

Fim das mutacoes: `git status --short` e `git diff --stat` iguais aos do inicio, sem `.bak`.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| - | nenhum | - | nenhum achado | - | nao |
