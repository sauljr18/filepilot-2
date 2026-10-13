# Itens - Correcao de sete defeitos remanescentes da main do FilePilot

Epico: filepilot-fix3
Titulo do epico: Correcao de sete defeitos remanescentes da main do FilePilot
**Data:** 2026-10-13
**Modo:** so SPEC + itens

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-fix3-1 | Checagem de tipos do mypy cobre a pasta de testes | 2 | filepilot-mypy-win32-1,filepilot-mypy-win32-2 | O comando unico de mypy passa a checar tests e termina sem erros, com as tres fixtures com yield tipadas e o workflow atualizado |
| 2 | filepilot-fix3-2 | Arquivo .gitignore na raiz do repositorio | 1 | - | O repositorio tem um .gitignore com os nove padroes da SPEC e nenhum arquivo rastreado casa com ele |
| 3 | filepilot-fix3-3 | Laco de atalhos detectado tambem no Windows | 5 | filepilot-fix2-4 | A recusa de pasta com laco de atalhos nao depende de Path.resolve e e provada por teste que roda no Windows sem ser pulado |
| 4 | filepilot-fix3-4 | Desfazer com laco de atalhos vira PASTA_INVALIDA | 4 | filepilot-fix2-4,filepilot-v1-11 | O desfazer com laco de atalhos em source_path ou folder_path termina com PASTA_INVALIDA em vez de erro interno |
| 5 | filepilot-fix3-5 | Historico mostra a data como veio quando ela e invalida | 2 | filepilot-v1-11 | A aba Historico carrega a pagina e mostra o started_at sem alteracao quando ele nao pode virar horario local |
| 6 | filepilot-fix3-6 | Barra de progresso some ao desfazer a organizacao | 2 | filepilot-v1-10,filepilot-v1-11 | A aba Organizar esconde a barra de progresso quando um desfazer realmente comeca |
| 7 | filepilot-fix3-7 | Testes de instancia unica e desfazer falham em vez de travar | 4 | filepilot-fix2-3,filepilot-v1-11 | Nenhum teste de instancia unica ou do botao de desfazer bloqueia a suite por dialogo real ou leitura sem limite de tempo |

## 2. Criterios de aceite

- filepilot-fix3-1:
  - `python -m mypy --platform win32 filepilot tests` termina com exit 0 e a saida `Success: no issues found`.
  - `pytest tests/test_typecheck_workflow.py` termina com exit 0.
  - `grep -n "python -m mypy --platform win32 filepilot tests" .github/workflows/tests.yml` encontra exatamente uma linha.
  - `pytest` termina com exit 0 e os tres arquivos alterados (`tests/ui/test_undo_button.py`, `tests/ui/test_history_tab.py`, `tests/ui/test_history_details.py`) continuam passando.
- filepilot-fix3-2:
  - `pytest tests/test_gitignore.py` termina com exit 0.
  - O `.gitignore` da raiz tem exatamente as nove linhas de 45.8 da SPEC.
  - `git ls-files -ci --exclude-standard` nao imprime nada.
  - Depois de `pytest`, `git status --short` nao lista nenhum `__pycache__/`.
- filepilot-fix3-3:
  - `pytest tests/services/test_planner_loop.py tests/services/test_scanner_loop.py` termina com exit 0 no Linux, sem o `pytest.skip` de "Path.resolve nao detecta o laco nesta plataforma" no codigo.
  - Com `Path.resolve` trocado por `lambda self, strict=False: self` e laco real, `build_plan` e `scan_folder` levantam `FilePilotError` com `code == "PASTA_INVALIDA"`.
  - O job de testes do GitHub Actions em `windows-latest` termina verde, sem teste de laco pulado.
  - `python -m mypy --platform win32 filepilot tests` termina com exit 0.
- filepilot-fix3-4:
  - `pytest tests/services/test_undo_loop.py tests/ui/test_undo_loop.py` termina com exit 0.
  - Laco no `source_path` ou no `folder_path` faz `undo_last` levantar `FilePilotError` com `code == "PASTA_INVALIDA"` e a mensagem de 6, e a aba mostra essa mensagem em vez de "Ocorreu um erro inesperado. Tente de novo.".
  - Laco so na limpeza de pastas vazias nao levanta erro: `UndoResult.removed_folders == []` e a organizacao fica `desfeita`.
  - `pytest tests/services/test_undo.py tests/services/test_undo_rollback.py tests/ui/test_undo_button.py` continuam com exit 0.
- filepilot-fix3-5:
  - `pytest tests/ui/test_history_invalid_date.py` termina com exit 0.
  - `format_local_time("0001-01-01T00:00:00Z")` devolve `"0001-01-01T00:00:00Z"`.
  - `HistoryTab.reload()` com uma organizacao de `started_at` no ano 0001 e outra valida nao levanta e mostra duas linhas, com a data invalida como veio.
  - `pytest tests/ui/test_history_tab.py` continua com exit 0.
- filepilot-fix3-6:
  - `pytest tests/ui/test_undo_progress.py` termina com exit 0.
  - Depois de organizar e desfazer, `tab.progress.isHidden()` e verdadeiro.
  - Desfazer sem `_db_path` ou sem organizacao desfazivel nao esconde a barra.
  - `pytest tests/ui/test_undo_button.py` continua com exit 0.
- filepilot-fix3-7:
  - `pytest tests/test_no_modal_dialogs.py tests/ui/test_single_instance.py` termina com exit 0.
  - Com `QLockFile` falso e sem espiao, `open_main_window` levanta `AssertionError` em vez de bloquear.
  - `_hold_lock` com um filho que sai na hora falha em menos de 15 s com `AssertionError` ou `pytestqt.exceptions.TimeoutError`.
  - `timeout 600 pytest` termina com exit 0, sem travar.

## 3. Mapa para a SPEC

- filepilot-fix3-1: 45.7 D6: checagem de tipos cobre os testes (substitui o comando e a frase de 19.2).
- filepilot-fix3-2: 45.8 D7: .gitignore.
- filepilot-fix3-3: 45.4 D3: laco de atalhos provado tambem no Windows (altera 37.5 e 27.2).
- filepilot-fix3-4: 45.3 D2: desfazer com laco de atalhos (acrescenta a 6.5).
- filepilot-fix3-5: 45.2 D1: data invalida no Historico (acrescenta a 7.4).
- filepilot-fix3-6: 45.5 D4: barra de progresso some ao desfazer (acrescenta a 7.2).
- filepilot-fix3-7: 45.6 D5: testes que travam em vez de falhar.

Todos os itens citam 45.1 Objetivo e fora de escopo; a regra de Iterator das fixtures de 45.7 vale para os itens 4, 5 e 6.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| A deteccao de laco no Windows (item 3) foi medida so no Linux; se `windows-latest` nao detectar, o teste 2 de 45.4 falha | Medio | O item 3 so conclui com o job de testes verde em `windows-latest` |
| O autouse de `tests/conftest.py` (item 7) pode revelar teste existente que abre dialogo real | Baixo | A suite de 465 testes passa sem travar, entao nenhum abre; se aparecer, troca o metodo por espiao |
| Item de teste novo (4, 5 e 6) copia a fixture conn com a anotacao errada e quebra o mypy do item 1 | Baixo | A regra de Iterator de 45.7 vale para os tres; entregar o item 1 antes evita o caso |
| Com a opcao A do item 4, o desfazer repete PASTA_INVALIDA enquanto o laco existir | Baixo | Decisao da pessoa registrada em 45.3; uma organizacao mais nova passa a ser a ultima desfazivel |
| 45.7 troca a decisao de 19.2 de deixar tests fora do mypy | Baixo | Registrada como decisao aprovada no relatorio da SPEC; o gate do item 1 confere o comando novo |

## 5. Cobertura

| Item do escopo | Item que cobre |
|---|---|
| D1: Historico com data invalida carrega a pagina | filepilot-fix3-5 |
| D2: desfazer com laco de atalho nao quebra com erro interno | filepilot-fix3-4 |
| D3: recusa do laco provada tambem no Windows | filepilot-fix3-3 |
| D4: barra de progresso some depois de desfazer | filepilot-fix3-6 |
| D5: testes de instancia unica e do botao de desfazer falham em vez de travar | filepilot-fix3-7 |
| D6: checagem de tipos cobre os testes, mypy sem erros | filepilot-fix3-1 |
| D7: repositorio com .gitignore | filepilot-fix3-2 |
| Um item de correcao com teste por defeito | filepilot-fix3-1 a filepilot-fix3-7 |
| Fora de escopo: nada alem dos sete defeitos | nenhum item cria funcionalidade nova |
