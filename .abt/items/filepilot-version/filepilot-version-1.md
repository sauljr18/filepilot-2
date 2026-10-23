# filepilot-version-1 - Opcao --version imprime a versao e sai sem abrir a janela
Epico: filepilot-version | Ordem: 1 | Pontos: 1 | Depende de: -

## Objetivo

`python -m filepilot --version` imprime o `__version__` de `filepilot/__init__.py` seguido de quebra de linha e sai com codigo 0, sem criar a `QApplication`; qualquer outra lista de argumentos segue o caminho de hoje.

## Contexto herdado

-

## Features

### filepilot-version-1-f1 Desvio --version no inicio de main com testes
Âncoras da SPEC: 54.2=eba99aa67823, 54.1=08ed0d63bb9d
Arquivos:
- filepilot/__main__.py L1-12
- filepilot/__main__.py L62-73
- filepilot/__init__.py L1-3
- tests/test_import.py L1-5
- tests/test_version_cli.py (novo)
Criterios de aceite:
- `python -m filepilot --version` termina com codigo 0, a saida padrao e exatamente `filepilot.__version__ + "\n"` (hoje `0.1.0`) e a saida de erro fica vazia (teste 1 de 54.2).
- Com `sys.argv` igual a `["filepilot", "--version"]` e `QApplication`, `default_data_dir` e `open_main_window` trocados por funcoes que levantam `AssertionError`, `app_main.main()` devolve 0 e imprime so a versao; com `sys.stdout` igual a `None`, devolve 0 sem excecao (testes 2 e 5 de 54.2).
- Com `sys.argv` igual a `["filepilot"]` e a `["filepilot", "--version", "x"]`, `main()` cria a `QApplication` falsa uma vez, chama `open_main_window` falso uma vez e nao imprime nada na saida padrao (teste 3 de 54.2).
- `python -m mypy --platform win32 filepilot tests` termina com exit 0 e `Success: no issues found`, e `pytest` termina com exit 0.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest tests/test_version_cli.py tests/test_import.py -> exit 0
- smoke: python -m filepilot --version (timeout 30 s) -> exit 0
- grep deve casar: from filepilot import __version__ em filepilot/__main__.py
- grep deve casar: sys.argv\[1:\] == \["--version"\] em filepilot/__main__.py
- grep nao deve casar: argparse em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/test_version_cli.py
Dicas:
- O desvio e a primeira instrucao de `main()` (`filepilot/__main__.py` L62), antes de `app = QApplication(sys.argv)` (L63); o bloco exato esta em 54.2. A escrita e por `print(__version__)`, nunca `sys.stdout.write` (com `sys.stdout` `None`, `print` nao faz nada; `write` levantaria `AttributeError`).
- O import novo `from filepilot import __version__` entra no grupo de imports de `filepilot` (L9-10), sem mexer nas importacoes de PySide6 (L6-7) nem no docstring (L1).
- Nos testes em processo, importe o modulo como em `tests/ui/test_single_instance.py` (`from filepilot import __main__ as app_main`) e troque `sys.argv`, `app_main.QApplication`, `app_main.default_data_dir` e `app_main.open_main_window` por `monkeypatch.setattr`; `main()` le `sys.argv` na hora da chamada.
- O teste 3 precisa de um falso da `QApplication` com `setApplicationName` (L64) e conta quantas vezes foi criado; o falso de `open_main_window` devolve `0`, entao `main()` retorna em L66-67 sem chamar `app.exec()`.
- O teste 1 roda `python -m filepilot` em subprocesso com `sys.executable` e `timeout=30`; com `text=True`, o `\r\n` do Windows chega como `\n`. Sem `QApplication` o comando nao precisa de tela, inclusive no Linux sem `DISPLAY`.
- A `tests/conftest.py` proibe dialogos reais (45.6): o caminho `--version` nao mostra `QMessageBox`, e o teste 3 nao chega a `open_main_window` real.
- Regra de 45.7: fixture com `yield` em teste novo e anotada `Iterator[tipo]`, com `from collections.abc import Iterator`.
- Fora do item (54.1): `-V`, `--help`, parser de argumentos, versao na janela e o executavel do PyInstaller.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest -> exit 0
- smoke: python -m filepilot --version (timeout 30 s) -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-version/*.md
```
