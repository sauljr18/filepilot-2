# filepilot-fix3-2 - Arquivo .gitignore na raiz do repositorio
Epico: filepilot-fix3 | Ordem: 2 | Pontos: 1 | Depende de: -

## Objetivo

O repositorio passa a ter um .gitignore na raiz com os nove padroes da SPEC, sem ignorar nenhum arquivo rastreado, e um teste confere o conteudo e o efeito.

## Contexto herdado

-

## Features

### filepilot-fix3-2-f1 Arquivo .gitignore com os nove padroes
Linhas da SPEC: .abt/SPEC.md L1393-1414
Arquivos:
- .gitignore (novo)
- packaging/filepilot.spec L1-10
Criterios de aceite:
- O `.gitignore` da raiz tem exatamente as nove linhas de 45.8, nesta ordem: `__pycache__/`, `*.py[cod]`, `*.egg-info/`, `.pytest_cache/`, `.mypy_cache/`, `.venv/`, `venv/`, `build/` e `dist/`.
- `git ls-files -ci --exclude-standard` nao imprime nada: nenhum arquivo rastreado casa com o `.gitignore`.
- `git check-ignore -q packaging/filepilot.spec` termina com exit 1 e o mesmo vale para `.abt/SPEC.md` e `.github/workflows/tests.yml`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- grep deve casar: ^__pycache__/$ em .gitignore
- grep deve casar: ^\*\.egg-info/$ em .gitignore
- grep deve casar: ^build/$ em .gitignore
- grep deve casar: ^dist/$ em .gitignore
- grep nao deve casar: spec em .gitignore
Dicas:
- Medicao desta especificacao: depois de rodar a suite, `git status --short` lista cada `__pycache__/` e, depois de `pip install -e`, `filepilot.egg-info/`; `.mypy_cache/` e `.pytest_cache/` ja trazem o proprio `.gitignore` e nao aparecem, mas o padrao entra mesmo assim.
- `build/` e `dist/` sao as pastas de saida do PyInstaller; `packaging/filepilot.spec` e `.github/workflows/build.yml` sao rastreados e nao podem ser ignorados.
- O item `filepilot-v1-13` registra a falta do `.gitignore` como armadilha (`.abt/items/filepilot-v1/filepilot-v1-13.md` L19); nao existe item que o entregue.
- Nao ignore `.abt/`: a especificacao e os itens ficam no repositorio.

### filepilot-fix3-2-f2 Teste do .gitignore
Linhas da SPEC: .abt/SPEC.md L1416-1421
Arquivos:
- tests/test_gitignore.py (novo)
- tests/test_repository_rules.py L1-30
Criterios de aceite:
- `pytest tests/test_gitignore.py` termina com exit 0 e confere as nove linhas lidas com `splitlines()`.
- O teste usa `git check-ignore -q` com exit 0 para `filepilot/__pycache__/x.cpython-312.pyc`, `filepilot.egg-info/PKG-INFO`, `.mypy_cache/x`, `.pytest_cache/x`, `.venv/x`, `venv/x`, `build/x` e `dist/x`, e exit 1 para `packaging/filepilot.spec`, `.abt/SPEC.md`, `.github/workflows/tests.yml` e `pyproject.toml`.
- Sem `git` no PATH ou fora de um repositorio, o teste faz `pytest.skip`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/test_gitignore.py -> exit 0
- testes: pytest tests/test_gitignore.py -> exit 0
- grep deve casar: check-ignore em tests/test_gitignore.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/test_gitignore.py
Dicas:
- Padrao a seguir: `tests/test_repository_rules.py` (L1-30) usa `ROOT = Path(__file__).resolve().parent.parent` e `pathlib`.
- Use `subprocess.run(["git", ...], cwd=ROOT)` com `capture_output=True` e confira o `returncode`; no Windows os caminhos do `git check-ignore` aceitam barra normal.
- Regra de 45.7: fixture com yield no arquivo novo e anotada `Iterator[tipo]`.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests/test_gitignore.py -> exit 0 (o comando completo de 45.7 so passa depois do item filepilot-fix3-1, por isso o gate checa o arquivo novo)
- testes: pytest -> exit 0
- git ls-files -ci --exclude-standard sem saida
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix3/*.md
```
