# Relatorio de Prontidao para o Fatiamento: Correcao de quatro defeitos do FilePilot na main

**Data:** 2026-10-12
**Modo:** so SPEC + itens

## 1. Cobertura de Requisitos

Itens do escopo de `discovery-notes.md`, conferidos contra a secao `## 37.` da SPEC e contra o codigo lido nesta execucao.

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| F1: banco indisponivel no meio do desfazer desfaz o que abriu e o segundo desfazer nao marca como restaurado arquivo fora do lugar | 37.2: helper `_rollback` em `filepilot/services/undo.py`, chamado no `except sqlite3.Error` de `_run` (antes do `os.rename` de volta) e de `undo_last`; testes 1 a 5 | coberto |
| F2: leitura da pasta com erro do sistema na aba Organizar nao deixa a aba presa em carregando | 37.3: `except OSError` em `OrganizeTab._read_folder` com `_UNREADABLE` (`PASTA_ILEGIVEL`); testes 1 a 6 | coberto |
| F3: sem saber se ha outra janela aberta o programa avisa em vez de fechar em silencio | 37.4: `lock.error()` em `open_main_window`; so `LockFailedError` e "ja aberto"; texto `_LOCK_UNAVAILABLE` e saida 1; testes 1 a 6 | coberto |
| F4: planejamento com laco de atalho nao quebra com erro interno | 37.5: `scanner.resolve_folder` publico usado por `planner._inside`; `PASTA_INVALIDA`; testes 1 a 8 | coberto |
| F5: um item de correcao com ao menos um teste por defeito | 37.2 a 37.5 (testes obrigatorios) | coberto |
| Fora de escopo: proximas telas, novas funcionalidades, refatoracoes alem das correcoes, outros defeitos | 37.1; 37.6 (3 registros fora de escopo) | coberto |
| Metrica: 4 defeitos corrigidos, 4 testes novos passando, nenhum teste existente quebrado | 37.2 a 37.5; comando unico de mypy de 19.2 | coberto |

**Lacunas:** 0. Nenhum requisito `parcial`, `ausente` ou `CORTADO`.

## 2. Mapa de Dependencias

| Parte | Depende de |
|---|---|
| E1: desfazer com `rollback` (`undo.py`) | filepilot-v1-7 (pronto, criou `undo.undo_last`) |
| E2: aba Organizar com `OSError` (`organize_tab.py`) | filepilot-v1-9 (pronto, criou `OrganizeTab`) |
| E3: instancia unica com `lock.error()` (`__main__.py`) | filepilot-v1-8 (pronto, criou a trava de instancia unica) |
| E4: planejamento com laco (`planner.py`, `scanner.py`) | filepilot-fix-1 (pronto, criou `_resolve_folder`) e filepilot-v1-4 (pronto, criou `build_plan`) |
| E1, E2, E3, E4 entre si | nenhuma: arquivos de codigo e arquivos de teste proprios em cada parte (o teste de interface de E4 foi separado em `tests/ui/test_organize_tab_plan_loop.py`) |

**Dependencias criticas:** nenhuma. Os quatro pre-requisitos ja estao `pronto` na fila, e nenhuma parte bloqueia outra.

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| E1: `_rollback` em 2 pontos de `undo.py` e 5 testes em `tests/services/test_undo_rollback.py` | Simples | 3 |
| E2: `except OSError` em `_read_folder` e 6 testes em `tests/ui/test_organize_tab_read_error.py` | Simples | 2 |
| E3: ramo de `lock.error()` com texto novo e 6 testes em `tests/ui/test_single_instance_unknown.py` (classe falsa de trava e `chmod`) | Simples | 3 |
| E4: renomear `resolve_folder`, usar em `planner._inside`, 8 testes em `tests/services/test_planner_loop.py` e 1 em `tests/ui/test_organize_tab_plan_loop.py` | Simples | 3 |

Nenhuma parte tem mais de 8 pontos, 5 subcomportamentos ou cruza 3 componentes: sem "decompor". Fatiamento sugerido: 1 item por defeito (4 itens), todos independentes.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| E2 e E4 editam arquivos que as proximas telas (filepilot-v1-10, v1-11 e v1-13, `na_fila`) tambem vao editar (`organize_tab.py`, `planner.py` e `scanner.py` em E4); conflito de mesclagem se as telas forem implementadas antes | Medio | Entregar os quatro itens antes das proximas telas, como a pessoa pediu, e os itens das telas devem depender dos de correcao ou ser reabertos sobre a main atualizada |
| O teste de permissao de E3 (`chmod 0o500`) depende do sistema e do usuario (ignorado sob `root` e no Windows) | Baixo | O teste ja prevê `skip` com verificacao previa; os testes 1 a 4 de E3 cobrem o comportamento sem depender do sistema |
| O teste de laco real de E4 depende de o sistema permitir `symlink_to` (Windows sem privilegio) | Baixo | O teste ja prevê `skip`; os testes 1 a 3 trocam `Path.resolve` por `monkeypatch` e rodam em qualquer sistema |
| E4 renomeia `scanner._resolve_folder` para `resolve_folder`; um item que ainda cite o nome antigo quebra | Baixo | Conferido: nenhum teste nem modulo do repositorio cita o nome antigo alem de `scanner.py`; o item de E4 roda a suite inteira e o mypy |
| A suite de interface depende de PySide6, que nao estava instalado no ambiente desta execucao; os testes propostos nao foram rodados aqui | Baixo | Rodar `pytest` e o comando unico de mypy (19.2) no ambiente do item, onde as dependencias de `pyproject.toml` estao instaladas |

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro da mudanca cabe em 4 itens independentes de ate 3 pontos cada (11 pontos no total), sem dependencia entre eles e com todos os pre-requisitos ja entregues; o caminho critico e de 1 item.

## 6. Dados para o fatiamento

Bruno nao escolhe ids: quem escolhe e o fatiamento, que deve evitar os ja usados.

**Epicos ja usados (`abt epic list --ids --json`):** `filepilot-fix`, `filepilot-mypy`, `filepilot-mypy-win32`, `filepilot-v1`.

**Itens ja usados (`abt queue list --json`, 20 itens):**

- `filepilot-fix`: `filepilot-fix-1` a `filepilot-fix-4` (todos `pronto`).
- `filepilot-mypy`: `filepilot-mypy-1` (`pronto`).
- `filepilot-mypy-win32`: `filepilot-mypy-win32-1` e `filepilot-mypy-win32-2` (`pronto`).
- `filepilot-v1`: `filepilot-v1-1` a `filepilot-v1-9` e `filepilot-v1-12` (`pronto`); `filepilot-v1-10`, `filepilot-v1-11` e `filepilot-v1-13` (`na_fila`).

**Dependencias com itens existentes:** E1 depois de `filepilot-v1-7`; E2 depois de `filepilot-v1-9`; E3 depois de `filepilot-v1-8`; E4 depois de `filepilot-fix-1` e `filepilot-v1-4`. Todos `pronto`. Os itens `na_fila` (`filepilot-v1-10`, `filepilot-v1-11`, `filepilot-v1-13`) nao dependem dos quatro de correcao hoje; ver o primeiro risco.

Pronto para fatiamento: SIM
