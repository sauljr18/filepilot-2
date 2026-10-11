# filepilot-v1-1 - Fundacao: projeto, dominio, banco e CI Windows
Epico: filepilot-v1 | Ordem: 1 | Pontos: 5 | Depende de: -

## Objetivo
Projeto Python 3.12 instalavel, com os pacotes domain e db, as cinco tabelas criadas pela migracao 0001_initial e um workflow que roda o pytest no runner windows-latest. Nenhuma funcionalidade de produto entra neste item.

## Contexto herdado
-

## Features

### filepilot-v1-1-f1 Projeto Python com pyproject e dependencias fixas
Linhas da SPEC: .abt/SPEC.md L95-119
Arquivos:
- pyproject.toml (novo)
- filepilot/__init__.py (novo)
- tests/__init__.py (novo)
- tests/test_import.py (novo)
Criterios de aceite:
- `pip install -e .[dev]` termina com exit 0 no Python 3.12.
- `python -c "import filepilot"` termina com exit 0.
- O `pyproject.toml` declara `requires-python = ">=3.12"`, `PySide6==6.12.0` como dependencia e `pytest==9.1.1`, `pytest-qt==4.5.0` e `pyinstaller==6.22.3` como dependencias de desenvolvimento.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest tests/test_import.py -> exit 0
- parser: python -m py_compile filepilot/__init__.py -> exit 0
- grep deve casar: PySide6==6.12.0 em pyproject.toml
- grep deve casar: requires-python em pyproject.toml
- grep nao deve casar: asyncio.new_event_loop em filepilot
- dependencias: PySide6 em pyproject.toml
- dependencias: mypy em pyproject.toml
Dicas:
- A SPEC secao 4 nao lista o `mypy`, mas o typecheck da stack Python o usa: acrescente `mypy` as dependencias de desenvolvimento e registre isso na descricao do PR; a versao deve ser confirmada na instalacao.
- Use o pacote `filepilot` na raiz do repositorio (SPEC 3.1 usa `filepilot/domain/...`), sem a pasta `src`.
- Confirme que cada versao fixada existe no PyPI antes de gravar o `pyproject.toml`.

### filepilot-v1-1-f2 Dominio: categorias, modelos e erros
Linhas da SPEC: .abt/SPEC.md L216-231
Arquivos:
- filepilot/domain/__init__.py (novo)
- filepilot/domain/categories.py (novo)
- filepilot/domain/models.py (novo)
- filepilot/domain/errors.py (novo)
- tests/domain/test_categories.py (novo)
Criterios de aceite:
- `CATEGORIES` tem as 4 chaves `documentos`, `imagens`, `videos` e `compactados`, com as subpastas `Documentos`, `Imagens`, `Videos` e `Compactados` e 11, 8, 6 e 5 extensoes, exatamente as da tabela de 5.5.
- Nenhuma extensao aparece em duas categorias (teste de unicidade).
- `FilePilotError(code, message, fields=None)` guarda os tres valores e e subclasse de `Exception`.
- Existem as dataclasses `ScannedFile`, `Rule`, `PlannedOperation`, `Plan` e `OrganizationResult` com os campos de 6.1, 6.2, 6.3 e 6.6; `PlannedOperation` usa `source_path` e `destination_path` e `Plan.is_empty` e verdadeiro sem operacoes.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest tests/domain -> exit 0
- parser: python -m py_compile filepilot/domain/models.py -> exit 0
- grep deve casar: source_path em filepilot/domain/models.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Os campos de cada dataclass vem de 6.1 (`ScannedFile`), 6.2 (`Rule`, `Plan`, `PlannedOperation`) e 6.3 (`OrganizationResult`); a secao 6 (L232-259) traz os codigos de erro.
- Extensoes sao guardadas em minusculas e sem ponto; os nomes das subpastas ficam com `Videos` sem acento.
- Use nomes snake_case iguais aos das colunas de 5.3 (decisao da SPEC 5).

### filepilot-v1-1-f3 Banco: conexao e migracao 0001_initial
Linhas da SPEC: .abt/SPEC.md L143-186
Arquivos:
- filepilot/db/__init__.py (novo)
- filepilot/db/connection.py (novo)
- filepilot/db/migrations.py (novo)
- tests/db/test_migrations.py (novo)
Criterios de aceite:
- `open_connection(db_path)` cria a pasta pai quando falta, abre o banco com `PRAGMA foreign_keys` igual a 1 e aplica a migracao 0001_initial.
- Depois da migracao existem as tabelas `schema_migrations`, `organizations`, `operations`, `rules` e `rule_extensions` com os indices `idx_organizations_started_at`, `idx_operations_organization_seq` e `idx_rule_extensions_extension`.
- Abrir o banco duas vezes deixa `schema_migrations` com exatamente 1 linha (version 1).
- Inserir em `operations` um status fora de movido, falha, restaurado e nao_restaurado levanta `sqlite3.IntegrityError`; excluir uma `organizations` apaga suas `operations` (ON DELETE CASCADE).
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest tests/db -> exit 0
- parser: python -m py_compile filepilot/db/migrations.py -> exit 0
- grep deve casar: ON DELETE CASCADE em filepilot/db/migrations.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Caminho e pasta de dados do banco em 5.1 (L126-132); a tabela `schema_migrations` esta em 5.2 (L133-142) e as tabelas de regras em 5.4 (L187-215).
- Datas em texto ISO 8601 UTC (`AAAA-MM-DDTHH:MM:SSZ`); `created_at` e `updated_at` nao nulos nas tabelas que os tem.
- A conversao de `em_andamento` para `interrompida` ao abrir o banco e do item filepilot-v1-7.

### filepilot-v1-1-f4 Workflow de testes no runner windows-latest
Linhas da SPEC: .abt/SPEC.md L629-634
Arquivos:
- .github/workflows/tests.yml (novo)
Criterios de aceite:
- O workflow roda em `push` e `pull_request`, em um job no `windows-latest` com Python 3.12.
- O job instala com `pip install -e .[dev]`, define `QT_QPA_PLATFORM=offscreen` e roda `pytest` e `mypy . --no-error-summary`.
- O job termina verde com os testes das features f1 a f3.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- grep deve casar: windows-latest em .github/workflows/tests.yml
- grep deve casar: QT_QPA_PLATFORM em .github/workflows/tests.yml
- grep deve casar: pytest em .github/workflows/tests.yml
Dicas:
- Testes que dependem do Windows usam `pytest.mark.skipif(sys.platform != "win32", ...)`; o runner Windows e o gate deles (SPEC 13).
- O workflow e gate dos itens filepilot-v1-2, filepilot-v1-5, filepilot-v1-6 e filepilot-v1-7.

## Gates do item
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest -> exit 0
- dependencias: pip check -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
