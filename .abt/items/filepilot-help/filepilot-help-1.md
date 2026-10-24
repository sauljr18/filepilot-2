# filepilot-help-1 - Opcao --help e -h imprimem o uso e saem sem abrir a janela
Epico: filepilot-help | Ordem: 1 | Pontos: 2 | Depende de: filepilot-version-1

## Objetivo

`python -m filepilot --help` e `python -m filepilot -h`, cada um como argumento unico, imprimem o texto de uso de 56.3 seguido de quebra de linha e saem com codigo 0, sem criar a `QApplication`; qualquer outra lista de argumentos segue o caminho de hoje.

## Contexto herdado

-

## Features

### filepilot-help-1-f1 Desvio --help e -h em main com o texto de uso e testes
Âncoras da SPEC: 56.3=d60428c6a57a, 56.4=063c03802e66, 56.1=eeb13e6e66e2
Arquivos:
- filepilot/__main__.py L1-25
- filepilot/__main__.py L63-77
- tests/test_version_cli.py L1-89
- tests/test_help_cli.py (novo)
Criterios de aceite:
- `python -m filepilot --help` e `python -m filepilot -h` terminam com codigo 0, a saida padrao e exatamente as quatro linhas do bloco `text` de 56.3 mais uma quebra de linha e a saida de erro fica vazia (teste 1 de 56.4).
- Com `sys.argv` igual a `["filepilot", "--help"]` ou `["filepilot", "-h"]` e `QApplication`, `default_data_dir` e `open_main_window` trocados por funcoes que levantam `AssertionError`, `app_main.main()` devolve 0 e imprime so o texto de uso; com `sys.stdout` igual a `None`, devolve 0 sem excecao (testes 2 e 4 de 56.4).
- Com `sys.argv` igual a `["filepilot", "--help", "x"]`, `["filepilot", "-h", "--version"]` e `["filepilot", "-H"]`, `main()` cria a `QApplication` falsa uma vez, chama `open_main_window` falso uma vez e nao imprime nada na saida padrao (teste 3 de 56.4).
- `python -m mypy --platform win32 filepilot tests` termina com exit 0 e `Success: no issues found`, e `pytest` termina com exit 0, com `tests/test_version_cli.py` sem mudanca.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest tests/test_help_cli.py tests/test_version_cli.py -> exit 0
- smoke: python -m filepilot --help (timeout 30 s) -> exit 0
- grep deve casar: _USAGE em filepilot/__main__.py
- grep deve casar: sys.argv\[1:\] in \(\["--help"\], \["-h"\]\) em filepilot/__main__.py
- grep deve casar: uso: python -m filepilot \[--help \| -h \| --version\] em tests/test_help_cli.py
- grep nao deve casar: argparse em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/test_help_cli.py
Dicas:
- `_USAGE` e constante de modulo anotada (`_USAGE: str = ...`) junto das outras constantes de `filepilot/__main__.py` (L13-25), com as quatro linhas do bloco `text` de 56.3 e sem quebra de linha no fim; descricoes alinhadas na coluna 15 (dois espacos + `--help, -h` + dois espacos; dois espacos + `--version` + tres espacos).
- O desvio novo vem logo depois do desvio de `--version` (L64-66) e antes de `app = QApplication(sys.argv)` (L67); o bloco exato esta em 56.3. A escrita e por `print(_USAGE)`, nunca `sys.stdout.write` (com `sys.stdout` `None`, `print` nao faz nada).
- No teste, o texto esperado e um literal escrito no proprio teste (com `opções` e `versão` acentuados), nunca lido de `app_main._USAGE`: assim o teste pega erro de digitacao na constante.
- Reaproveite o estilo de `tests/test_version_cli.py`: `from filepilot import __main__ as app_main`, `_forbid_interface` com `monkeypatch.setattr`, falsos `FakeApplication` e `FakeOpenMainWindow` (copiados para o arquivo novo, sem importar de outro teste) e `pytest.mark.parametrize` com `ids`.
- O teste 1 roda `python -m filepilot` em subprocesso com `sys.executable`, `text=True` e `timeout=30`; o `\r\n` do Windows chega como `\n`, e o acento sai e volta pela mesma codificacao do sistema (cp1252 no Windows, UTF-8 no Linux). Sem `QApplication` o comando nao precisa de tela.
- Saida padrao sem `ã` e `õ` (como `PYTHONIOENCODING=ascii`) sai com 1: limite aceito em 56.3, sem tratamento nem teste.
- Regra de 45.7: fixture com `yield` em teste novo e anotada `Iterator[tipo]`, com `from collections.abc import Iterator`.
- Fora do item (56.1): `-V`, parser de argumentos, mudar o `--version` de 54.2, uso na janela e o executavel do PyInstaller.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest -> exit 0
- smoke: python -m filepilot --help (timeout 30 s) -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-help/*.md
```
