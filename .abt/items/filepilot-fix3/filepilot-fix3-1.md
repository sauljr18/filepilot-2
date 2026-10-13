# filepilot-fix3-1 - Checagem de tipos do mypy cobre a pasta de testes
Epico: filepilot-fix3 | Ordem: 1 | Pontos: 2 | Depende de: filepilot-mypy-win32-1,filepilot-mypy-win32-2

## Objetivo

O comando unico de mypy passa a checar a pasta tests e termina sem erros: as tres fixtures com yield ficam tipadas como Iterator e o workflow do GitHub Actions usa o comando novo, com um teste que o confere.

## Contexto herdado

-

## Features

### filepilot-fix3-1-f1 Fixtures conn dos testes de interface tipadas como Iterator
Linhas da SPEC: .abt/SPEC.md L1379-1382
Arquivos:
- tests/ui/test_undo_button.py L1-29
- tests/ui/test_history_tab.py L1-26
- tests/ui/test_history_details.py L1-29
Criterios de aceite:
- `python -m mypy --platform win32 filepilot tests` termina com exit 0 e a saida `Success: no issues found`.
- Nos tres arquivos, a fixture conn passa a declarar `-> Iterator[sqlite3.Connection]` e importa `from collections.abc import Iterator`.
- Nenhuma outra funcao de teste dos tres arquivos muda.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest tests/ui/test_undo_button.py tests/ui/test_history_tab.py tests/ui/test_history_details.py -> exit 0
- grep deve casar: Iterator\[sqlite3.Connection\] em tests/ui/test_undo_button.py
- grep deve casar: Iterator\[sqlite3.Connection\] em tests/ui/test_history_tab.py
- grep deve casar: Iterator\[sqlite3.Connection\] em tests/ui/test_history_details.py
- grep nao deve casar: def conn\(tmp_path: Path\) -> sqlite3.Connection: em tests/ui/test_undo_button.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/ui/test_undo_button.py
Dicas:
- Medicao desta especificacao: `mypy .` e `mypy --platform win32 filepilot tests` dao so tres erros, `tests/ui/test_undo_button.py:25`, `tests/ui/test_history_tab.py:21` e `tests/ui/test_history_details.py:24`, todos `The return type of a generator function should be "Generator" or one of its supertypes [misc]`.
- Padrao a seguir: a fixture `conn` de `tests/services/test_undo.py` (L40-43) nao tem yield e fica como esta.
- Regra de 45.7: toda fixture com yield em teste novo ou alterado e anotada `Iterator[tipo]`, tambem nos testes dos outros itens do epico.
- Ver 45.7 da SPEC para o texto que substitui o comando e a frase de 19.2.

### filepilot-fix3-1-f2 Workflow usa o comando de mypy com tests e um teste o confere
Linhas da SPEC: .abt/SPEC.md L1383-1391
Arquivos:
- .github/workflows/tests.yml L1-22
- tests/test_typecheck_workflow.py (novo)
- tests/test_repository_rules.py L1-30
Criterios de aceite:
- `.github/workflows/tests.yml` tem uma unica linha `run: python -m mypy --platform win32 filepilot tests` e nenhuma linha `run: mypy . --no-error-summary` nem `run: python -m mypy --platform win32 filepilot`.
- `pytest tests/test_typecheck_workflow.py` termina com exit 0 e o teste compara linhas inteiras sem os espacos das pontas, porque a forma antiga e prefixo da nova.
- O nome e a ordem dos passos do workflow nao mudam: `Testes` continua antes de `Checagem de tipos`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest tests/test_typecheck_workflow.py -> exit 0
- grep deve casar: run: python -m mypy --platform win32 filepilot tests em .github/workflows/tests.yml
- grep nao deve casar: mypy \. --no-error-summary em .github/workflows/tests.yml
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/test_typecheck_workflow.py
Dicas:
- Padrao a seguir: `tests/test_repository_rules.py` (L1-30) le arquivos do repositorio com `pathlib` a partir de `ROOT = Path(__file__).resolve().parent.parent`.
- Cuidado com a comparacao: `python -m mypy --platform win32 filepilot` esta contido em `python -m mypy --platform win32 filepilot tests`; compare a linha inteira.
- Contrato com o item filepilot-mypy-win32-2: o passo `Checagem de tipos` fica na linha 22 do arquivo; confirme a linha atual antes de editar.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix3/*.md
```
