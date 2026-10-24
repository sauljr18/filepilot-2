# Validacao do item filepilot-help-1 - Opcao --help e -h imprimem o uso e saem sem abrir a janela

**Item:** filepilot-help-1 | **Epico:** filepilot-help | **Data:** 2026-10-24
Execucao: 20261024-124421
Veredito: APROVADO
**Tipo do item:** backend (ponto de entrada de linha de comando; nenhuma tela nova ou alterada)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot tests` exit 0, `Success: no issues found in 84 source files`; zero erro novo contra a baseline (0 erros) |
| 2 Criterios de aceite | PASS | 4/4 atendidos, 0 NAO VERIFICAVEL |
| 3 Qualidade de codigo | PASS | zero problemas (grep TODO/placeholder/not implemented/FIXME vazio nos 2 arquivos do diff) |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint; so o ponto de entrada muda (56.1) |
| 5 Testes | PASS | 14 passed (itens + `test_version_cli.py`); suite completa 538 passed, 2 skipped por plataforma pre-existentes (`tests/services/test_destination_checks.py:153`, `tests/services/test_scanner_protected.py:185`); 3 mutacoes independentes pegas |
| 6 Consistencia entre documentos | PASS | consistente com 56.1, 56.3 e 56.4 (ancoras conferidas) |
| 7b Varredura adversarial | PASS | nenhum: sem entidade nova; sem parser reinventado (`argparse` ausente, como 56.1 pede) |
| 7c Degradacao e borda | PASS | nenhuma: argumentos fora do desvio seguem o caminho de hoje; `sys.stdout` `None` devolve 0 |
| 7d Matriz (backend) | PASS | BE-1: `grep -rn argparse filepilot/` = 0; BE-2 e BE-3 n/a (sem DI nem policies) |
| 7e Funcao irma e comando citado | PASS | nenhuma: o uso cita `--help`, `-h` e `--version`, os tres tratados em `filepilot/__main__.py:70` e `:73` |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-help-1-f1 | `python -m filepilot --help` e `-h`: exit 0, stdout = 4 linhas de 56.3 + quebra de linha, stderr vazio (teste 1 de 56.4) | PASS | `tests/test_help_cli.py:45-56`; `filepilot/__main__.py:25-30` (texto igual byte a byte ao bloco de 56.3, descricoes na coluna 15) e `:73-75`; smoke `python -m filepilot --help` exit 0 |
| filepilot-help-1-f1 | Em processo com `QApplication`, `default_data_dir` e `open_main_window` proibidos: `main()` devolve 0 e imprime so o uso; com `sys.stdout` `None`, devolve 0 (testes 2 e 4) | PASS | `tests/test_help_cli.py:59-69` e `:99-107`; execucao manual com `sys.stdout=None` e `-h`: `ret=0` |
| filepilot-help-1-f1 | `--help x`, `-h --version` e `-H`: `QApplication` falsa criada uma vez, `open_main_window` falso chamado uma vez, stdout vazio (teste 3) | PASS | `tests/test_help_cli.py:72-96`; comparacao exata em `filepilot/__main__.py:73` |
| filepilot-help-1-f1 | mypy exit 0 com `Success: no issues found` e `pytest` exit 0, com `tests/test_version_cli.py` sem mudanca | PASS | Gate 1 e Gate 5 acima; `git diff --quiet -- tests/test_version_cli.py` exit 0 |

## Prova por mutacao (escopo: tests/test_help_cli.py, revertida por copia)

| # | Diff | Resultado |
|---|------|-----------|
| M1 | `"  --version   mostra a versão e sai"` -> `"  --version   mostra a versao e sai"` | 4 failed, 5 passed |
| M2 | `if sys.argv[1:] in (["--help"], ["-h"]):` -> `if sys.argv[1:] in (["--help"],):` | 3 failed, 6 passed |
| M3 | `if sys.argv[1:] in (["--help"], ["-h"]):` -> `if sys.argv[1:][:1] in (["--help"], ["-h"]):` | 2 failed, 7 passed |

Depois das mutacoes: `git status --short` e `git diff --stat` iguais aos do Passo 0.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
