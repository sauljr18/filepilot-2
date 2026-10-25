# Itens - Opcao -V na linha de comando

Epico: filepilot-opcao-v
Titulo do epico: Opcao -V na linha de comando
**Data:** 2026-10-25
**Modo:** delta focado

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-opcao-v-1 | Opcao -V imprime a versao e aparece na ajuda | 2 | filepilot-version-1,filepilot-help-1 | `python -m filepilot -V`, como argumento unico, imprime a versao e sai com 0 sem abrir a janela, e o texto do `--help` cita `-V` junto do `--version` |

## 2. Criterios de aceite

- filepilot-opcao-v-1:
  - `python -m filepilot -V` termina com codigo 0, saida padrao igual a `filepilot.__version__ + "\n"` e saida de erro vazia (teste de subprocesso de 58.6, parametrizado com `--version` e `-V`).
  - Com `sys.argv` igual a `["filepilot", "-V"]` e `QApplication`, `default_data_dir` e `open_main_window` trocados por funcoes que levantam, `main()` devolve 0 (teste em processo de 58.6).
  - Com `sys.argv` igual a `["filepilot", "-V", "x"]` e a `["filepilot", "-v"]`, `main()` cria uma `QApplication` e chama `open_main_window` uma vez, sem nada na saida padrao.
  - `python -m filepilot --help` imprime exatamente as quatro linhas de 58.5 mais a quebra de linha final (`EXPECTED_USAGE` de `tests/test_help_cli.py`).
  - `python -m mypy --platform win32 filepilot tests` sai com 0 e `Success: no issues found`, e `pytest` passa a suite inteira.

## 3. Mapa para a SPEC

- filepilot-opcao-v-1: 58.1 Objetivo e fora de escopo; 58.4 Desvio de versao aceita -V; 58.5 Ponto de entrada com --help e -h; 58.6 Testes do -V e do texto de uso.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| Desvio `-V` e texto de uso em itens separados mexeriam no mesmo `filepilot/__main__.py` e deixariam o teste do `--help` inconsistente entre as entregas | Baixo | fatiado num item so (filepilot-opcao-v-1) |
| Os itens entregues `filepilot-version-1` e `filepilot-help-1` citam as ancoras 54.1, 54.2, 56.1 e 56.3, que as erratas da secao 58 mudam | Baixo | nenhuma: os dois estao `pronto` e integrados (§55, §57); `filepilot-opcao-v-1` cita as ancoras da secao 58 |

## 5. Cobertura

| Item do escopo | Item |
|---|---|
| `python -m filepilot -V`, argumento unico, imprime a versao e sai com 0 sem abrir a janela | filepilot-opcao-v-1 |
| O texto do `--help` e do `-h` cita `-V` junto do `--version`, e o teste do `--help` acompanha | filepilot-opcao-v-1 |
