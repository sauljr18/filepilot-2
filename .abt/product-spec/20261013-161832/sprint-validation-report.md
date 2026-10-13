# Relatorio de Prontidao para o Fatiamento: Correcao de sete defeitos remanescentes na main do FilePilot

**Data:** 2026-10-13
**Modo:** so SPEC + itens

## 1. Cobertura de Requisitos

Fonte: o escopo de `discovery-notes.md` (modo so SPEC + itens, sem `prd.md`), conferido contra a seção `## 45.` de `.abt/SPEC.md` e contra o código lido (`undo.py`, `history_tab.py`, `scanner.py`, `planner.py`, `organize_tab.py`, os testes citados e `.github/workflows/tests.yml`), não só contra a Traceability Matrix.

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| D1: Historico com data invalida (ano 0001) carrega a pagina | 45.2; testes 1 a 4; acrescenta a 7.4 | coberto |
| D2: desfazer com laco de atalho nao quebra com erro interno (`PASTA_INVALIDA`, opcao A) | 45.3; testes 1 a 6; acrescenta a 6.5 | coberto |
| D3: recusa do laco provada tambem no Windows, sem teste pulado | 45.4; testes 1 a 9 | coberto |
| D4: barra de progresso some ao desfazer | 45.5; testes 1 a 6; acrescenta a 7.2 | coberto |
| D5: testes de instancia unica e do botao de desfazer falham em vez de travar | 45.6; testes 1 a 6 | coberto |
| D6: checagem de tipos cobre os testes; `mypy .` sem erros | 45.7; substitui o comando e a frase de 19.2 | coberto |
| D7: repositorio com `.gitignore` | 45.8; testes 1 a 4 | coberto |
| Um item de correcao com teste por defeito | 45.2 a 45.8 (testes obrigatorios) | coberto |
| Fora de escopo (qualquer mudanca alem dos sete defeitos, funcionalidade nova, atualizar a stack-decision) | 45.1; 45.9 | coberto |
| Metrica: cada defeito com teste que falha antes e passa depois | 45.2 a 45.8 | coberto |
| Metrica: `mypy .` sem erros | 45.7 | coberto |

Nenhuma linha `CORTADO`. Decisões aprovadas pela pessoa na SPEC (opcao A de 45.3 e as sugestoes 1 a 3 do enriquecimento) sao decisão registrada, não lacuna.

**Lacunas:** 0.

## 2. Mapa de Dependencias

Todos os 24 itens existentes na fila estao `pronto` (`abt queue list --json`); nenhum dos sete itens novos depende de item aberto. As dependencias reais abaixo foram conferidas por grep nos detalhes de item (`grep -l <termo> .abt/items/*/*.md`).

| Parte | Depende de |
|---|---|
| D1 (Historico, `format_local_time`) | `filepilot-v1-11` (aba Historico, cita `history_tab.py`) |
| D2 (desfazer com laco) | `filepilot-fix2-4` (`resolve_folder` publico, citado tambem por `filepilot-fix-1`, `filepilot-fix-2`, `filepilot-fix2-2`) e `filepilot-v1-11` (desfazer na interface) |
| D3 (laco no Windows) | `filepilot-fix2-4` (planejamento com laco, `resolve_folder`) |
| D4 (barra de progresso ao desfazer) | `filepilot-v1-10` (barra) e `filepilot-v1-11` (desfazer na interface) |
| D5 (testes que travam) | `filepilot-fix2-3` (instancia unica, `__main__.py`) e `filepilot-v1-11` (`test_undo_button.py`) |
| D6 (mypy cobre os testes) | `filepilot-mypy-win32-1` e `filepilot-mypy-win32-2` (comando unico e workflow de 19) |
| D7 (`.gitignore`) | nenhuma |

Entre as partes novas nao ha dependencia com direcao: as sete sao independentes (45.1). Ordem recomendada, sem ser obrigatoria: D3 antes de D2, porque D2 passa a usar `resolve_folder` e o item de D3 muda o corpo dele; D6 antes de D1, D2, D4 e D5 para que os arquivos de teste novos nasçam sob o comando novo de mypy.

**Dependencias criticas:** nenhuma que bloqueie 3 ou mais partes. A mais pesada e D3 antes de D2, que afeta uma parte.

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| D1 | Simples | 2 |
| D2 | Medio | 4 |
| D3 | Medio | 5 |
| D4 | Simples | 2 |
| D5 | Medio | 4 |
| D6 | Simples | 2 |
| D7 | Simples | 1 |

Nenhuma parte passa de 8 pontos, tem 5 ou mais subcomportamentos ou cruza 3 ou mais componentes. D3 e a maior: o helper de travessia, a mudanca de `resolve_folder`, os dois arquivos de teste e a prova no runner Windows. Cada defeito e um item com um objetivo verificavel.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| A deteccao de laco no Windows (D3) foi medida so no Linux; se `windows-latest` nao detectar, o teste 2 de 45.4 falha | Medio | O gate do item de D3 exige o job de testes verde em `windows-latest`; sem isso o item nao esta concluido |
| O `autouse` de `tests/conftest.py` (D5) pode revelar teste existente que abre dialogo real | Baixo | A suite de 465 testes passa sem travar hoje, entao nenhum abre; se algum aparecer, ele troca o metodo por espiao, como os existentes |
| Item de teste novo copia a fixture `conn` com a anotacao errada e quebra o comando novo de mypy (D6) | Baixo | A regra de `Iterator` de 45.7 e citada em 45.2, 45.3 e 45.5; entregar D6 antes dos demais evita o caso |
| Com a opcao A de D2, o desfazer repete `PASTA_INVALIDA` enquanto o laco existir | Baixo | Decisao da pessoa registrada em 45.3; uma organizacao mais nova passa a ser a ultima desfazivel |
| 45.7 troca a decisao de 19.2 de deixar `tests/` fora do mypy | Baixo | Registrada nas decisoes aprovadas do relatorio da SPEC; o gate do item de D6 confere o comando novo |

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro da mudanca cabe em 7 itens independentes de ate 5 pontos cada (20 pontos no total), sem fundacao nova, com caminho critico curto (D3 antes de D2) e todos os itens existentes ja entregues.

## 6. Dados para o fatiamento

Epicos ja usados no projeto (`abt epic list --ids --json`, 5): `filepilot-fix`, `filepilot-fix2`, `filepilot-mypy`, `filepilot-mypy-win32`, `filepilot-v1`.

Itens ja usados (`abt queue list --json`, 24, todos `pronto`): `filepilot-fix-1` a `filepilot-fix-4`; `filepilot-fix2-1` a `filepilot-fix2-4`; `filepilot-mypy-1`; `filepilot-mypy-win32-1` e `filepilot-mypy-win32-2`; `filepilot-v1-1` a `filepilot-v1-13`.

Dependencias com itens existentes (conferidas por grep): `filepilot-v1-10`, `filepilot-v1-11`, `filepilot-fix2-3`, `filepilot-fix2-4`, `filepilot-mypy-win32-1` e `filepilot-mypy-win32-2`, nas partes da secao 2. Bruno nao escolhe ids; quem escolhe e o fatiamento.

Pronto para fatiamento: SIM
