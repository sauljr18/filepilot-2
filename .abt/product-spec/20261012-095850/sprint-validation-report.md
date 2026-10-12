# Relatorio de Prontidao para o Fatiamento: Correcao de quatro defeitos do FilePilot

**Data:** 2026-10-12
**Modo:** so SPEC + itens

## 1. Cobertura de Requisitos

Fonte dos requisitos: o escopo de `discovery-notes.md` (Funcionalidades Core F1 a F5). Conferido na seção 27 da SPEC e no código lido nesta execução, não só na Traceability Matrix.

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| F1: laço de atalho na leitura de pasta vira pasta inválida, sem erro interno | 27.2 (`_resolve_folder`, `_is_protected(folder, resolved)`, 5 testes em `tests/services/test_scanner_loop.py`); código afetado: `scanner.py:52` | coberto |
| F2: `SystemRoot` vazia não torna a pasta atual protegida | 27.3 (`_protected_root`, 4 testes em `tests/services/test_scanner_protected.py`); código afetado: `scanner.py:56` e `:57` | coberto |
| F3: ordem da lista estável quando nomes só diferem por maiúscula e minúscula | 27.4 (chave `(casefold, nome)`, 4 testes em `tests/services/test_scanner_order.py`); código afetado: `scanner.py:101` | coberto |
| F4: banco indisponível no meio da organização desfaz o que foi aberto e encerra a organização | 27.5 (`_interrupt_organization`, `rollback` em `_open_organization`, recuperação `_recover_interrupted` em `open_connection`, 4 testes em `tests/db/test_connection_recovery.py` e 8 em `tests/services/test_organizer_interrupted.py`); código afetado: `organizer.py:130`, `:175` a `:221`, `connection.py:12` a `:28` | coberto |
| F5: um item de correção com ao menos um teste por defeito | testes obrigatórios de 27.2 a 27.5 (25 no total) | coberto |
| Fora de escopo: interface, novas funcionalidades, mudança de stack, outros defeitos | 27.1; 27.6 (registro do laço de atalhos no destino do planner) | coberto |

**Lacunas:** 0 requisitos `parcial` ou `ausente`. Nenhum requisito `CORTADO`. Há dependências e sobreposições com itens da fila que o fatiamento precisa tratar (seções 2 e 4): não são lacunas de cobertura.

## 2. Mapa de Dependencias

Dependência: B antes de A.

| Parte | Depende de |
|---|---|
| D1 (27.2, `scanner.py`) | `filepilot-v1-2` (pronto: criou `scanner.py`) |
| D2 (27.3, `scanner.py`) | `filepilot-v1-2` (pronto); D1 antes de D2, porque os dois alteram `_is_protected` (`scanner.py:48` a `:59`) |
| D3 (27.4, `scanner.py`) | `filepilot-v1-2` (pronto); sem dependência dos outros, mas toca `scan_folder` perto de D1 (`scanner.py:88` a `:102`) |
| D4 (27.5, `organizer.py` e `connection.py`) | `filepilot-v1-5` (pronto: criou `organizer.py`); `filepilot-v1-6` antes de D4 (em andamento, reorganiza `organizer.py`); decisão sobre `filepilot-v1-7` (fila): ver riscos 1 e 2 |
| Testes de D4 que chamam `last_undoable` (27.5 testes 4 e 7; recuperação, teste 1) | `filepilot-v1-7` (`filepilot/services/history.py` ainda não existe no código) ou a condição equivalente em SQL |

**Dependencias criticas:** D1 antes de D2 (mesma função). O resto de D1, D2 e D3 corre em paralelo. D4 é a parte que bloqueia mais gente: `filepilot-v1-7` (recuperação ao abrir o banco, `last_undoable`) e `filepilot-v1-6` (extrai `destination_checks.py` de `organizer.py`) mexem nos mesmos arquivos.

Evidência de sobreposição, lida nesta execução em `.abt/items/filepilot-v1/`: `filepilot-v1-7.md`, feature `filepilot-v1-7-f2`, critério "Ao abrir o banco, toda linha `em_andamento` vira `interrompida`" e verificação `grep deve casar: interrompida em filepilot/db/connection.py`; `filepilot-v1-6.md` cita, em "Achados abertos", o `rollback` que falta depois de `BANCO_INDISPONIVEL` (`organizer.py:205-212`) como achado que não bloqueia e que a seção 27 corrige.

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| D1: laço de atalhos vira `PASTA_INVALIDA` (1 helper, ajuste de assinatura, 5 testes) | Simples | 2 |
| D2: variável vazia vale como ausente (1 helper, 3 variáveis, 4 testes) | Simples | 2 |
| D3: ordem total da lista (1 linha de código, 4 testes) | Simples | 1 |
| D4: organização interrompida e recuperação ao abrir o banco (helper, 2 pontos de chamada, `rollback`, `_recover_interrupted`, 12 testes em 2 arquivos novos) | Complexo | 8 |

D4 está no limite de 8 pontos e tem 5 ou mais subcomportamentos (helper, `rollback` na abertura, fechamento, primeira gravação, recuperação com recálculo das contagens, guarda `AND status`). Se a estimativa passar de 8, decompor: D4a (`organizer.py`: helper, `rollback` e 3 testes de falha) e D4b (`connection.py`: recuperação ao abrir o banco e seus 4 testes). A decomposição conflita com o pedido de um item por defeito: só vale se o item estourar 8 pontos.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| 1. A recuperação ao abrir o banco está nos dois lugares: na seção 27 (D4) e em `filepilot-v1-7-f2`; dois itens implementariam a mesma função em `connection.py`, e o de `filepilot-v1-7-f2` não recalcula as contagens (sem isso a linha recuperada fica com `moved_count` 0 e `last_undoable` a recusa, contra 5.3) | Alto | A pessoa decide o dono antes de fatiar. Recomendação: D4 é o dono, com o recálculo; o fatiamento acrescenta a `filepilot-v1-7` (ainda `na_fila`) a mudança de tirar o critério de recuperação de `filepilot-v1-7-f2` ou fazê-lo depender de D4. Alternativa: D4 depende de `filepilot-v1-7` e só acrescenta o recálculo |
| 2. `last_undoable` não existe no código (`filepilot/services/history.py` é de `filepilot-v1-7`); os testes de 27.5 (4 e 7) e da recuperação (1) o chamam e não rodariam | Alto | Escrever esses testes com a condição equivalente em SQL (`status IN ('concluida','interrompida') AND moved_count >= 1`, de 6.4) em vez de importar `history`, ou declarar `Depende de: filepilot-v1-7` no item de D4. Recomendação: a condição em SQL (D4 não fica esperando a fila) |
| 3. `filepilot-v1-6` está `implementando` (branch `abt/filepilot-v1-6`) e reescreve `organizer.py` (extrai `destination_checks.py`): conflito de mesclagem com D4 e deslocamento das linhas citadas na SPEC (`organizer.py:190` a `:221`) | Medio | D4 `Depende de: filepilot-v1-6`; o detalhe do item cita as funções (`_run`, `_open_organization`, `_close_organization`) em vez de só números de linha |
| 4. D1 e D2 alteram a mesma função (`_is_protected`) | Medio | D2 `Depende de: D1`; ou D1 e D2 entregues na ordem, na mesma branch de trabalho |
| 5. D3 altera `scan_folder` perto do trecho de D1 | Baixo | Rebase trivial; D3 independente |
| 6. Teste de laço real e de link `up -> ..` pode falhar no Windows sem privilégio | Baixo | Os testes já preveem `pytest.skip`; os testes por `monkeypatch` cobrem o comportamento nos dois sistemas |
| 7. Recuperação ao abrir o banco depende da premissa de que nenhuma organização está em curso (7.1: conexão única e instância única) | Baixo | Registrar a premissa no item; nenhuma ação extra |

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro cabe em 4 itens de até 8 pontos cada, na ordem D1, D2 (depois de D1), D3 e D4 (depois de `filepilot-v1-6`, com a decisão do risco 1 e a escolha do risco 2); estimativa de 4 itens e 13 pontos.

## 6. Dados para o fatiamento

Bruno não escolhe ids: quem escolhe é o fatiamento.

Epicos ja usados no projeto (`abt epic list --ids --json`): `filepilot-mypy`, `filepilot-mypy-win32`, `filepilot-v1`.

Itens ja usados no projeto (`abt queue list --json`, 16 itens):

| item_id | epic_id | status | depende de |
|---|---|---|---|
| `filepilot-mypy-1` | `filepilot-mypy` | pronto | `filepilot-v1-1` |
| `filepilot-mypy-win32-1` | `filepilot-mypy-win32` | pronto | - |
| `filepilot-mypy-win32-2` | `filepilot-mypy-win32` | pronto | - |
| `filepilot-v1-1` | `filepilot-v1` | pronto | - |
| `filepilot-v1-2` | `filepilot-v1` | pronto | `filepilot-v1-1` |
| `filepilot-v1-3` | `filepilot-v1` | pronto | `filepilot-v1-1` |
| `filepilot-v1-4` | `filepilot-v1` | pronto | `filepilot-v1-1`, `filepilot-v1-2` |
| `filepilot-v1-5` | `filepilot-v1` | pronto | `filepilot-v1-1`, `filepilot-v1-4` |
| `filepilot-v1-6` | `filepilot-v1` | implementando | `filepilot-v1-5` |
| `filepilot-v1-7` | `filepilot-v1` | na_fila (disponível) | `filepilot-v1-1`, `filepilot-v1-5` |
| `filepilot-v1-8` | `filepilot-v1` | na_fila (disponível) | `filepilot-v1-1` |
| `filepilot-v1-9` | `filepilot-v1` | na_fila | `filepilot-v1-2`, `filepilot-v1-3`, `filepilot-v1-4`, `filepilot-v1-8` |
| `filepilot-v1-10` | `filepilot-v1` | na_fila | `filepilot-v1-5`, `filepilot-v1-6`, `filepilot-v1-9` |
| `filepilot-v1-11` | `filepilot-v1` | na_fila | `filepilot-v1-7`, `filepilot-v1-9`, `filepilot-v1-10` |
| `filepilot-v1-12` | `filepilot-v1` | na_fila | `filepilot-v1-3`, `filepilot-v1-8` |
| `filepilot-v1-13` | `filepilot-v1` | na_fila | `filepilot-v1-10`, `filepilot-v1-11`, `filepilot-v1-12` |

Dependências com itens existentes: D1, D2 e D3 partem de `filepilot-v1-2`; D4 parte de `filepilot-v1-5`. Itens existentes afetados: `filepilot-v1-6` (em andamento, mesmo arquivo `organizer.py`) e `filepilot-v1-7` (recuperação ao abrir o banco e `last_undoable`), ver riscos 1 a 3. A seção nova da SPEC é a `## 27.`; as seções `## §N` dos itens já integrados vão de `§18` a `§26`.

Pronto para fatiamento: SIM
