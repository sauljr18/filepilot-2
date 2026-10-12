# Validacao do item filepilot-v1-7 - Historico e desfazer a ultima organizacao

**Item:** filepilot-v1-7 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-114028
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, 16 arquivos, zero erros; `comm` contra a baseline so lista a linha de sucesso com a nova contagem de arquivos (14 -> 16) |
| 2 Criterios de aceite | PASS | 10/10 criterios atendidos (tabela abaixo) |
| 3 Qualidade de codigo | PASS | zero `TODO`, `placeholder`, `not implemented`, `FIXME` e `print(`; sem codigo comentado; `py_compile` exit 0 nos dois arquivos de producao |
| 4 Autorizacao e seguranca | PASS | sem endpoint; consultas parametrizadas com `?`; guarda de NFR-001 sempre aplicada (`undo.py:53`); `rmdir` so apaga pasta vazia; `grep shutil.rmtree filepilot/services` sem ocorrencia |
| 5 Testes | PASS | `pytest` completo: 301 passaram, 2 ignorados (ambos "so no Windows", justificados no proprio teste); 50 testes novos, um arquivo por feature; sem mocks de excesso (so `os.rename` e `_record_status`, para forcar falha) |
| 6 Consistencia entre documentos | PASS | campos de `OrganizationRow` e `OperationRow` iguais as colunas de 5.3 e a tabela 16.3; mensagens iguais a tabela de erros da SPEC; ver divergencia do detalhe abaixo |
| 7b Varredura adversarial | PASS | sem coluna nova em entidade com CRUD; mensagens por modulo seguem a convencao de `organizer.py:31`, `planner.py:19`, `rules.py:12` e `scanner.py:13`; `OPERATION_LOCK` reusado de `organizer.py:29`, sem segundo lock |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim" decide; ver observacoes 2 e 3 |
| 7d Matriz (backend) | PASS | BE-1: sem criterio "nenhum ponto faz X" alem dos greps do item, todos com resultado correto; BE-2 e BE-3: n/a (sem conteiner de injecao nem policies) |
| 7e Funcao irma e comando citado | PASS | `undo_last` replica o lock nao bloqueante de `organize` (`undo.py:147` e `organizer.py:222`) e libera em `finally`; nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-7-f1 | `list_organizations` ordena por `started_at` desc com desempate por `id` desc, pagina em 50, vazio devolve `items` vazio e `total` 0 | PASS | `history.py:89`; `test_history.py` ordem, desempate, 55 registros em 50+5, vazio |
| filepilot-v1-7-f1 | `page` < 1 vira 1; `page_size` fora de 1 a 200 vira 50 | PASS | `history.py:81-84`; testes parametrizados (0, -1, 201, 1000 e limites 1 e 200) |
| filepilot-v1-7-f1 | `get_organization_detail` por `seq` crescente, lista vazia para id inexistente | PASS | `history.py:110`; `test_detalhe_ordena_por_seq_crescente`, `test_detalhe_de_organizacao_inexistente_e_lista_vazia` |
| filepilot-v1-7-f2 | `last_undoable` devolve `None` sem organizacoes, para `moved_count` 0 e para `desfeita`; devolve a linha para `concluida` ou `interrompida` com `moved_count` >= 1 | PASS | `history.py:129-147`; `test_last_undoable.py` (13 testes) |
| filepilot-v1-7-f2 | Nao ha retrocesso | PASS | `history.py:138` le so a ultima; `test_nao_ha_retrocesso_*` (2 testes) |
| filepilot-v1-7-f2 | Ao abrir o banco, toda linha `em_andamento` vira `interrompida` | PASS | `connection.py:15-35` (ja existia, fix-4); `test_organizacao_em_andamento_vira_interrompida_ao_abrir_o_banco` |
| filepilot-v1-7-f3 | `undo_last` restaura ao caminho e nome originais (inclusive com sufixo), grava `restaurado`, deixa `desfeita` com `undone_at`, `last_undoable` passa a `None` | PASS | `undo.py:50-62`, `undo.py:132`; `test_devolve_cada_arquivo...`, `test_restaura_arquivos_que_receberam_sufixo`, `test_grava_restaurado...` |
| filepilot-v1-7-f3 | Subpastas vazias removidas com `Path.rmdir`, subindo pelo pai ate a pasta escolhida (nunca removida); pasta com arquivo permanece | PASS | `undo.py:80-100`; `test_remove_subpastas...`, `test_sobe_pelo_pai...`, `test_subida_para_na_pasta...`, `test_pasta_com_arquivo_permanece` |
| filepilot-v1-7-f3 | Apagado vira `nao_restaurado` "arquivo não está mais no destino"; ocupado vira "caminho original ocupado"; nada sobrescrito | PASS | `undo.py:55-58`; `test_arquivo_apagado...`, `test_caminho_original_ocupado_nao_sobrescreve` |
| filepilot-v1-7-f3 | `ORGANIZACAO_EM_ANDAMENTO` durante organizacao; `NADA_PARA_DESFAZER` sem organizacao desfazivel | PASS | `undo.py:147-152`; `test_durante_organizacao_em_andamento...`, `test_sem_organizacao_desfazivel...` |

Verificacoes da `Verificacao:` das features e dos `## Gates do item`: mypy exit 0; `pytest` exit 0; `py_compile` exit 0; `page_size` casa em `history.py` (7 ocorrencias); `interrompida` casa em `connection.py` (2); `OPERATION_LOCK` casa em `undo.py` (3); `shutil.rmtree` em `filepilot/services` sem ocorrencia; Unicode proibido em `filepilot` sem ocorrencia; awk do Passo 6 sem saida.

## Lista de correcoes

Nenhuma correcao obrigatoria. Observacoes que a pessoa pode tratar agora ou depois:

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | .abt/items/filepilot-v1/filepilot-v1-7.md | 32-35 | A feature f2 lista `filepilot/db/connection.py` como "(novo)", mas o arquivo ja existia desde o fix-4 e ja faz a conversao; o item nao o altera | Corrigir o detalhe do item no product-spec; sem efeito no codigo | nao |
| 2 | filepilot/services/undo.py | 59-62 | Origem cuja pasta pai foi removida: `os.rename` levanta `FileNotFoundError`, que vira `nao_restaurado` com o texto do erro (confirmado so por leitura; o teste cobre `PermissionError`, nao este caso) | Acrescentar um teste com a pasta de origem removida | nao |
| 3 | filepilot/services/undo.py | 112-120 | Se a gravacao de um status falha no meio do laco, as linhas ja marcadas `restaurado` ficam e a organizacao continua `concluida`; um novo desfazer so processa as `movido` e o `restored_count` do resultado cobre so essa rodada | Aceitavel pela SPEC (falha do banco levanta `BANCO_INDISPONIVEL`); registrar se a interface precisar do total acumulado | nao |
| 4 | tests/services/test_last_undoable.py | 116 | `assert maior_id > 1` e vacuo; o teste ja prova o desempate pelo resultado `None` | Remover a linha | nao |
| 5 | .abt/items/filepilot-v1/filepilot-v1-7.md | 8 | `## Contexto herdado` esta `-`, embora o item dependa de filepilot-v1-1 e filepilot-v1-5 | Preencher a partir dos itens anteriores; nao afetou a entrega | nao |

Limite da validacao: a sondagem por script avulso (pasta de origem removida, observacao 2) foi negada pelo ambiente, e nao foi executada. Nao houve mutacao, porque o item nao declara prova por mutacao.
