# Itens - Opcao --version na linha de comando
Epico: filepilot-version
Titulo do epico: Opcao --version na linha de comando
**Data:** 2026-10-23
**Modo:** so SPEC + itens

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-version-1 | Opcao --version imprime a versao e sai sem abrir a janela | 1 | - | `python -m filepilot --version` imprime o `__version__` de `filepilot/__init__.py` e sai com codigo 0 sem criar a `QApplication` |

## 2. Criterios de aceite

- filepilot-version-1:
  - `python -m filepilot --version` termina com codigo 0, a saida padrao e exatamente o `__version__` seguido de quebra de linha (hoje `0.1.0`) e a saida de erro fica vazia.
  - Com `sys.argv` igual a `["filepilot", "--version"]`, `main()` devolve 0 sem criar `QApplication` nem chamar `default_data_dir` e `open_main_window` (testes 2 e 5 de 54.2, inclusive com `sys.stdout` igual a `None`).
  - Com `sys.argv` igual a `["filepilot"]` e a `["filepilot", "--version", "x"]`, `main()` segue o caminho de hoje: cria a `QApplication` uma vez e chama `open_main_window` uma vez (teste 3 de 54.2).
  - `python -m mypy --platform win32 filepilot tests` termina com codigo 0 e `Success: no issues found`, e `pytest` passa inteiro.

## 3. Mapa para a SPEC

- filepilot-version-1: 54.1 Objetivo e fora de escopo; 54.2 Ponto de entrada com --version.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| Teste 1 de 54.2 exige saida de erro vazia: um aviso do Python ou do PySide6 no runner `windows-latest` quebraria o teste sem defeito no codigo | Baixo | O item roda o teste 1 no Linux e no runner `windows-latest`; aviso que aparecer e tratado no proprio item |

## 5. Cobertura

| Item do escopo | Item |
|---|---|
| `python -m filepilot --version` imprime o `__version__` de `filepilot/__init__.py` | filepilot-version-1 |
| O comando sai com codigo 0 e nao abre a interface grafica | filepilot-version-1 |
| Fora de escopo: outros argumentos, fonte da versao, versao na janela, abertura sem argumento como hoje | filepilot-version-1 (teste 3 e o que 54.1 exclui) |
| Metrica: imprime a versao e sai com 0, sem janela | filepilot-version-1 |
