# Validacao do item filepilot-fix3-7 - Testes de instancia unica e desfazer falham em vez de travar

**Item:** filepilot-fix3-7 | **Epico:** filepilot-fix3 | **Data:** 2026-10-13
Execucao: 20261013-182324
Veredito: APROVADO
**Tipo do item:** refatoracao (infraestrutura de teste, sem tela, sem endpoint, sem dados)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot tests/conftest.py tests/test_no_modal_dialogs.py tests/ui/test_single_instance.py`: exit 0, "no issues found in 28 source files"; baseline (26 arquivos) tambem sem erro; zero erros novos |
| 2 Criterios de aceite | PASS | 8/8 atendidos, 0 NAO VERIFICAVEL |
| 3 Qualidade de codigo | PASS | zero TODO/placeholder/FIXME, zero bloco comentado, zero print, zero aspa ou travessao tipografico nos 3 arquivos |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint novo ou alterado |
| 5 Testes | PASS | `pytest` completo: 524 passed, 2 skipped (exit 0), 3,14 s; os 2 skips sao de plataforma, fora do item (tests/services/test_destination_checks.py:153 junction so existe no Windows; tests/services/test_scanner_protected.py:185 so vale no Windows); mutacoes refeitas por mim (abaixo) |
| 6 Consistencia entre documentos | PASS | SPEC L1360-1372: fixture `_no_modal_dialogs` autouse nos 4 metodos, mensagem `caixa de dialogo inesperada (<nome>): <titulo>: <texto>`, helper `_hold_lock(qtbot, lock_path) -> subprocess.Popen[str]`, `_HOLD_LOCK` sem `locked`, e os 5 testes obrigatorios existem; nomes batem com o `## Contexto herdado` |
| 7b Varredura adversarial | PASS | nenhuma coluna ou propriedade nova; nenhum utilitario reinventado (o helper substitui o `stdout.readline` no unico ponto que o usava) |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim" que decida; 3 observacoes desejaveis abaixo |
| 7d Matriz (refatoracao) | PASS | RF-1 suite completa verde (524 passed); unico teste existente alterado: `test_trava_velha_de_processo_que_caiu_e_recuperada` (L141-159), por exigencia da SPEC L1363; RF-2 `grep -rn "'locked'"` e `"locked"` em tests e filepilot: zero; RF-3 o teste de trava velha chama `_hold_lock` (L145) |
| 7e Funcao irma e comando citado | PASS | nenhuma funcao de service nova; nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix3-7-f1 | Com `qapp`, `QMessageBox.critical(None, "t", "x")` levanta `AssertionError` com `caixa de dialogo inesperada` em vez de bloquear | PASS | tests/test_no_modal_dialogs.py:51-53 e tests/conftest.py:11, 23-24; rodado: passa |
| filepilot-fix3-7-f1 | Com `qapp` e `QLockFile` falso devolvendo `LockFailedError`, sem espiao, `open_main_window(tmp_path)` levanta `AssertionError` | PASS | tests/test_no_modal_dialogs.py:24-40 (falso) e 64-70 |
| filepilot-fix3-7-f1 | Com `OrganizeTab(conn)`, `tab._on_failed("ERRO_INTERNO", "x")` tambem levanta | PASS | tests/test_no_modal_dialogs.py:73-80; filepilot/ui/organize_tab.py:345 |
| filepilot-fix3-7-f1 | Espiao por `monkeypatch.setattr` recebe a chamada e nao levanta | PASS | tests/test_no_modal_dialogs.py:83-91 |
| filepilot-fix3-7-f1 | `pytest` termina com exit 0: os testes de hoje e os dos itens novos | PASS | 524 passed, 2 skipped, exit 0 (rodado por mim) |
| filepilot-fix3-7-f2 | `tests/ui/test_single_instance.py` nao contem `holder.stdout.readline` | PASS | `grep -n "stdout.readline"`: zero linhas |
| filepilot-fix3-7-f2 | `_hold_lock(qtbot, lock_path)` espera com `qtbot.waitUntil(..., timeout=10_000)` ate `getLockInfo()[0]` e falha com `AssertionError` se `holder.poll()` deixar de ser `None` | PASS | tests/ui/test_single_instance.py:37-57 (espera L49, `getLockInfo` L45, `AssertionError` L50) |
| filepilot-fix3-7-f2 | `test_filho_que_nao_trava_falha_em_vez_de_travar` com `_HOLD_LOCK` = `"import sys; sys.exit(3)"` falha com `AssertionError` ou `TimeoutError` em menos de 15 s; o teste de trava velha usa o helper | PASS | tests/ui/test_single_instance.py:162-168 (passa em menos de 1 s: o filho que morre encerra a espera) e :145 |

## Mutacoes (refeitas por mim; escopo declarado; revertidas por copia de arquivo)

| # | Mutacao (diff) | Escopo | Resultado |
|---|----------------|--------|-----------|
| A | tests/conftest.py:23 `for name in _DIALOGS:` -> `for name in ():` (fixture desligada) | `pytest -v -x tests/test_no_modal_dialogs.py::test_on_failed_sem_espiao_levanta` | TRAVA no dialogo real; `timeout -s INT -k 20 40` precisou do KILL (exit 137): e o travamento que a fixture evita |
| B | tests/ui/test_single_instance.py:49 linha `qtbot.waitUntil(locked_or_dead, timeout=10_000)` removida | `pytest -q tests/ui/test_single_instance.py` | 2 failed, 5 passed: `test_filho_que_nao_trava_falha_em_vez_de_travar` ("DID NOT RAISE any of (AssertionError, TimeoutError)") e `test_trava_velha_de_processo_que_caiu_e_recuperada` |

No fim: `git status --short` (` M tests/ui/test_single_instance.py`, `?? tests/conftest.py`, `?? tests/test_no_modal_dialogs.py`) e `git diff --stat` (1 file changed, 33 insertions(+), 10 deletions(-)) iguais aos de antes das mutacoes; os `.bak` foram removidos e `grep` confirma as linhas originais.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/ui/rules_tab.py | 252-266 | Desejavel: a fixture cobre so os 4 metodos estaticos de `QMessageBox`; `QMessageBox(...).exec()` (L266), `dialog.exec()` (L243) e `QFileDialog.getExistingDirectory` (organize_tab.py:240) continuam podendo bloquear um teste que nao tenha espiao. Fora do escopo da SPEC L1362 | Se a pessoa quiser, um item novo estende a fixture a esses pontos | nao |
| 2 | tests/conftest.py | 10 | Desejavel: a funcao proibida nao aceita `**kwargs`; chamada com argumento nomeado levanta `TypeError` em vez de `AssertionError` (continua falhando sem travar) | Acrescentar `**kwargs: object` se o projeto passar a chamar os dialogos com argumento nomeado | nao |
| 3 | tests/ui/test_single_instance.py | 162-168 | Desejavel: o teste nao mede os 15 s do criterio; o limite vem do `timeout=10_000` do `waitUntil` (L49) e a medicao real foi de menos de 1 s | Opcional: assert do tempo decorrido com `time.monotonic()` | nao |

Observacao de ambiente: a verificacao usou o venv do projeto `$HOME/.cache/abt-venvs/filepilot-2` (so dependencias declaradas, sem o pacote do projeto instalado; `pip show filepilot` fora da area falha), em vez de criar outro venv; nada foi instalado e nada foi gravado na arvore alem deste relatorio.
