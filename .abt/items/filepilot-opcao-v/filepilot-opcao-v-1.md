# filepilot-opcao-v-1 - Opcao -V imprime a versao e aparece na ajuda
Epico: filepilot-opcao-v | Ordem: 1 | Pontos: 2 | Depende de: filepilot-version-1,filepilot-help-1

## Objetivo

`python -m filepilot -V`, como argumento unico, imprime a versao seguida de quebra de linha e sai com codigo 0, sem criar a `QApplication`, como o `--version`; e o texto de uso do `--help` e do `-h` passa a citar `-V` junto do `--version`, com as quatro linhas de 58.5.

## Contexto herdado

-

## Features

### filepilot-opcao-v-1-f1 Desvio de versao aceita -V, com testes
Âncoras da SPEC: 54.2=a90d9766fdf3, 58.6=25f24e9b530b, 58.1=05fb06b3f6bf
Arquivos:
- filepilot/__main__.py L69-72
- tests/test_version_cli.py L1-89
Criterios de aceite:
- `python -m filepilot -V` termina com codigo 0, a saida padrao e exatamente `filepilot.__version__ + "\n"` e a saida de erro fica vazia (teste de subprocesso parametrizado com `--version` e `-V`, 58.6 item 1).
- Com `sys.argv` igual a `["filepilot", "-V"]` e `QApplication`, `default_data_dir` e `open_main_window` trocados por funcoes que levantam `AssertionError`, `app_main.main()` devolve 0 e imprime so a versao; com `sys.stdout` igual a `None`, devolve 0 sem excecao (58.6 item 1).
- Com `sys.argv` igual a `["filepilot", "-V", "x"]` e a `["filepilot", "-v"]`, `main()` cria a `QApplication` falsa uma vez, chama `open_main_window` falso uma vez e nao imprime nada na saida padrao (58.6 item 2).
- `pytest tests/test_version_cli.py -v` lista os ids `longo` e `curto` nos tres testes parametrizados e `sem`, `extra`, `curto-extra` e `minuscula` no teste do caminho de hoje.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest tests/test_version_cli.py -> exit 0
- smoke: python -m filepilot -V (timeout 30 s) -> exit 0
- grep deve casar: sys.argv\[1:\] in \(\["--version"\], \["-V"\]\) em filepilot/__main__.py
- grep deve casar: \["--version", "-V"\] em tests/test_version_cli.py
- grep nao deve casar: argparse em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/test_version_cli.py
Dicas:
- So a condicao do primeiro `if` de `main()` muda (`filepilot/__main__.py:70`, hoje `sys.argv[1:] == ["--version"]`); o `print(__version__)` e o `return 0` ficam, e o desvio de versao continua antes do desvio de ajuda (`:73`).
- Nos testes 1, 2 e 5 de 54.2, troque o argumento fixo por um parametro `arg: str` com `@pytest.mark.parametrize("arg", ["--version", "-V"], ids=["longo", "curto"])`, no mesmo formato de `tests/test_help_cli.py:45`.
- No teste 3 (`tests/test_version_cli.py:62` e `:63`), acrescente os dois casos ao fim da lista e os ids `curto-extra` e `minuscula` ao fim de `ids`; as duas listas precisam ter o mesmo tamanho, senao a coleta do pytest falha.
- A mensagem de `_forbidden` (`tests/test_version_cli.py:11`) pode continuar citando `--version`: ela so aparece se o teste falhar.
- Regra de 45.7: fixture com `yield` em teste novo e anotada `Iterator[tipo]`, com `from collections.abc import Iterator`.
- Fora do item (58.1): `-V` com outros argumentos, parser de argumentos, versao no executavel do PyInstaller e na janela.

### filepilot-opcao-v-1-f2 Texto de uso cita -V, com o teste do --help
Âncoras da SPEC: 56.3=7c0bdbff240f, 58.6=25f24e9b530b
Arquivos:
- filepilot/__main__.py L25-30
- tests/test_help_cli.py L8-13
Criterios de aceite:
- `python -m filepilot --help` e `python -m filepilot -h` terminam com codigo 0 e a saida padrao e exatamente as quatro linhas do bloco `text` da visao vigente de 56.3 (`uso: python -m filepilot [--help | -h | --version | -V]` na primeira) mais uma quebra de linha.
- `EXPECTED_USAGE` de `tests/test_help_cli.py` e um literal com as mesmas quatro linhas e a quebra de linha final, sem ler `app_main._USAGE`, e os testes de `tests/test_help_cli.py` passam sem outra mudanca.
- `python -m mypy --platform win32 filepilot tests` termina com exit 0 e `Success: no issues found`, e `pytest` termina com exit 0.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest tests/test_help_cli.py -> exit 0
- smoke: python -m filepilot --help (timeout 30 s) -> exit 0
- grep deve casar: uso: python -m filepilot \[--help \| -h \| --version \| -V\] em filepilot/__main__.py
- grep deve casar: uso: python -m filepilot \[--help \| -h \| --version \| -V\] em tests/test_help_cli.py
- grep deve casar: version, -V  mostra a vers em tests/test_help_cli.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/__main__.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/test_help_cli.py
Dicas:
- `_USAGE` (`filepilot/__main__.py:25` a `:30`) passa a ter as linhas `"uso: python -m filepilot [--help | -h | --version | -V]\n"`, `"opções:\n"`, `"  --help, -h     mostra esta ajuda e sai\n"` e `"  --version, -V  mostra a versão e sai"`: cinco espacos depois de `--help, -h` e dois depois de `--version, -V`, descricoes na mesma coluna, sem quebra de linha no fim da ultima.
- `EXPECTED_USAGE` (`tests/test_help_cli.py:8` a `:13`) tem as mesmas quatro linhas, com `\n` tambem no fim da ultima (o `print` acrescenta); `opções` e `versão` acentuados, como hoje.
- O caso `["filepilot", "-h", "--version"]` do teste do caminho de hoje (`tests/test_help_cli.py:76`) nao muda: continua abrindo a janela.
- Contrato compartilhado: o texto de uso e o mesmo em `_USAGE` e em `EXPECTED_USAGE`; a fonte canonica e o bloco `text` da visao vigente de 56.3 (58.5).

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest -> exit 0
- smoke: python -m filepilot -V (timeout 30 s) -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-opcao-v/*.md
```
