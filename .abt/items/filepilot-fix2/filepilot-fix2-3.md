# filepilot-fix2-3 - Instancia unica avisa quando nao consegue saber se ha outra janela aberta
Epico: filepilot-fix2 | Ordem: 3 | Pontos: 3 | Depende de: filepilot-v1-8

## Objetivo

Quando a trava de instancia unica falha por motivo diferente de LockFailedError, o programa mostra o texto de falha de acesso a pasta de dados e sai com 1, em vez de fechar em silencio com 0 como se ja houvesse outra janela aberta.

## Contexto herdado

-

## Features

### filepilot-fix2-3-f1 Falha da trava que nao e outra instancia vira erro de acesso
Linhas da SPEC: .abt/SPEC.md L1147-1168
Arquivos:
- filepilot/__main__.py L12-51
- tests/ui/test_single_instance_unknown.py (novo)
- tests/ui/test_single_instance.py L1-70
Criterios de aceite:
- Com app_main.QLockFile trocado por uma classe falsa cujo tryLock devolve False e cujo error devolve QLockFile.LockError.PermissionError, open_main_window(tmp_path) devolve 1, QMessageBox.critical recebe "Não foi possível verificar se o FilePilot já está aberto. Confira se você tem permissão para usar a pasta de dados do aplicativo." e QMessageBox.information nao e chamado.
- O mesmo com QLockFile.LockError.UnknownError devolve 1 e chama critical com o mesmo texto; nos dois casos a janela nao e criada e filepilot.db nao existe em tmp_path.
- Com a classe falsa devolvendo QLockFile.LockError.LockFailedError, open_main_window devolve 0, information recebe "O FilePilot já está aberto." e critical nao e chamado.
- Com a pasta de dados em chmod 0o500 e a trava real, open_main_window devolve 1 e critical recebe o texto de _LOCK_UNAVAILABLE; o teste faz pytest.skip no Windows e quando a permissao e ignorada (por exemplo sob root) e desfaz o chmod num finally.
- tests/ui/test_single_instance.py passa sem nenhuma alteracao.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/ui/test_single_instance_unknown.py tests/ui/test_single_instance.py -> exit 0
- parser: python -m py_compile filepilot/__main__.py -> exit 0
- grep deve casar: LockFailedError em filepilot/__main__.py
- grep deve casar: _LOCK_UNAVAILABLE em filepilot/__main__.py
- grep deve casar: pasta de dados do aplicativo em filepilot/__main__.py
- grep deve casar: pasta de dados do aplicativo em tests/ui/test_single_instance_unknown.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/__main__.py
Dicas:
- Hoje open_main_window (__main__.py L43-45) trata todo tryLock(0) falso como "outra instancia aberta": mostra a informacao e devolve 0. O QLockFile devolve falso tambem quando nao consegue criar ou ler o arquivo de trava; lock.error() distingue LockFailedError (outro processo segura a trava), PermissionError (sem acesso a pasta ou ao arquivo) e UnknownError (outra falha, como disco cheio).
- Confirmar que QLockFile.error() e QLockFile.LockError existem na versao instalada do PySide6 (6.12.0, pyproject.toml) antes de usar; mypy precisa do tipo correto, use QLockFile.LockError.LockFailedError.
- Depois do tryLock falso, leia lock.error() uma unica vez: LockFailedError mantem o comportamento atual (QMessageBox.information com _ALREADY_OPEN e retorno 0); qualquer outro valor chama QMessageBox.critical(None, APP_NAME, _LOCK_UNAVAILABLE) e devolve 1. Em ambos, nao crie MainWindow, nao abra o banco e nao chame lock.unlock() (a trava nao foi tomada).
- Defina _LOCK_UNAVAILABLE = "Não foi possível verificar se o FilePilot já está aberto. Confira se você tem permissão para usar a pasta de dados do aplicativo." ao lado de _ALREADY_OPEN e _DB_UNAVAILABLE (L17-18). Os textos do banco e da falha de mkdir (L36-40) ficam como estao.
- Padrao de teste: tests/ui/test_single_instance.py L22-70 (InfoSpy, _forbid_window, monkeypatch de app_main.QLockFile em L99-116). Acrescente um espiao equivalente para app_main.QMessageBox.critical. A classe falsa precisa de setStaleLockTime, tryLock, error e unlock.
- Para o teste de permissao, antes de afirmar, confira que a permissao nao e ignorada: uma QLockFile de teste na mesma pasta com tryLock(0) verdadeiro significa permissao ignorada, entao libere com unlock() e use pytest.skip.
- Fora de escopo (SPEC 37.4): nao altere o mkdir da pasta de dados, o tempo de trava velha nem a falha de open_connection.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix2/*.md
```
