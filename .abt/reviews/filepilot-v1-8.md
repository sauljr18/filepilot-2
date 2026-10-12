# Validacao do item filepilot-v1-8 - Janela principal, abas e instancia unica

**Item:** filepilot-v1-8 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-115645
Veredito: APROVADO - Gate UI-1 DEFERIDO (smoke ao vivo pendente)
Transicoes a cobrir no smoke: aba Organizar -> Historico, aba Organizar -> Regras, janela aberta com organizing=False -> fechada (conexao fechada e trava liberada), janela aberta com organizing=True -> fechamento bloqueado com aviso, segunda abertura com a trava tomada -> aviso e saida 0, banco inacessivel -> erro critico e saida 1
**Tipo do item:** interface

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, 19 arquivos, zero erros; baseline (exit 0, 16 arquivos, zero erros) sem diferenca em erros |
| 2 Criterios de aceite | PASS | 7/7 criterios atendidos |
| 3 Qualidade de codigo | PASS | zero TODO/FIXME/not implemented; zero print; gate Unicode sem casamento; a classe `PlaceholderTab` (main_window.py:27) so casa `placeholder` sem diferenciar maiusculas e e o marcador de posicao que o detalhe do item manda criar |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint, nenhuma entrada externa alem do caminho da pasta de dados |
| 5 Testes | PASS | `pytest tests/ui` 17 passed; suite completa 318 passed, 2 skipped (os dois so valem no Windows); 6 mutacoes independentes, 5 detectadas e 1 equivalente (ver correcao 2) |
| 6 Consistencia entre documentos | PASS | titulo, abas e as tres mensagens batem caractere a caractere com SPEC.md L426, L427 e L432; `db_path`, `conn` e `organizing` com os nomes e tipos de 7.1 |
| 7b Varredura adversarial | PASS | sem entidade com CRUD anterior; sem utilitario reinventado; a mensagem de banco repete a literal que o repositorio ja repete em db/connection.py:10, history.py:15, rules.py:15 |
| 7c Degradacao e borda | PASS | 1 "sim" (correcao 1), nao decide o veredito |
| 7d Matriz (interface) | DEFERIDO | UI-1 deferido ao Ivan; UI-2 e UI-3 n/a (a janela so contem abas, SPEC L429); UI-4 listado em `Transicoes a cobrir no smoke` |
| 7e Funcao irma e comando citado | PASS | nenhuma divergencia; nenhuma mensagem manda rodar comando |

Observacao sobre o smoke: a skill `smoke-e2e-playwright` do Ivan trata de interface web, e este projeto e um aplicativo desktop PySide6. Cabe a pessoa decidir, no ponto de checagem, se o smoke ao vivo (abrir `python -m filepilot` no Windows) sera manual.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-8-f1 | `MainWindow` com titulo "FilePilot" e `QTabWidget` com "Organizar", "Histórico", "Regras", nesta ordem | PASS | filepilot/ui/main_window.py:13,14,54,55-57; tests/ui/test_main_window.py:25 |
| filepilot-v1-8-f1 | `organizing` comeca `False` e `conn` aberta por `open_connection` | PASS | filepilot/ui/main_window.py:50,53; tests/ui/test_main_window.py:38 |
| filepilot-v1-8-f1 | trocar para Historico ou Regras recarrega a aba (`currentChanged`) | PASS | filepilot/ui/main_window.py:17,58,61-66; tests/ui/test_main_window.py:59,76; mutacao M1 derruba 2 testes |
| filepilot-v1-8-f2 | trava `QLockFile` em `filepilot.lock` antes do banco; tomada: aviso "O FilePilot já está aberto.", saida 0, sem janela e sem banco | PASS | filepilot/__main__.py:41,43-45,17; tests/ui/test_single_instance.py:44,59; mutacao M4 derruba os 2 testes |
| filepilot-v1-8-f2 | trava liberada no `closeEvent`; trava velha recuperada (`setStaleLockTime`) | PASS | filepilot/ui/main_window.py:74-75; filepilot/__main__.py:16,42; tests/ui/test_single_instance.py:86,99,119; mutacao M3 derruba 2 testes |
| filepilot-v1-8-f3 | `closeEvent` com `organizing` ignora e avisa; sem organizacao fecha a conexao, libera a trava e aceita | PASS | filepilot/ui/main_window.py:68-76,15; tests/ui/test_close_and_db_error.py:33,53; mutacoes M2 e M3 |
| filepilot-v1-8-f3 | falha em `open_connection` mostra `QMessageBox.critical` com a mensagem e sai com codigo 1 | PASS | filepilot/__main__.py:46-51,18; tests/ui/test_close_and_db_error.py:70,87,103,116; mutacao M6 derruba 2 testes |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/__main__.py | 43 | `tryLock(0)` falso por qualquer causa (por exemplo, sem permissao de escrita na pasta de dados) mostra "O FilePilot já está aberto." e sai com 0, sem dizer o motivo real | Conferir `lock.error()`: so `QLockFile.LockError.LockFailedError` e "ja aberto"; os demais erros seguem o caminho de banco inacessivel | nao |
| 2 | tests/ui/test_single_instance.py | 99 | `test_define_o_tempo_de_trava_velha` nao distingue a chamada de `setStaleLockTime`: 30 000 ms e o padrao do Qt, e a mutacao M5 (remover a chamada) passou com 17 testes verdes; a recuperacao do teste da linha 119 vem do PID morto | Usar um valor diferente do padrao na constante e no teste, ou aceitar o teste como documentacao | nao |
| 3 | filepilot/__main__.py | 54-61 | `main()` e `default_data_dir()` sem teste; a ordem `setApplicationName` (linha 56) antes de `default_data_dir()` (linha 57) define a pasta de dados e nada a protege | Teste com `QApplication` offscreen e `XDG_DATA_HOME` em `tmp_path` conferindo que o caminho termina em `FilePilot` | nao |

Evidencia das mutacoes (por copia de arquivo, suite `tests/ui`, 17 testes; `git status` identico ao de antes):

| Mutacao | Diff | Resultado |
|---|---|---|
| M1 | main_window.py:17 `(1, 2)` -> `()` | 2 falham |
| M2 | main_window.py:71 `event.ignore()` -> `event.accept()` | 1 falha |
| M3 | main_window.py:75 `self._lock.unlock()` -> `pass` | 2 falham |
| M4 | __main__.py:43 `if not lock.tryLock(0):` -> `if lock.tryLock(0) and False:` | 2 falham |
| M5 | __main__.py:42 `lock.setStaleLockTime(...)` -> `pass` | 0 falham (equivalente, correcao 2) |
| M6 | __main__.py:51 `return 1` -> `return 0` | 2 falham |
