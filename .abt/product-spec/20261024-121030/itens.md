# Itens - Opcao --help na linha de comando

Epico: filepilot-help
Titulo do epico: Opcao --help na linha de comando
**Data:** 2026-10-24
**Modo:** delta focado

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-help-1 | Opcao --help e -h imprimem o uso e saem sem abrir a janela | 2 | filepilot-version-1 | `python -m filepilot --help` e `python -m filepilot -h`, cada um como argumento unico, imprimem o texto de uso de 56.3 e saem com 0 sem abrir a janela |

## 2. Criterios de aceite

- filepilot-help-1:
    - `python -m filepilot --help` e `python -m filepilot -h` terminam com codigo 0, saida padrao igual as quatro linhas do bloco de 56.3 mais uma quebra de linha e saida de erro vazia (teste 1 de 56.4).
    - Com `--help` ou `-h`, `main()` devolve 0 sem criar `QApplication` nem chamar `default_data_dir` e `open_main_window` (testes 2 e 4 de 56.4, inclusive com `sys.stdout` igual a `None`).
    - `["filepilot", "--help", "x"]`, `["filepilot", "-h", "--version"]` e `["filepilot", "-H"]` seguem o caminho de hoje: `QApplication` criada uma vez, `open_main_window` chamado uma vez, nada na saida padrao (teste 3 de 56.4).
    - `python -m mypy --platform win32 filepilot tests` sai com 0 e `Success: no issues found`, e `pytest` passa inteiro, inclusive `tests/test_version_cli.py` sem mudanca.

## 3. Mapa para a SPEC

- filepilot-help-1: 56.1 Objetivo e fora de escopo; 56.3 Ponto de entrada com --help e -h; 56.4 Testes do ponto de entrada com --help.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| Espacos do alinhamento de `_USAGE` digitados errado quebram os testes de texto literal | Baixo | O detalhe do item cita o bloco `text` de 56.3 como fonte exata |

## 5. Cobertura

| Item do escopo | Item |
|---|---|
| `--help`, argumento unico, imprime o uso e sai com 0 sem abrir a janela | filepilot-help-1 |
| `-h`, argumento unico, faz o mesmo que `--help` | filepilot-help-1 |
| Texto de uso em portugues, terminando com nova linha, uma linha por opcao | filepilot-help-1 |
| Demais combinacoes de argumentos abrem a janela; sem parser | filepilot-help-1 |
| Sem saida padrao (`pythonw`): devolve 0 sem excecao | filepilot-help-1 |
| Metrica: `--help` e `-h` imprimem o uso e saem com 0, sem janela | filepilot-help-1 |
