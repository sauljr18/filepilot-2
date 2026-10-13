# filepilot-fix3-7 - Testes de instancia unica e desfazer falham em vez de travar
Epico: filepilot-fix3 | Ordem: 7 | Pontos: 4 | Depende de: filepilot-fix2-3,filepilot-v1-11

## Objetivo

Nenhum teste de instancia unica ou do botao de desfazer bloqueia a suite por causa de um dialogo real ou de uma leitura sem limite de tempo: o comportamento errado faz o teste falhar em ate 15 segundos.

## Contexto herdado

Artefatos criados por filepilot-fix3-6 (commit 80cf4e3):
- filepilot/ui/organize_tab.py - modulo - `OrganizeTab.undo` passa a chamar `self.progress.setVisible(False)` (L357), depois das guardas de `_undoable` e `_db_path` e antes de criar o `UndoWorker`.
- tests/ui/test_undo_progress.py - testes - seis testes da barra de progresso ao desfazer, com `_window`, `_organize`, `_undo` e `_MessageSpy` copiados de tests/ui/test_undo_button.py (em tests/ui/test_undo_progress.py L46-84).

Contratos:
- `OrganizeTab.undo()` e `OrganizeTab._on_failed(code, message)` em filepilot/ui/organize_tab.py: sem mudanca de assinatura. `_on_failed` (L338-345) continua chamando `QMessageBox.critical` e nao muda aqui. Armadilha: o `setVisible(False)` do `undo` fica depois das guardas; nao o mova para antes delas.

Padroes estabelecidos:
- Nos testes de interface, a visibilidade da barra e lida com `isHidden()`, que nao depende de a janela estar mostrada, e todo teste que prova o sumico roda `_organize` antes (tests/ui/test_undo_progress.py L86-98).
- Para provar o estado no meio do desfazer, o `undo_last` e trocado por `monkeypatch` por uma funcao lenta que espera um `threading.Event`, e o teste solta o evento dentro de `qtbot.waitSignal(tab.organizing_changed, ...)` (tests/ui/test_undo_progress.py L101-128).

filepilot-fix3-6 entregou a barra escondida ao desfazer e NAO toca em filepilot/__main__.py nem em tests/ui/test_single_instance.py: NAO reimplemente `OrganizeTab.undo` aqui.

## Features

### filepilot-fix3-7-f1 Dialogos reais proibidos nos testes por uma fixture autouse
Linhas da SPEC: .abt/SPEC.md L1360-1364
Arquivos:
- tests/conftest.py (novo)
- tests/test_no_modal_dialogs.py (novo)
- filepilot/__main__.py L37-52
- filepilot/ui/organize_tab.py L338-345
Criterios de aceite:
- Com `qapp`, `QMessageBox.critical(None, "t", "x")` levanta `AssertionError` com `caixa de dialogo inesperada` em vez de bloquear.
- Com `qapp` e `QLockFile` falso devolvendo `LockFailedError`, sem espiao, `app_main.open_main_window(tmp_path)` levanta `AssertionError`; com `OrganizeTab(conn)`, `tab._on_failed("ERRO_INTERNO", "x")` tambem.
- Um teste que troca o metodo por um espiao com `monkeypatch.setattr` recebe a chamada e nao levanta: a fixture nao impede o espiao.
- `pytest` termina com exit 0: os 465 testes de hoje e os dos itens novos.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/conftest.py tests/test_no_modal_dialogs.py -> exit 0
- testes: pytest tests/test_no_modal_dialogs.py -> exit 0
- grep deve casar: autouse em tests/conftest.py
- grep deve casar: caixa de dialogo inesperada em tests/conftest.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/conftest.py
Dicas:
- Medicao desta especificacao: um teste com `qapp` que chama `open_main_window` com `QLockFile` falso e sem espiao nao termina (o `timeout 15` do shell o encerra com saida 124); sem `QApplication` aborta com saida 134.
- A fixture troca `QMessageBox.information`, `.warning`, `.critical` e `.question` por funcoes que levantam `AssertionError("caixa de dialogo inesperada (nome): titulo: texto")`; os testes existentes que usam espiao (`tests/ui/test_single_instance_unknown.py` L21-35) trocam o metodo depois e vencem a fixture.
- Contrato: `open_main_window` em `filepilot/__main__.py` L37-52 chama `QMessageBox.information` e `.critical`; `OrganizeTab._on_failed` em `organize_tab.py` L338-345 chama `QMessageBox.critical`. Nenhum dos dois muda.
- Regra de 45.7: fixture com yield nos arquivos novos e anotada `Iterator[tipo]`.

### filepilot-fix3-7-f2 Processo filho da trava com limite de tempo
Linhas da SPEC: .abt/SPEC.md L1363-1372
Arquivos:
- tests/ui/test_single_instance.py L1-20
- tests/ui/test_single_instance.py L119-145
Criterios de aceite:
- `tests/ui/test_single_instance.py` nao contem `holder.stdout.readline`.
- O helper `_hold_lock(qtbot, lock_path)` espera com `qtbot.waitUntil(..., timeout=10_000)` ate `QLockFile(lock_path).getLockInfo()[0]` ser verdadeiro e falha com `AssertionError` se `holder.poll()` deixar de ser `None` antes disso.
- `test_filho_que_nao_trava_falha_em_vez_de_travar`, com `_HOLD_LOCK` trocado por `"import sys; sys.exit(3)"`, falha com `AssertionError` ou `pytestqt.exceptions.TimeoutError` em menos de 15 s.
- `pytest tests/ui/test_single_instance.py` termina com exit 0 e `test_trava_velha_de_processo_que_caiu_e_recuperada` usa o helper.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/ui/test_single_instance.py -> exit 0
- testes: pytest tests/ui/test_single_instance.py tests/ui/test_single_instance_unknown.py tests/ui/test_undo_button.py -> exit 0
- grep nao deve casar: stdout.readline em tests/ui/test_single_instance.py
- grep deve casar: getLockInfo em tests/ui/test_single_instance.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/ui/test_single_instance.py
Dicas:
- Medicao desta especificacao (Linux): `QLockFile.getLockInfo()` devolve `(pid, hostname, appname)` quando o filho segura a trava, em 0,1 s, e `(0, '', '')` quando nao ha trava; por isso o indice 0 e falso ate o filho escrever o pid.
- Padrao a seguir: `tests/ui/test_single_instance.py` L119-145 (o teste atual de trava velha) e L12-19 (`_HOLD_LOCK`, que deixa de imprimir `locked`).
- `pytestqt.exceptions.TimeoutError` herda de `Exception` e nao do `TimeoutError` embutido (medido nesta especificacao): use `pytest.raises((AssertionError, TimeoutError))` com o `TimeoutError` importado de `pytestqt.exceptions`.
- Confirmar que `QLockFile.getLockInfo` existe no PySide6 6.12.0 instalado (existe: medido).
- Regra de 45.7: fixture com yield em teste alterado e anotada `Iterator[tipo]`.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests/conftest.py tests/test_no_modal_dialogs.py tests/ui/test_single_instance.py -> exit 0 (o comando completo de 45.7 so passa depois do item filepilot-fix3-1)
- testes: pytest -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix3/*.md
```
