# Validacao do item filepilot-v1-12 - Aba Regras e dialogo de regra

**Item:** filepilot-v1-12 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-125202
Veredito: APROVADO - Gate UI-1 DEFERIDO (smoke ao vivo pendente)
Transicoes a cobrir no smoke: carregando -> listado, carregando -> vazio, carregando -> erro, vazio -> listado (Nova regra), listado -> vazio (excluir a ultima regra), listado -> listado (editar, subir, descer, excluir com sobra), listado -> erro (falha do servico ao mover ou excluir)
**Tipo do item:** interface

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, 23 arquivos, zero erros; baseline do Carlos (21 arquivos, exit 0) sem diferenca alem da contagem de arquivos |
| 2 Criterios de aceite | PASS | 10/10 criterios atendidos (tabela abaixo) |
| 3 Qualidade de codigo | PASS | zero TODO, FIXME, placeholder de codigo, not implemented e print; zero `type: ignore`; 3 `noqa: N802` justificados (nomes do Qt) iguais aos de file_table.py; grep de Unicode proibido em `filepilot` sem resultado |
| 4 Autorizacao e seguranca | PASS | n/a: sem endpoint; sem dado sensivel; SQL so no servico (a aba nunca toca o banco) |
| 5 Testes | PASS | `pytest tests/ui` 79 passed; suite completa 380 passed e 2 skipped (os 2 so valem no Windows, justificados no proprio teste); 30 testes novos; mutacao refeita por mim: ver abaixo |
| 6 Consistencia entre documentos | PASS | nomes e textos batem com SPEC 7.5 (L499-521), SPEC 6.6 e `## Contexto herdado` (`list_rules`, `create_rule`, `update_rule`, `delete_rule`, `move_rule`, `fields`, `Reloadable`, `build_tabs`) |
| 7b Varredura adversarial | PASS | consumidor das regras e a aba Organizar, que chama `list_rules` a cada simulacao (organize_tab.py:135): criei regras pela aba e a simulacao seguinte usou a regra nova e a ordem nova; sem utilitario reinventado (a aba so chama o servico) |
| 7c Degradacao e borda | PASS | 2 observacoes desejaveis (itens 2 e 3 da lista), nenhuma regressao 5xx |
| 7d Matriz (interface) | DEFERIDO | UI-1 DEFERIDO; UI-2 PASS; UI-3 n/a; UI-4 lista acima |
| 7e Funcao irma e comando citado | PASS | nenhuma funcao de servico nova; nenhuma mensagem manda rodar comando |

### Evidencia do Gate 5 e do 7b

- Mutacao refeita por mim, por copia de arquivo: em `filepilot/ui/rules_tab.py:185` troquei `row is not None and row > 0` por `row is not None`. Escopo: `pytest tests/ui` inteiro. Resultado: 3 falhas (`test_ao_chegar_ao_extremo_o_botao_correspondente_desabilita`, `test_botoes_dependem_da_selecao_e_da_posicao`, `test_regra_unica_nao_sobe_nem_desce`), 76 passed. Revertida por `cp`, `.bak` removido, 79 passed; `git status --short` e `git diff --stat` iguais aos do inicio.
- Verificacao integrada com a `MainWindow` real em modo offscreen: aba Regras e `RulesTab`; vazia mostra o convite; criar pelo dialogo seleciona a regra; regra criada por fora aparece ao trocar de aba; a simulacao da aba Organizar enviou `balanco.xlsx` para `Trabalho/Planilhas` e `foto.png` para `Imagens`; Subir deixou a regra selecionada e desabilitou Subir na primeira linha; excluir renumerou sem lacuna e a ultima exclusao voltou ao convite.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-12-f1 | Lista por prioridade com as colunas Prioridade, Nome, Extensoes (separadas por virgula) e Subpasta | PASS | rules_tab.py:30, :83; test_rules_tab.py `test_lista_mostra_as_colunas_e_as_regras_por_prioridade` |
| filepilot-v1-12-f1 | Vazio mostra o convite exato; carregando mostra "Carregando regras..."; erro mostra a mensagem do servico | PASS | rules_tab.py:37-38, :195-198, :208, :213-214; testes `test_sem_regras...`, `test_durante_a_leitura...`, `test_erro_do_servico_mostra_a_mensagem_dele` |
| filepilot-v1-12-f1 | Editar, Excluir, Subir e Descer so habilitados com linha selecionada; Subir na primeira e Descer na ultima desabilitados | PASS | rules_tab.py:181-186; `test_botoes_dependem_da_selecao_e_da_posicao`, `test_regra_unica_nao_sobe_nem_desce`; mutacao acima |
| filepilot-v1-12-f2 | Campos Nome, Extensoes (separadas por virgula) e Subpasta de destino, obrigatorios, com Salvar e Cancelar | PASS | rule_editor_dialog.py:23-33, :87-89; `test_dialogo_tem_os_tres_campos_e_os_dois_botoes` |
| filepilot-v1-12-f2 | Salvar valida chama create_rule ou update_rule, emite `saved(rule_id)`, fecha com accept e a lista seleciona a regra | PASS | rule_editor_dialog.py:124-129, :156-157; rules_tab.py:245-246; `test_salvar_regra_valida...`, `test_salvar_em_edicao...`, `test_salvar_no_dialogo_recarrega_e_seleciona_a_regra` |
| filepilot-v1-12-f2 | REGRA_INVALIDA mostra a mensagem exata de `fields` em vermelho abaixo do campo, sem fechar; durante a gravacao o botao fica "Salvando..." e desabilitado | PASS | rule_editor_dialog.py:35, :118-122, :131-142; `test_regra_invalida_mostra_a_mensagem_exata...`, `test_durante_a_gravacao...` |
| filepilot-v1-12-f2 | BANCO_INDISPONIVEL mostra QMessageBox.critical e o dialogo continua aberto | PASS | rule_editor_dialog.py:142; `test_banco_indisponivel_mostra_critical...` |
| filepilot-v1-12-f3 | Excluir pergunta com o texto exato e botoes Excluir e Cancelar; Cancelar mantem; Excluir chama delete_rule | PASS | rules_tab.py:40, :250-266, :268-278; `test_excluir_pergunta...`, `test_cancelar_mantem...`, `test_excluir_chama_delete_rule...` (ver item 1 da lista: metodo estatico nao usado) |
| filepilot-v1-12-f3 | Subir e Descer chamam move_rule, atualizam a Prioridade e mantem a regra selecionada | PASS | rules_tab.py:288-297; `test_subir_move_a_regra...`, `test_descer_move_a_regra...` |
| filepilot-v1-12-f3 | Depois de excluir ou mover, posicoes de 1 a N sem lacuna | PASS | rules_tab.py:278, :297 recarregam do servico; `test_excluir_chama_delete_rule_e_reordena_sem_lacuna`, `test_subir_move_a_regra...` |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/ui/rules_tab.py | 250 | A SPEC 7.5 (L506) e o criterio dizem `QMessageBox.question`, mas a confirmacao usa uma instancia de `QMessageBox`, porque o metodo estatico nao permite os botoes "Excluir" e "Cancelar". O comportamento visivel (texto e botoes) esta correto e testado | A pessoa confirma que a instancia e aceitavel, ou ajusta a SPEC para dizer "caixa de pergunta" | nao |
| 2 | filepilot/ui/rules_tab.py | 243 | `RuleEditorDialog` e criado com a aba como pai e nunca liberado: cada abertura deixa um dialogo oculto como filho ate a aba ser destruida | `dialog.deleteLater()` depois do `exec()` | nao |
| 3 | filepilot/ui/rules_tab.py | 293 | `move_up` ou `move_down` chamado sem os botoes (primeira ou ultima linha) chega ao servico com posicao invalida (REGRA_INVALIDA) e a aba entra no estado de erro, escondendo a lista. Os botoes desabilitados impedem isso pela interface | Ignorar o movimento fora dos limites antes de chamar `move_rule` | nao |
| 4 | filepilot.egg-info/ e __pycache__/ | - | Nao rastreados, criados pelo ambiente virtual de teste (o repositorio nao tem `.gitignore`) | Nao commitar; o commit deve ser escopado aos 6 arquivos do item e a este relatorio | nao |
| 5 | smoke ao vivo | - | UI-1: o item toca tela, mas e um aplicativo desktop PySide6; o procedimento `smoke-e2e-playwright` e de navegador. O smoke e abrir o aplicativo e exercitar a aba Regras | Ivan faz o smoke antes do commit, cobrindo as transicoes listadas no topo | nao |
