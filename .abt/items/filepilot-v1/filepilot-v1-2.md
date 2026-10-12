# filepilot-v1-2 - Leitura da pasta e pastas protegidas
Epico: filepilot-v1 | Ordem: 2 | Pontos: 4 | Depende de: filepilot-v1-1

## Objetivo
scan_folder lista os arquivos elegiveis do nivel da pasta escolhida e recusa pasta invalida, ilegivel, vazia, protegida ou de rede com o codigo de erro certo.

## Contexto herdado
Entregue por filepilot-v1-1 (commit 940e833). Nao reimplementar: pyproject.toml, pacotes `filepilot.domain` e `filepilot.db`, migracao 0001_initial e o workflow de testes.

Artefatos criados:
- pyproject.toml - manifesto - setuptools; `requires-python >=3.12`; `PySide6==6.12.0`; extras `dev` com pytest, pytest-qt, pyinstaller e `mypy==2.4.0`; `testpaths = ["tests"]`
- filepilot/__init__.py - pacote - `__version__ = "0.1.0"`
- filepilot/domain/categories.py - constantes - `CategoryDef(folder, extensions)` e `CATEGORIES: dict[str, CategoryDef]` (documentos, imagens, videos, compactados)
- filepilot/domain/models.py - dataclasses - `ScannedFile(path, name, extension, size_bytes)`, `Rule`, `PlannedOperation`, `Plan` (com `is_empty`), `OrganizationResult`
- filepilot/domain/errors.py - excecao - `FilePilotError(code, message, fields=None)` com atributos `code`, `message` e `fields`
- filepilot/db/connection.py - servico - `open_connection(db_path: Path) -> sqlite3.Connection`
- filepilot/db/migrations.py - servico - `apply_migrations(conn)` e a lista `MIGRATIONS` com a 0001_initial
- .github/workflows/tests.yml - CI - roda `pytest` e `python -m mypy --platform win32 filepilot` no windows-latest

Contratos:
- `ScannedFile` (filepilot/domain/models.py): `path: Path`, `name: str`, `extension: str` (minusculas, sem ponto, `""` se nao houver), `size_bytes: int`; dataclass imutavel (`frozen=True`). Armadilha: `scan_folder` precisa preencher `extension` ja normalizada.
- `FilePilotError` (filepilot/domain/errors.py): `FilePilotError(code: str, message: str, fields: dict[str, str] | None = None)`; `message` e o texto da interface de 6; use os codigos de 6 (`PASTA_INVALIDA`, `PASTA_PROTEGIDA`, `PASTA_ILEGIVEL`, `PASTA_VAZIA`).

Nomes decididos:
- Os testes ficam em `tests/<pacote>/test_<modulo>.py` e cada pasta de teste tem `__init__.py`.
- `CATEGORIES` guarda a subpasta em `CategoryDef.folder` (nao `subfolder`).

Padroes estabelecidos:
- Testes de caminho usam `tmp_path` do pytest e anotam `-> None`.
- Todo codigo novo passa em `python -m mypy --platform win32 filepilot` (configuracao padrao, sem arquivo de configuracao proprio).
- Nenhum caractere Unicode de traco ou aspas tipograficas no codigo de `filepilot` (grep do gate).

## Features

### filepilot-v1-2-f1 scan_folder lista os arquivos elegiveis do nivel da pasta
Linhas da SPEC: .abt/SPEC.md L260-275
Arquivos:
- filepilot/services/__init__.py (novo)
- filepilot/services/scanner.py (novo)
- tests/services/test_scanner.py (novo)
Criterios de aceite:
- Em `tmp_path` com 3 arquivos visiveis, 1 pasta e 1 arquivo oculto (atributo simulado), `scan_folder` devolve exatamente os 3 arquivos, ordenados por nome sem diferenciar maiusculas.
- A extensao de `a.tar.gz`, `.gitignore` e `b.` e `gz`, vazio e vazio, respectivamente.
- Pasta inexistente levanta `PASTA_INVALIDA`, falha de listagem levanta `PASTA_ILEGIVEL` e pasta sem arquivos elegiveis levanta `PASTA_VAZIA`.
- Link simbolico para arquivo nao aparece na lista; atalho `.lnk` aparece com extensao `lnk`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_scanner.py -> exit 0
- parser: python -m py_compile filepilot/services/scanner.py -> exit 0
- grep deve casar: FILE_ATTRIBUTE_HIDDEN em filepilot/services/scanner.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Atributo oculto ou de sistema: `os.stat(path).st_file_attributes & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM)`; fora do Windows o atributo nao existe e o arquivo conta como visivel (use `getattr`).
- Arquivo cujo `os.stat` falha durante a listagem e omitido, sem interromper.
- Os modelos `ScannedFile` e `FilePilotError` vem do item filepilot-v1-1.

### filepilot-v1-2-f2 Pastas protegidas e pastas de rede
Linhas da SPEC: .abt/SPEC.md L260-275
Arquivos:
- filepilot/services/scanner.py (novo)
- tests/services/test_scanner_protected.py (novo)
Criterios de aceite:
- Raiz de unidade, `%SystemRoot%`, `%ProgramFiles%`, `%ProgramFiles(x86)%` e qualquer pasta dentro delas levantam `PASTA_PROTEGIDA` antes de listar.
- Caminho que comeca com `\\` (por exemplo `\\servidor\pasta`) e unidade de rede (`GetDriveTypeW` igual a 4, simulado) levantam `PASTA_PROTEGIDA`.
- Fora do Windows a verificacao de unidade de rede e ignorada e os demais testes continuam passando.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_scanner_protected.py -> exit 0
- parser: python -m py_compile filepilot/services/scanner.py -> exit 0
- grep deve casar: PASTA_PROTEGIDA em filepilot/services/scanner.py
- grep deve casar: GetDriveTypeW em filepilot/services/scanner.py
Dicas:
- Use as variaveis de ambiente com padrao `C:\Windows`, `C:\Program Files` e `C:\Program Files (x86)` quando ausentes (SPEC 6.1).
- Os testes que dependem do Windows usam `skipif` e rodam de verdade no windows-latest; no Linux use mocks de `os.environ` e de `ctypes`.
- Mensagem de `PASTA_PROTEGIDA`: "Esta pasta é protegida e não pode ser organizada. Escolha outra pasta." (tabela da secao 6, L232-259).

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
