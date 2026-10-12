# Validacao do item filepilot-fix2-4 - Planejamento com laco de atalhos vira PASTA_INVALIDA

**Item:** filepilot-fix2-4 | **Epico:** filepilot-fix2 | **Data:** 2026-10-12
Execucao: 20261012-154517
Veredito: APROVADO
**Tipo do item:** backend + refatoracao (rename scanner._resolve_folder -> resolve_folder); sem tela nova, so teste de interface

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | mypy --platform win32 filepilot: exit 0, 23 arquivos, `comm` contra a baseline sem erro novo |
| 2 Criterios de aceite | PASS | 8/8 criterios atendidos (f1: 5, f2: 3 contando o criterio de arquivo proprio) |
| 3 Qualidade de codigo | PASS | zero TODO/placeholder/not implemented/FIXME e zero print nos 4 arquivos do diff; zero caractere Unicode proibido em planner.py |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint; a mensagem de PASTA_INVALIDA e o texto fixo, nunca o da excecao |
| 5 Testes | PASS | pytest completo 402 passed, 2 skipped (os 2 so valem no Windows, justificados no proprio skip); mutacoes refeitas |
| 6 Consistencia entre documentos | PASS | SPEC L1169-1194 conferida: nomes, mensagem, codigo e escopo batem; testes 1-8 da SPEC cobertos |
| 7b Varredura adversarial | PASS | `_inside` tem 2 consumidores fora de Arquivos (organizer.py:88, destination_checks.py:59); nenhum reinventa utilitario |
| 7c Degradacao e borda | FAIL (nao decide) | 1 achado: ver correcao 1 |
| 7d Matriz (backend, refatoracao) | PASS | BE-1: `grep -rn "_resolve_folder" filepilot tests` = zero; BE-2/BE-3 n/a (sem DI nem policy); RF-1 suite completa verde, nenhum teste existente alterado; RF-2 zero chamada orfa; RF-3 n/a |
| 7e Funcao irma e comando citado | PASS | `_inside` reutiliza `resolve_folder` do scanner (nao duplica); nenhuma mensagem cita comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix2-4-f1 | RuntimeError("Symlink loop") so para folder/Documentos/a.pdf: build_plan levanta FilePilotError PASTA_INVALIDA, mensagem fixa, sem Symlink loop | PASS | tests/services/test_planner_loop.py:57-63; filepilot/services/planner.py:50; filepilot/services/scanner.py:52-57 |
| filepilot-fix2-4-f1 | OSError ELOOP vira PASTA_INVALIDA; EACCES continua OSError | PASS | tests/services/test_planner_loop.py:73-78 e :88-92; scanner.py:58-61 |
| filepilot-fix2-4-f1 | Laco real em folder/Documentos da PASTA_INVALIDA e a arvore fica identica | PASS | tests/services/test_planner_loop.py:102-107 |
| filepilot-fix2-4-f1 | Laco real em folder/Imagens com a.pdf devolve o plano para Documentos sem erro; destino fora continua DESTINO_FORA_DA_PASTA | PASS | tests/services/test_planner_loop.py:118-120 e :135-138; planner.py:70-77 so resolve o destino de arquivo com alvo |
| filepilot-fix2-4-f1 | test_scanner_loop.py e test_planner_guard.py passam sem alteracao | PASS | `git diff HEAD --stat` desses arquivos vazio; 37 passed no conjunto da Verificacao |
| filepilot-fix2-4-f2 | resolve com RuntimeError so para folder/Documentos/a.pdf: tab.choose_folder() leva tab.mode a erro | PASS | tests/ui/test_organize_tab_plan_loop.py:65 |
| filepilot-fix2-4-f2 | tab.summary.text() e exatamente "A pasta escolhida não existe ou não é uma pasta." | PASS | tests/ui/test_organize_tab_plan_loop.py:66 |
| filepilot-fix2-4-f2 | Arquivo proprio: nao importa nem depende de test_organize_tab_read_error | PASS | grep de test_organize_tab_read_error no arquivo: zero; helpers copiados nas linhas 15-48 |

## Mutacoes refeitas pela Rita (escopo: suite inteira, 402 testes; reversao por copia de arquivo)

| # | Diff | Resultado |
|---|------|-----------|
| M1 | planner.py:50 `resolve_folder(destination).is_relative_to(resolve_folder(folder))` -> `destination.resolve().is_relative_to(folder.resolve())` | 4 failed, 398 passed (3 em test_planner_loop.py e 1 em test_organize_tab_plan_loop.py) |
| M2 | scanner.py:57 `raise _error("PASTA_INVALIDA") from exc` -> `raise` | 5 failed, 397 passed (2 em test_planner_loop.py, 2 em test_scanner_loop.py, 1 na aba) |
| M3 | planner.py: resolver `folder / categoria.folder` de todas as categorias antes do laco | 1 failed, 401 passed (test_laco_real_em_subpasta_que_nenhum_arquivo_usa_nao_impede_o_plano) |

Reconciliacao com o Carlos: a M1 dele deu 3 failed, 398 passed porque foi medida antes de existir o teste da aba; com o teste da aba (f2) o mesmo mutante falha 4, como medido aqui. Sem divergencia. Apos reverter: arquivos identicos aos copiados, 402 passed, `git status --short` e `git diff --stat` iguais aos do inicio.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/services/organizer.py e filepilot/services/destination_checks.py | 88 e 59 | Consumidores de `_inside` fora de Arquivos: se um laco surgir depois do planejamento, a execucao passa a levantar FilePilotError PASTA_INVALIDA em vez de RuntimeError dentro de `_move_file`, e `organize` nao captura nenhum dos dois (fraqueza antiga, agora com excecao tipada). Hoje nao ha caller de `organize` na interface (item filepilot-v1-10) | Ao ligar a execucao na aba (filepilot-v1-10), capturar FilePilotError em `_move_file`/`organize` e contar como falha do arquivo; fora de escopo deste item (SPEC 37.6 so exclui o desfazer) | nao |
