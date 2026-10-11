# Validacao do item filepilot-v1-1 - Fundacao: projeto, dominio, banco e CI Windows

**Item:** filepilot-v1-1 | **Epico:** filepilot-v1 | **Data:** 2026-10-11
Execucao: 20261011-233203
Veredito: APROVADO
**Tipo do item:** backend e dados (sem interface)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `mypy . --no-error-summary` exit 0, saida vazia (0 bytes). Gate 1 sem baseline: exigido exit 0 (mypy so existe depois da f1). Extra: `python -m mypy --platform win32 filepilot` = "Success: no issues found in 8 source files" |
| 2 Criterios de aceite | PASS | 13/13 criterios atendidos |
| 3 Qualidade de codigo | PASS | grep de TODO, FIXME, placeholder, not implemented e print( em filepilot, tests e .github: zero ocorrencias; sem bloco comentado |
| 4 Autorizacao e seguranca | PASS | n/a: nao ha endpoint; nenhuma credencial no codigo (RULES 1) |
| 5 Testes | PASS | `pytest -rs -q`: 30 passed, 0 pulados; todo codigo novo com logica tem teste (categorias, erro, modelos, conexao, migracao). Instalacao em venv novo (`pip install '.[dev]'`) exit 0 e `pip check` sem requisitos quebrados |
| 6 Consistencia entre documentos | PASS | tabelas, colunas, CHECKs, indices e categorias conferem com SPEC 5.1 a 5.5; dataclasses com os nomes de 6.1, 6.2, 6.3 e 6.6; nomes snake_case iguais aos das colunas |
| 7b Varredura adversarial | PASS | nenhuma entidade pre-existente; sem consumidores fora do item; sem utilitario existente reinventado (repositorio novo) |
| 7c Degradacao e borda | PASS | nenhuma das 4 perguntas confirmada (ver observacoes) |
| 7d Matriz (backend, dados) | PASS | BE-2/BE-3 n/a (sem DI nem policy); DA-1 migracao aplicada em banco limpo (tmp_path) e idempotente; DA-2 observacao abaixo; DA-3 n/a |
| 7e Funcao irma e comando citado | PASS | nenhuma funcao de service que decide e grava estado; nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-1-f1 | `pip install -e .[dev]` exit 0 no Python 3.12 | PASS | instalacao em venv novo exit 0, Python 3.12.3; pyproject.toml:1-26 |
| filepilot-v1-1-f1 | `python -c "import filepilot"` exit 0 | PASS | exit 0, versao 0.1.0; filepilot/__init__.py:3; tests/test_import.py:4 |
| filepilot-v1-1-f1 | pyproject declara requires-python, PySide6==6.12.0 e dev pytest==9.1.1, pytest-qt==4.5.0, pyinstaller==6.22.3 | PASS | pyproject.toml:9, 11, 16-18 (mais mypy==2.4.0 em :19, pedido pelas Dicas e por SPEC 17.2) |
| filepilot-v1-1-f2 | CATEGORIES com 4 chaves, subpastas e 11, 8, 6, 5 extensoes da tabela de 5.5 | PASS | filepilot/domain/categories.py:15-46; tests/domain/test_categories.py:15, 24, 34 |
| filepilot-v1-1-f2 | Nenhuma extensao em duas categorias | PASS | tests/domain/test_categories.py:57 |
| filepilot-v1-1-f2 | FilePilotError(code, message, fields=None) guarda os tres valores e e subclasse de Exception | PASS | filepilot/domain/errors.py:4, 14-16; tests/domain/test_categories.py:62, 70 |
| filepilot-v1-1-f2 | Dataclasses ScannedFile, Rule, PlannedOperation, Plan, OrganizationResult com os campos de 6.1, 6.2, 6.3, 6.6; source_path e destination_path; Plan.is_empty verdadeiro sem operacoes | PASS | filepilot/domain/models.py:11, 21, 32, 43, 51, 56; tests/domain/test_categories.py:75, 92, 96 |
| filepilot-v1-1-f3 | open_connection cria pasta pai, foreign_keys = 1 e aplica 0001_initial | PASS | filepilot/db/connection.py:20, 22, 23; tests/db/test_migrations.py:39, 46 |
| filepilot-v1-1-f3 | Cinco tabelas e tres indices existem | PASS | filepilot/db/migrations.py:12, 19, 35, 38, 58, 62, 75, 86; tests/db/test_migrations.py:52 |
| filepilot-v1-1-f3 | Abrir duas vezes deixa schema_migrations com 1 linha (version 1) | PASS | filepilot/db/migrations.py:110; tests/db/test_migrations.py:77 |
| filepilot-v1-1-f3 | Status invalido em operations levanta IntegrityError; excluir organizations apaga operations | PASS | filepilot/db/migrations.py:50-54; tests/db/test_migrations.py:105, 132 |
| filepilot-v1-1-f4 | Workflow em push e pull_request, job no windows-latest com Python 3.12 | PASS | .github/workflows/tests.yml:3-5, 9, 15-16 (YAML lido por parser: gatilhos push e pull_request, runs-on windows-latest) |
| filepilot-v1-1-f4 | Instala com `pip install -e .[dev]`, define QT_QPA_PLATFORM=offscreen, roda pytest e mypy | PASS | .github/workflows/tests.yml:11, 18-22 |
| filepilot-v1-1-f4 | O job termina verde com os testes de f1 a f3 | PASS (local) | pytest 30 passed e mypy exit 0 em Linux; a execucao no runner Windows so existe depois do push, na solicitacao de mesclagem |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | .github/workflows/tests.yml | 18 | Observacao: o job so pode ser comprovado no runner Windows depois do push | Conferir o resultado do GitHub Actions na solicitacao de mesclagem antes de mesclar | nao |
| 2 | filepilot/db/migrations.py | 110 | Observacao (7d DA-2): a migracao 0001 nao tem reversao; SPEC 13 diz que migracoes so acrescentam | Nenhuma agora; registrar a decisao se uma migracao futura precisar de reversao | nao |
| 3 | filepilot/db/migrations.py | 110 | Observacao (7c): `apply_migrations` emite BEGIN e falha se a conexao ja tiver transacao aberta; hoje so `open_connection` a chama, em conexao nova | Nenhuma agora; revisar se outro chamador surgir | nao |
| 4 | (repositorio) | - | Observacao: `filepilot.egg-info/` fica nao rastreado e nao ha `.gitignore` no item | Nao commitar `filepilot.egg-info/`; um `.gitignore` e decisao fora dos `Arquivos:` do item | nao |
| 5 | .abt/RULES.md, .abt/WORKFLOW.md | - | Observacao: copiados do clone principal com autorizacao da pessoa no preflight; nao rastreados na branch | Decidir se entram no commit do item ou ficam fora | nao |
