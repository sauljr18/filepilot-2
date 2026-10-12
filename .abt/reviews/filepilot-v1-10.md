# Validacao do item filepilot-v1-10 - Aba Organizar: execucao com barra de progresso

**Item:** filepilot-v1-10 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-160136
Veredito: APROVADO - Gate UI-1 DEFERIDO (smoke ao vivo pendente)
Transicoes a cobrir no smoke: vazio -> carregando -> listado; listado -> organizando -> listado; simulado -> simulado (aviso de pasta mudou); organizando -> erro (falha do worker); listado -> erro (sem db_path)
**Tipo do item:** interface (com um worker de execucao em thread; sem endpoints)

Revalidacao completa, do zero, depois da rejeicao com retorno a `execucao`. Skills ignoradas por nao serem da stack do projeto (Python 3.12 e PySide6): `optimizing-ef-core-queries`, `run-tests` (.NET), `test-anti-patterns` (.NET), `coverage-analysis`, `vuetify-sneat-ui-patterns` e `go-senior-engineer`. Os gates de teste vieram da `Verificacao:` do detalhe do item.

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot`: exit 0, "no issues found in 24 source files"; `comm -13` contra a baseline do Carlos sem linha de erro nova |
| 2 Criterios de aceite | PASS | 9/9 criterios atendidos (tabela abaixo) |
| 3 Qualidade de codigo | PASS | zero `TODO`/`placeholder`/`not implemented`/`FIXME`, zero `print`, zero `type: ignore`, zero travessao ou aspas tipograficas; `grep` por `.execute(`, `PRAGMA`, `database_list`, `import os` e `shutil` em `filepilot/ui` sem resultado (fronteira da SPEC 3.2 L89 respeitada); docstrings do modulo e da classe cobrem a organizacao |
| 4 Autorizacao e seguranca | PASS | n/a: o item nao tem endpoint; o texto bruto de excecao nao chega a pessoa (`test_excecao_inesperada_mostra_o_texto_generico_e_a_janela_continua_aberta`) |
| 5 Testes | PASS | suite completa 421 passed, 2 skipped (Windows, com justificativa no `-rs`); `tests/ui` 109 passed; os 3 arquivos novos (19 testes) rodaram 60 vezes sem falha; cada modulo novo tem teste |
| 6 Consistencia entre documentos | PASS | nomes, textos e sinais batem com a SPEC 7.2 (L434-458) e o contexto herdado; `db_path` vem da janela, como a SPEC L129 e L421 mandam; `OrganizeWorker(plan, db_path)` bate com a L450 |
| 7b Varredura adversarial | PASS | consumidores de `organizing`: so o `closeEvent` (`main_window.py:82-83`); todos os chamadores de `OrganizeTab(` e `build_tabs(` seguem validos com o parametro opcional (testes de v1-8 e v1-9 passam sem mudanca); `internal_error` do servico reusado (`organize_worker.py:14`) |
| 7c Degradacao e borda | PASS | as 4 perguntas sem "sim": pasta vazia depois de organizar tratada (`organize_tab.py:169-185`); plano vazio nao inicia worker; `db_path` ausente vira `BANCO_INDISPONIVEL` sem mover nada; comentarios conferidos e verdadeiros |
| 7d Matriz (interface) | DEFERIDO | UI-1 DEFERIDO; UI-2 PASS (carregando, vazio e erro presentes); UI-3 n/a; UI-4 com a lista acima |
| 7e Funcao irma e comando citado | PASS | `organize` repete o que as irmas `simulate` e `refresh` fazem (esconde a barra, le a pasta antes de decidir); nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-10-f1 | Organizar roda `OrganizeWorker` em `QThread`; barra de 0 a N, texto "%v de %m arquivos", termina em 100% com "Concluído: X movidos, Y falhas." | PASS | `organize_tab.py:247-263` (worker e `run_in_thread`), `organize_worker.py:54-61` (`QThread`), `organize_tab.py:256` (`setRange`), `:39` e `:98` (formato), `:280-285` (100% e resumo); `test_organizar_mostra_a_barra_e_o_resumo_final`, `test_resumo_conta_as_falhas_por_arquivo` |
| filepilot-v1-10-f1 | O worker emite `progress(done, total, filename)`, `finished(result)` e `failed(code, message)`, ligados ao `progress_callback` | PASS | `organize_worker.py:20-22` (sinais), `:35` (`self.progress.emit` como callback); `test_worker_emite_progresso_e_resultado_em_outra_thread` |
| filepilot-v1-10-f1 | Terminado o worker, a pasta e relida, `mode` volta a `listado` e a aba emite `organization_finished` com o id | PASS | `organize_tab.py:277-287` (releitura, `_show_listed` em `:155`, emissao em `:287`); `test_depois_de_organizar_a_pasta_e_relida` |
| filepilot-v1-10-f2 | Plano novo diferente do exibido (com `simulado`): nada e movido, tabela mostra o plano novo, aparece o aviso | PASS | `organize_tab.py:241-244`, `:57-64` (compara origem, destino e regra); `test_pasta_mudou_depois_da_simulacao_nao_move_nada`, `test_regra_alterada_depois_da_simulacao_tambem_e_mudanca` |
| filepilot-v1-10-f2 | Com `listado` ou plano igual, a organizacao e executada | PASS | `organize_tab.py:245`; `test_simulacao_igual_ao_plano_novo_executa`, `test_sem_simulacao_le_a_pasta_e_move_o_arquivo_novo` |
| filepilot-v1-10-f2 | Plano recalculado vazio nao executa, mostra "Não há operações para executar." e desabilita Organizar | PASS | `organize_tab.py:234-240` e `:137` (botao); `test_plano_recalculado_vazio_depois_da_simulacao_nao_executa`, `test_plano_recalculado_vazio_sem_simulacao_nao_executa` |
| filepilot-v1-10-f3 | Durante a organizacao os quatro botoes ficam desabilitados e `MainWindow.organizing` e verdadeiro; ao fim todos voltam e `organizing` e falso | PASS | `organize_tab.py:131-137` e `:260-261`, `:286`; `main_window.py:67-68` e `:72-73`; `test_durante_a_organizacao_os_botoes_ficam_desabilitados_e_a_janela_bloqueia` |
| filepilot-v1-10-f3 | `failed` mostra `QMessageBox.critical` com a mensagem e `mode` vai para `erro`; excecao inesperada mostra o texto generico e a janela continua aberta | PASS | `organize_tab.py:289-294`, `organize_worker.py:38-41`; `test_falha_de_contrato_mostra_a_mensagem_e_vai_para_erro`, `test_excecao_inesperada_mostra_o_texto_generico_e_a_janela_continua_aberta`, `test_aba_sem_caminho_do_banco_mostra_banco_indisponivel_e_nao_organiza` |
| filepilot-v1-10-f3 | Fechar a janela durante a organizacao continua bloqueado pelo `closeEvent` do v1-8 | PASS | `main_window.py:82-86` (inalterado) e `test_organize_states.py:107-109` (`window.close() is False` com o aviso) |

## Conferencia da rejeicao anterior

| # | Achado da rodada anterior | Situacao | Evidencia |
|---|---------------------------|----------|-----------|
| 1 | SQL direto na interface (`PRAGMA database_list`) | corrigido | `_database_path` removido; `OrganizeTab(conn, db_path=None)` em `organize_tab.py:78-81`, `build_tabs(conn, db_path=None)` em `main_window.py:36-38`, passado em `:65`; grep de `.execute(` e `PRAGMA` em `filepilot/ui` sem resultado |
| 2 | Docstrings do modulo e da classe desatualizadas | corrigido | `organize_tab.py:1` e `:68-72` |
| 3 | Resumo "Y falhas" so testado com 0 | corrigido | `test_resumo_conta_as_falhas_por_arquivo` (`test_organize_worker.py:209`): 1 movido e 1 falha, linha do banco `(1, 1)` |

## Evidencia dos gates

- Gate 1: `exit=0`; baseline do Carlos com o mesmo "Success" (23 arquivos, agora 24 com o worker).
- Gates da `Verificacao:`: `py_compile` de `organize_worker.py` exit 0; `grep QThread` em `organize_worker.py` casa (linhas 10, 46, 54); `grep "%v de %m arquivos"` casa em `organize_tab.py:39`; `grep "A pasta mudou desde a simulação"` casa em `:42`; `grep organizing` casa em `:75-76`; `grep -P` de travessao e aspas tipograficas em `filepilot` sem saida; `awk` do Passo 6 sem saida.
- Estabilidade de thread: o `quit` e ligado por `DirectConnection` (`organize_worker.py:59-60`), o que removeu um travamento intermitente que apareceu antes; 60 repeticoes dos testes do item sem falha.
- Afinidade de thread (verificada na rodada anterior com sonda em `/tmp`, sem mudanca de codigo no mecanismo): as leituras da pasta depois do worker rodam na thread da interface.
- Mutacao refeita pela Rita (escopo: suite completa, `pytest -q`; reversao por copia de arquivo, com o original guardado fora do repositorio):

  | Mutacao | Diff | Resultado |
  |---------|------|-----------|
  | Resumo fixa `0 falhas` no lugar de `{result.failed_count}` | `organize_tab.py:284`: `{result.moved_count} movidos, {result.failed_count} falhas.` vira `{result.moved_count} movidos, 0 falhas.` | `1 failed, 420 passed, 2 skipped`: `test_organize_worker.py::test_resumo_conta_as_falhas_por_arquivo` (`AssertionError` em `:229`) |

  Mesmo numero que o Carlos informou (1 failed, 420 passed). Revertida por `cp`, com `diff` confirmando arquivo identico ao original e `grep` confirmando a linha. `git status --short` e `git diff --stat` iguais aos do inicio (2 arquivos, +139 -11, mais 4 arquivos novos e este relatorio).

## Gate UI-1 (DEFERIDO) e observacoes que nao decidem

- UI-1: o smoke ao vivo e do Ivan, no `avanco`, antes do commit. Atencao para quem decide: a skill `smoke-e2e-playwright` descreve smoke de pagina web, e o FilePilot e um aplicativo de desktop PySide6; ela nao se aplica como esta escrita. A cobertura atual e `pytest-qt` em modo `offscreen` (109 testes de interface). A pessoa decide se isso basta ou se quer um smoke manual do executavel.
- Decisao do Carlos a confirmar: `db_path` ficou opcional (`None`) para manter o contrato herdado `OrganizeTab(conn)` e os testes do v1-9; sem ele, Organizar mostra `BANCO_INDISPONIVEL` e nao move nada (`organize_tab.py:249-251`). A `MainWindow` sempre o passa.
- Decisao do Carlos a confirmar: depois de organizar tudo a pasta fica sem arquivos e a releitura devolveria `PASTA_VAZIA`; `empty_ok` (`organize_tab.py:169-185`) trata isso como lista vazia, so nesse caminho. Coerente com a SPEC 8.1 (L531).
- Fora do item, como o contexto herdado ja previa: "Ver detalhes", "Desfazer última organização" e a ligacao de `organization_finished` ao Historico (v1-11) nao existem ainda.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| - | - | - | nenhuma correcao pendente | - | - |
