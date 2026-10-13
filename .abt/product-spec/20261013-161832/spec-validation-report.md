# Relatorio de Validacao da SPEC - Round 2/3

**Data:** 2026-10-13
**Modo:** so SPEC + itens
**Secao auditada:** ## 45. Correcao de sete defeitos remanescentes na main [DELTA 2026-10-13, historico, desfazer, laco no Windows, barra de progresso, testes e repositorio]

## Resumo

Contagem acumulada das duas rodadas. Round 1 encontrou 5 achados e corrigiu os 5; Round 2 reauditou a secao inteira depois das correcoes e encontrou 0.

| Categoria | Encontrados | Corrigidos auto | Requer decisao |
|---|---|---|---|
| Erros | 3 | 3 | 0 |
| Inconsistencias | 0 | 0 | 0 |
| Scope Creep | 0 | 0 | 0 |
| Lacunas vs. PRD | 0 | 0 | 0 |
| Definicoes Vagas | 2 | 2 | 0 |
| Inconsistencia de Nomenclatura | 0 | 0 | 0 |
| Total | 5 | 5 | 0 |

Cobertura conferida item a item contra o escopo de `discovery-notes.md` (nenhum pulado): D1 em 45.2, D2 em 45.3, D3 em 45.4, D4 em 45.5, D5 em 45.6, D6 em 45.7 e D7 em 45.8, cada um com testes obrigatorios que falham antes e passam depois; fora de escopo em 45.1 e 45.9; metricas em 45.2 a 45.8. Todos os arquivos e linhas citados na secao foram lidos nesta execucao (`undo.py`, `history_tab.py`, `scanner.py`, `planner.py`, `organize_tab.py`, `organize_worker.py`, `__main__.py`, `tests/ui/test_single_instance.py`, `tests/ui/test_undo_button.py`, `tests/services/test_planner_loop.py`, `.github/workflows/tests.yml`).

## Correcoes Aplicadas Automaticamente

### ERR-001: .mypy_cache apontado como nao rastreado sem medicao

Problema: 45.8 dizia que `.mypy_cache/` aparece como nao rastreado, o que contradiz a medicao.
Referencia: item 7 do escopo (`.gitignore` no repositorio).
Localizacao na SPEC: 45.8, bullet "Hoje".
Evidencia: depois de `mypy .` nesta execucao, `git status --short` nao listou `.mypy_cache/` (o mypy cria um `.gitignore` dentro da pasta de cache), enquanto `__pycache__/` e `*.egg-info/` apareceram.
Correcao aplicada: o bullet passou a dizer que so `__pycache__/` e `*.egg-info/` aparecem (medido), que `.mypy_cache/` e `.pytest_cache/` ja se ignoram sozinhos, e que os padroes entram no `.gitignore` da raiz mesmo assim, com `[DECISAO]` de nao depender de arquivo que a ferramenta cria.

### ERR-002: teste 4 de D4 passava antes da correcao

Problema: o teste "organizacao de outra pasta" nao organizava antes, entao a barra ja nascia escondida e o teste passaria sem a correcao, contra a metrica de falhar antes e passar depois.
Referencia: item 4 do escopo e metrica de teste que falha antes (D4).
Localizacao na SPEC: 45.5, testes obrigatorios, item 4.
Evidencia: `organize_tab.py:109` e `:111` criam a barra e a escondem; sem `_organize` ela nunca e mostrada (`:300`).
Correcao aplicada: o teste passou a rodar `_organize` primeiro, inserir a organizacao de outra pasta com `started_at="2999-01-01T00:00:00Z"`, chamar `tab.refresh_undo()` e so entao `_undo`.

### ERR-003: teste 5 de D4 partia de estado impossivel

Problema: o teste 5 pedia `_undoable is None` "depois de organizar", mas depois de organizar `_undoable` nao e `None`.
Referencia: item 4 do escopo (D4).
Localizacao na SPEC: 45.5, testes obrigatorios, item 5.
Evidencia: `organize_tab.py:328` a `:330` e `:165` a `:172`: `refresh_undo` volta a preencher `_undoable` ao fim da organizacao.
Correcao aplicada: o teste passou a atribuir `tab._undoable = None` direto depois de `_organize` e chamar `tab.undo()`, que retorna pela guarda de `organize_tab.py:352`.

### VAG-001: comparacao da forma antiga do comando por prefixo

Problema: "nenhuma linha com a forma antiga sem `tests`" e ambigua, porque a forma antiga e prefixo da nova e uma busca por substring acharia a nova.
Referencia: item 6 do escopo (D6).
Localizacao na SPEC: 45.7, testes obrigatorios, item 1.
Evidencia: `python -m mypy --platform win32 filepilot` esta contido em `python -m mypy --platform win32 filepilot tests`.
Correcao aplicada: o teste compara linhas inteiras, sem os espacos das pontas, e recusa so `run: mypy . --no-error-summary` e `run: python -m mypy --platform win32 filepilot`.

### VAG-002: TimeoutError sem dizer qual

Problema: "AssertionError ou TimeoutError" nao diz qual `TimeoutError`; o do pytest-qt nao e o embutido.
Referencia: item 5 do escopo (D5).
Localizacao na SPEC: 45.1 (tabela, linha D5) e 45.6, testes obrigatorios, item 5.
Evidencia: `pytestqt.exceptions.TimeoutError` tem a cadeia `TimeoutError`, `Exception`, `BaseException`, `object` (medido nesta execucao); nao herda do embutido.
Correcao aplicada: os dois pontos passaram a citar `pytestqt.exceptions.TimeoutError`, a excecao de `qtbot.waitUntil`.

## Itens Aguardando Decisao

Nenhum.

## Decisoes registradas

- `CORTADO`: nenhuma linha.
- Decisoes aprovadas pela pessoa nesta execucao (nao sao achados): opcao A do desfazer com laco de atalhos (45.3, `PASTA_INVALIDA`); sugestoes 1, 2 e 3 do enriquecimento (45.7, 45.4 e 45.4); sugestao 4 recusada (o desfazer mantem o texto de `PASTA_INVALIDA` de 6).
- Substituicao de decisao anterior: 45.7 troca o comando unico e a frase "A pasta tests/ fica fora da checagem de tipos" de 19.2, que trazia uma `[DECISAO: aprovada no enriquecimento; ...]` de outra execucao. A troca vem do item 6 do escopo de `discovery-notes.md`, aprovado no ponto de checagem desta execucao, e foi avisada a pessoa na pergunta do desfazer. Fica registrada aqui para a aprovacao deste ponto de checagem.
- Hipotese sem medicao possivel nesta execucao (Linux): o `Path.resolve()` do Python 3.12 no Windows trata o erro 1921 como inexistente (45.4, 45.9 item 3). A prova e o teste 2 de 45.4 no runner `windows-latest`; o resto de 45.4 foi medido no Linux.
- `[DECISAO: <motivo>]` da secao 45 (isentas so de Scope Creep, sem achado): `format_local_time` captura `OverflowError` e `OSError`; laco na limpeza de pastas do desfazer nao levanta; limite de 40 saltos; falha de criacao de link no runner do Windows e falha, nao pulo; barra escondida so quando o desfazer realmente comeca; `tests/conftest.py` com dialogos proibidos e `getLockInfo`; comando de mypy com `tests` e sem `packaging`; nove padroes no `.gitignore`.

## Status apos Round 2

APROVAVEL: SPEC sem erros, inconsistencias ou lacunas; pronta para aprovacao.

Retorno: validacao-spec
