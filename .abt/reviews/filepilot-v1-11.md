# Validacao do item filepilot-v1-11 - Aba Historico e desfazer na interface

**Item:** filepilot-v1-11 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-163844
Veredito: APROVADO - Gate UI-1 DEFERIDO (smoke ao vivo pendente)
Transicoes a cobrir no smoke: Organizar vazio -> listado, listado -> organizando -> listado, listado -> desfazendo -> listado (Desfazer desabilitado -> habilitado -> desabilitado), Ver detalhes oculto -> visivel (failed_count > 0) -> oculto (atualizar, escolher pasta, nova organizacao), Historico sem selecao -> organizacao selecionada -> detalhes, Historico pagina 1 -> pagina 2, Historico lista -> vazio e lista -> erro com Tentar de novo
**Tipo do item:** interface

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "no issues found in 25 source files"; baseline do Carlos (24 arquivos, exit 0, zero erros): zero erros novos |
| 2 Criterios de aceite | PASS | 10/10 criterios atendidos (f1 4, f2 3, f3 3) |
| 3 Qualidade de codigo | PASS | grep de TODO, placeholder, not implemented e FIXME nos 7 arquivos do diff: zero; sem codigo comentado nem print; grep Unicode (U+2010-2015, U+2018-201F) em `filepilot`: zero |
| 4 Autorizacao e seguranca | PASS | sem endpoint novo; nenhum segredo; a aba so mostra a `message` dos erros de contrato (texto bruto de excecao nao vaza: teste `test_falha_inesperada_no_desfazer_mostra_o_texto_generico`) |
| 5 Testes | PASS | `pytest tests/ui` 153 passed; suite completa 465 passed, 2 skipped (ambos "so existe no Windows", ja existentes); mutacoes refeitas por mim, ver abaixo |
| 6 Consistencia entre documentos | PASS | SPEC L479-498 (7.4) e L434-458 (7.2) conferidas contra o codigo; contratos do contexto herdado respeitados (`page`/`page_size` da pagina devolvida, `UndoResult`, `organization_finished`/`organizing_changed`) |
| 7b Varredura adversarial | PASS | `PlaceholderTab` removida e sem referencia restante (grep zero); `run_in_thread` ampliada, usos antigos (`OrganizeWorker`) intactos; nenhuma consulta nova ao banco na interface (so `list_organizations`, `get_organization_detail`, `last_undoable`) |
| 7c Degradacao e borda | FAIL | achados 1 e 2 da lista (nao decidem o veredito; sem erro 5xx nem regressao) |
| 7d Matriz (interface) | DEFERIDO | UI-1 DEFERIDO (smoke ao vivo pelo Ivan no avanco, antes do commit); UI-2 PASS (carregando, vazio e erro no Historico: history_tab.py:52-55, :269, :277, :224-227); UI-3 n/a (sem roles); UI-4 coberto pela linha `Transicoes a cobrir no smoke:` |
| 7e Funcao irma e comando citado | PASS | `undo()` replica o que `organize()` ja faz: trava `OPERATION_LOCK` no servico `undo_last` (o worker so abre conexao propria, como `OrganizeWorker`), `organizing_changed(True/False)`, thread guardada ate o `wait`; ressalva nos achados 2 e 5; nenhuma mensagem manda rodar comando |

### Mutacoes refeitas pela Rita (escopo: `pytest tests/ui` inteira, 153 testes)

| # | Arquivo | Diff | Resultado |
|---|---------|------|-----------|
| M1 (a do Carlos) | organize_tab.py:375 | `if self.folder is not None and self._undo_folder == self.folder:` -> `if self.folder is not None:` | 1 failed, 152 passed (`test_organizacao_de_outra_pasta_nao_rele_a_pasta_atual`) |
| M2 | organize_tab.py:162 | `self._undoable is not None and self.mode != MODE_ORGANIZING and not self._undoing` -> `self._undoable is not None and not self._undoing` | pego (F em `test_botao_desabilitado_durante_a_organizacao_e_reavaliado_no_fim`), mas a execucao travou no encerramento; encerrei o processo (ver achado 3) |
| M3 | organize_tab.py:329 | `setVisible(result.failed_count > 0)` -> `setVisible(True)` | 2 failed, 151 passed |
| M4 | history_tab.py:297 | `page += 1` -> `break` | 1 failed, 152 passed (`test_show_organization_carrega_a_pagina_...`) |

Cada mutacao foi revertida por copia de arquivo e a reversao confirmada por `grep -c` (1 em cada). No fim, `git status --short` e `git diff --stat` iguais aos do Passo 0, nenhum `.bak` restante e suite `tests/ui` de novo com 153 passed.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-11-f1 | Lista da mais recente para a mais antiga, colunas Data e hora (dd/MM/yyyy HH:mm local), Pasta, Movidos, Falhas e Situacao | PASS | history_tab.py:33, :38-43, :60-66, :113-120; ordem vem de `list_organizations` (history.py `ORDER BY started_at DESC, id DESC`); test_history_tab.py::test_lista_da_mais_recente_para_a_mais_antiga_com_as_colunas e ::test_situacao_em_andamento_e_data_no_horario_local |
| filepilot-v1-11-f1 | Selecionar mostra Arquivo, Origem, Destino final, Situacao e Detalhe; sem selecao "Selecione uma organização." | PASS | history_tab.py:34, :44-49, :124-130, :306-313, :54; test_selecionar_mostra_as_operacoes_da_organizacao e test_sem_selecao_o_painel_direito_pede_para_selecionar |
| filepilot-v1-11-f1 | Vazio "Nenhuma organização registrada ainda."; falha de leitura mostra a mensagem de BANCO_INDISPONIVEL e "Tentar de novo" | PASS | history_tab.py:53, :277, :171, :224-227; test_historico_vazio_mostra_a_mensagem e test_falha_de_leitura_mostra_a_mensagem_e_tentar_de_novo |
| filepilot-v1-11-f1 | "Anterior" desabilitado na pagina 1 e "Próxima" quando `page * 50 >= total` | PASS | history_tab.py:205-207; test_anterior_desabilitado_na_pagina_1_e_proxima_pelo_total e test_proxima_e_anterior_trocam_de_pagina |
| filepilot-v1-11-f2 | "Carregando detalhes..." durante a carga; sem operacoes "Nenhum arquivo nesta organização." | PASS | history_tab.py:52, :55, :315-318; test_enquanto_o_detalhe_carrega_mostra_carregando_detalhes e test_organizacao_sem_operacoes_mostra_nenhum_arquivo |
| filepilot-v1-11-f2 | `HistoryTab.show_organization` carrega a pagina que contem a organizacao, seleciona a linha e mostra os detalhes | PASS | history_tab.py:284-298; test_show_organization_carrega_a_pagina_seleciona_a_linha_e_mostra_os_detalhes (pagina 2) e mutacao M4 |
| filepilot-v1-11-f2 | "Ver detalhes" so com `failed_count > 0`, abre o Historico naquela organizacao, some ao escolher outra pasta, atualizar ou iniciar nova organizacao | PASS | organize_tab.py:329 (visibilidade), :251-252 e :269-270 (some), :79 (sinal), :122 e :334-336 (clique emite o sinal), main_window.py:70 e :77-80 (abre a aba); test_ver_detalhes_* (5 testes) e mutacao M3 |
| filepilot-v1-11-f3 | "Desfazer última organização" so habilitado com `last_undoable` diferente de `None` e `organizing` falso, reavaliado ao abrir a aba e depois de organizar ou desfazer | PASS | organize_tab.py:161-163, :165-172 (`refresh_undo`), :174-177 (`showEvent`), :124, :330, :344 e :381/:389; test_habilita_so_quando_last_undoable_devolve_uma_organizacao (5 casos), test_ao_abrir_a_aba_o_botao_e_reavaliado, test_botao_desabilitado_durante_a_organizacao_e_reavaliado_no_fim e mutacao M2 |
| filepilot-v1-11-f3 | Clique executa `undo_last`; resumo "Desfeito: X arquivos restaurados." e, com `not_restored`, "Não restaurados: " mais os caminhos | PASS | organize_tab.py:349-365 (`undo`), :367-383 (`_on_undone`); organize_worker.py:47-75 (`UndoWorker`, fora da thread da interface); test_desfazer_restaura_os_arquivos_mostra_o_resumo_e_desabilita_o_botao e test_nao_restaurados_acrescenta_os_caminhos_ao_resumo |
| filepilot-v1-11-f3 | Depois de desfazer o botao fica desabilitado ate a proxima organizacao e, se a pasta e a atual, ela e relida | PASS | organize_tab.py:375-381; test_a_proxima_organizacao_habilita_o_botao_de_novo, test_organizacao_de_outra_pasta_nao_rele_a_pasta_atual e mutacao M1 |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/ui/history_tab.py | 60-66 | `format_local_time` so captura `ValueError`; `format_local_time("0001-01-01T00:00:00Z")` levanta `OverflowError: date value out of range` (medido). Uma linha com `started_at` fora de faixa derruba `_load_page` com `_rows` e `page` ja trocados e o modelo sem atualizar | Capturar `(ValueError, OverflowError, OSError)` e devolver `started_at` como veio; acrescentar teste com esse valor | nao |
| 2 | filepilot/ui/organize_tab.py | 349-383 | `undo()` e `_on_undone` nao escondem a barra de progresso (`progress.setVisible(False)` so existe em :111, :251, :260 e :269); depois de organizar e desfazer, a barra da organizacao anterior ("N de N arquivos") continua visivel junto de "Desfeito: ..." (conferido por leitura, nao medido ao vivo) | Chamar `self.progress.setVisible(False)` no inicio de `undo()` | nao |
| 3 | tests/ui/test_undo_button.py | 214-237 | O teste nao troca `QMessageBox.information` nem libera o evento em `finally`; com a mutacao M2 ele falhou e o pytest travou no encerramento (janela com `organizing` verdadeiro abre o aviso modal de fechar; processo encerrado por mim) | Trocar `main_window_module.QMessageBox.information` por um dubl e chamar `release.set()` em `finally`, como em tests/ui/test_organize_states.py | nao |
| 4 | tests/ui/test_history_tab.py, tests/ui/test_history_details.py, tests/ui/test_undo_button.py | test_history_tab.py:73-76, test_history_details.py:199, test_undo_button.py:227 | `# type: ignore` em testes (principio 6 do Carlos) porque `_rows` recebe `model: object`; alem disso a data esperada em test_history_tab.py:105-107 usa a propria `format_local_time` (so o teste de :111-120 calcula a data de forma independente) | Tipar o parametro como `QAbstractItemModel` e usar `datetime`/`astimezone` no teste de lista, sem `type: ignore` | nao |
| 5 | filepilot/ui/organize_worker.py, filepilot/ui/organize_tab.py | organize_worker.py:1-6, organize_tab.py:71 | Comentarios desatualizados: o docstring do modulo so cita `organize` e o da `OrganizeTab` nao cita desfazer nem "Ver detalhes"; alem disso `undo()` sem `db_path` so mostra o resumo (organize abre `QMessageBox.critical`), diferenca nao documentada | Atualizar os dois docstrings e dizer em comentario que o desfazer nao abre dialogo (SPEC 7.2 so pede o resumo) | nao |
