# Validacao do item filepilot-opcao-v-1 - Opcao -V imprime a versao e aparece na ajuda

**Item:** filepilot-opcao-v-1 | **Epico:** filepilot-opcao-v | **Data:** 2026-10-25
Execucao: 20261025-183410
Veredito: APROVADO
**Tipo do item:** backend (ponto de entrada de linha de comando; o diff nao toca tela)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | zero erros: `python -m mypy --platform win32 filepilot tests` exit=0, `Success: no issues found in 84 source files`; `comm` contra a baseline vazio |
| 2 Criterios de aceite | PASS | 7/7 atendidos, 0 NAO VERIFICAVEL |
| 3 Qualidade de codigo | PASS | zero problemas: grep de TODO/placeholder/not implemented/FIXME, Unicode proibido e `argparse` vazio nos 3 arquivos |
| 4 Autorizacao e seguranca | PASS | n/a: sem endpoint, sem dado sensivel |
| 5 Testes | PASS | `pytest` 543 passed, 2 skipped (skipif de plataforma Windows explicito, fora do item: `tests/services/test_destination_checks.py:153`, `tests/services/test_scanner_protected.py:185`) |
| 6 Consistencia entre documentos | PASS | consistente: ancoras 54.2, 56.3, 58.1, 58.6 conferem (`abt spec check`, 4 ok); texto de uso igual byte a byte ao bloco `text` de 56.3 |
| 7b Varredura adversarial | PASS | nenhum: sem entidade nova; sem logica de parsing nova (comparacao exata de `sys.argv[1:]`, sem parser) |
| 7c Degradacao e borda | PASS | nenhuma: `-V x`, `-v` seguem o caminho de hoje (testado); nenhum comentario cita linha |
| 7d Matriz (backend) | PASS | BE-1: `grep argparse filepilot/__main__.py` = 0; BE-2 e BE-3 n/a (sem service nem policy) |
| 7e Funcao irma e comando citado | PASS | nenhuma: o texto de uso cita `--help`, `-h`, `--version`, `-V`, todos tratados em `filepilot/__main__.py:70` e `:73` |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-opcao-v-1-f1 | `python -m filepilot -V` exit 0, stdout `__version__ + "\n"`, stderr vazio (subprocesso parametrizado) | PASS | `filepilot/__main__.py:70`; `tests/test_version_cli.py:39-50`; execucao propria: `-V exit=0 stdout=0.1.0\n stderr_bytes=0` |
| filepilot-opcao-v-1-f1 | `["filepilot", "-V"]` com interface proibida devolve 0 e so a versao; com `sys.stdout` `None` devolve 0 | PASS | `tests/test_version_cli.py:53-61`, `:91-99`; `[curto]` PASSED |
| filepilot-opcao-v-1-f1 | `-V x` e `-v`: uma `QApplication`, uma chamada de `open_main_window`, nada no stdout | PASS | `tests/test_version_cli.py:64-88`; `[curto-extra]` e `[minuscula]` PASSED |
| filepilot-opcao-v-1-f1 | `pytest -v` lista `longo`/`curto` nos 3 parametrizados e `sem`, `extra`, `curto-extra`, `minuscula` | PASS | saida de `pytest -v tests/test_version_cli.py`: 10 PASSED com esses ids |
| filepilot-opcao-v-1-f2 | `--help` e `-h` exit 0, stdout = as 4 linhas do bloco de 56.3 + `\n` | PASS | `filepilot/__main__.py:25-30`; `cmp` com o bloco de 56.3: igual para `--help` e `-h` |
| filepilot-opcao-v-1-f2 | `EXPECTED_USAGE` literal das 4 linhas com `\n` final, sem ler `_USAGE`; demais testes sem mudanca | PASS | `tests/test_help_cli.py:8-13`; `grep _USAGE` so acha `EXPECTED_USAGE`; diff do arquivo so nas linhas 9, 11, 12 |
| filepilot-opcao-v-1-f2 | mypy exit 0 `Success: no issues found` e `pytest` exit 0 | PASS | Gate 1 e Gate 5 acima |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
