# filepilot-v1-11 - Aba Historico e desfazer na interface
Epico: filepilot-v1 | Ordem: 11 | Pontos: 5 | Depende de: filepilot-v1-7,filepilot-v1-9,filepilot-v1-10

## Objetivo
A aba Historico lista organizacoes e detalhes por arquivo, o botao Ver detalhes abre a organizacao com falhas e o botao Desfazer restaura a ultima organizacao pela interface.

## Contexto herdado
Do item filepilot-v1-7 (commit 7f98bbb):

Artefatos criados:
- filepilot/services/history.py - servico - `list_organizations`, `get_organization_detail`, `last_undoable` e os tipos `OrganizationRow`, `OperationRow`, `OrganizationPage`
- filepilot/services/undo.py - servico - `undo_last` e o tipo `UndoResult`

Contratos:
- `list_organizations(conn, page=1, page_size=50) -> OrganizationPage` (`items`, `page`, `page_size`, `total`); `page` menor que 1 vira 1 e `page_size` fora de 1 a 200 vira 50, entao use `page` e `page_size` da pagina devolvida, nao os pedidos.
- `get_organization_detail(conn, organization_id) -> list[OperationRow]`, por `seq` crescente; id inexistente devolve lista vazia.
- `last_undoable(conn) -> OrganizationRow | None`: habilita o botao Desfazer. Devolve `None` quando a ultima organizacao esta `desfeita`, `em_andamento` ou sem arquivos movidos; nao ha retrocesso.
- `undo_last(conn) -> UndoResult` (`organization_id`, `restored_count`, `not_restored: list[tuple[str, str]]`, `removed_folders`). Levanta `NADA_PARA_DESFAZER`, `ORGANIZACAO_EM_ANDAMENTO` e `BANCO_INDISPONIVEL` como `FilePilotError`, com as mensagens da SPEC em `.message`.
- Armadilha: `undo_last` pega `OPERATION_LOCK` sem bloquear, entao deve rodar fora da thread da interface e a interface trata `ORGANIZACAO_EM_ANDAMENTO`. Um texto de `not_restored` fora da SPEC: "caminho original fora da pasta escolhida".

Nomes decididos:
- Os tipos de linha vivem em `history.py`, nao em `filepilot/domain/models.py`.

Padroes estabelecidos:
- Erros de contrato por modulo: dicionario `_MESSAGES` e funcao `_error(code)`, como em `organizer.py`.

O item filepilot-v1-7 entregou os servicos de historico e de desfazer e seus testes; a interface NAO deve reimplementar consulta ao banco nem a restauracao.

Do item filepilot-v1-9 (commit f779c72):

Artefatos criados:
- filepilot/ui/organize_tab.py - interface - exporta `OrganizeTab(conn)` e as constantes `MODE_EMPTY`, `MODE_LOADING`, `MODE_LISTED`, `MODE_SIMULATED`, `MODE_ORGANIZING` e `MODE_ERROR`
- filepilot/ui/file_table.py - interface - exporta `FileTableView`, `FileTableModel`, `HEADERS`, `CUSTOM_RULE`, `NO_CATEGORY` e `EMPTY_MESSAGE`
- tests/ui/test_file_table.py, tests/ui/test_organize_tab_folder.py e tests/ui/test_organize_tab_simulate.py - testes - 31 casos da aba, da tabela e da simulacao
- .abt/reviews/filepilot-v1-9.md - relatorio - veredito APROVADO da Rita

Contratos:
- `OrganizeTab(conn: sqlite3.Connection)` (organize_tab.py) guarda `folder: Path | None`, `files`, `plan: Plan | None` e `mode: str` (comeca em `vazio`), com os widgets publicos `folder_edit`, `choose_button`, `refresh_button`, `table`, `simulate_button`, `organize_button` e `summary`; `build_tabs` ja cria a aba no indice 0 com a conexao da janela.
- Metodos publicos `choose_folder()`, `refresh()` e `simulate()`; `refresh()` relê a pasta, recalcula o plano com `list_rules` e volta a `listado`, entao e o que o fim da organizacao chama para reescanear. `_read_folder(folder) -> Plan | None` e privado e devolve `None` ao mostrar o erro.
- `_update_buttons()` decide tudo pelo `mode`: Escolher pasta e Atualizar ficam desabilitados em `carregando` e `organizando`; Simular so em `listado` e `simulado`; Organizar em `listado` ou `simulado` com plano nao vazio. Nada coloca a aba em `organizando` ainda.
- `organize_button` ja habilita pela regra da SPEC 7.2, mas NAO tem `clicked` ligado: a execucao, a conferencia da simulacao, o `OrganizeWorker`, a barra de progresso e o `MainWindow.organizing` sao deste item; Desfazer, "Ver detalhes" e `organization_finished` ainda nao existem. O `ActionBar` e um `QHBoxLayout` local de `_build_layout` (Simular, Organizar e um `addStretch` no fim) e o `summary` fica abaixo dele; promova a atributo o que precisar.
- `FileTableView.set_rows(files, plan, show_destination=True)`: em `listado` a aba passa `show_destination=False` (categoria prevista, destino vazio); em `simulado`, `True`. A coluna Categoria mostra a subpasta, "Regra personalizada" ou "sem categoria".
- Armadilha: `build_tabs` continua sem acesso a janela, entao o caminho para ligar `MainWindow.organizing` e emitir `organization_finished` ao `HistoryTab` ainda precisa ser criado (por exemplo, sinais conectados em `MainWindow.__init__`).
- Achado aberto da Rita (nao bloqueou): `_read_folder` captura so `FilePilotError`; um `OSError` do `scan_folder` (relancado em scanner.py `_resolve_folder`) deixa `mode` em `carregando` com os botoes desabilitados. Ao tocar a leitura da pasta, trate `OSError` e va para `erro`.

Nomes decididos:
- Os estados `mode` sao constantes publicas `MODE_*` em organize_tab.py; os textos ficam em constantes privadas (`_CHOOSE_FOLDER`, `_LOADING`, `_NO_OPERATIONS`, `_NOT_CHANGED`).

Padroes estabelecidos:
- Os testes da aba usam uma fixture `conn` com `open_connection(tmp_path / "db" / "filepilot.db")` e trocam o seletor por `monkeypatch.setattr(organize_tab_module.QFileDialog, "getExistingDirectory", lambda *a, **k: str(pasta))`.
- A interface nao usa `os` nem `shutil`; `sqlite3` so entra nas anotacoes de tipo.

O item filepilot-v1-9 entregou a aba, a tabela e a simulacao: NAO reimplementar a escolha da pasta, a lista, o Simular nem o Atualizar.

Do item filepilot-v1-10 (commit 09e3902):

Artefatos criados:
- filepilot/ui/organize_worker.py - interface - exporta `OrganizeWorker(plan, db_path)` (sinais `progress(int, int, str)`, `finished(object)` e `failed(str, str)`) e `run_in_thread(worker) -> QThread`
- filepilot/ui/organize_tab.py - interface (alterado) - `OrganizeTab(conn, db_path=None)`, com `organize()`, a barra `progress` e os sinais `organization_finished(int)` e `organizing_changed(bool)`
- filepilot/ui/main_window.py - interface (alterado) - `build_tabs(conn, db_path=None)` passa o caminho do banco a aba, e `MainWindow._set_organizing(bool)` espelha `organizing_changed` em `MainWindow.organizing`
- tests/ui/test_organize_worker.py, tests/ui/test_organize_confirm.py e tests/ui/test_organize_states.py - testes - 19 casos do worker, da conferencia da simulacao e dos estados
- .abt/reviews/filepilot-v1-10.md - relatorio - veredito APROVADO com Gate UI-1 DEFERIDO, smoke ao vivo feito pelo Ivan em 2026-10-12

Contratos:
- `organization_finished = Signal(int)` e emitido no fim de `OrganizeTab._on_finished`, depois da releitura da pasta e de `organizing_changed(False)`, e leva so o `organization_id`. O `failed_count` do resultado existe apenas dentro de `_on_finished` (`OrganizationResult`); o botao "Ver detalhes" precisa dele (ou do detalhe lido do banco), entao o sinal ou a aba precisam expor esse dado. O resumo "Concluído: X movidos, Y falhas." e o `QLabel` `summary`.
- A ligacao com a janela ja existe e e o modelo para o Historico: o laco de `MainWindow.__init__` (main_window.py:65-68) percorre `build_tabs` e conecta `organizing_changed` quando a aba e `OrganizeTab`; conecte `organization_finished` da mesma forma ao `HistoryTab` (recarregar a lista e reavaliar `last_undoable`).
- `OrganizeTab.organize()` roda o `OrganizeWorker` em `QThread` e `MainWindow.organizing` fica verdadeiro ate o fim; `undo_last` pega o mesmo `OPERATION_LOCK` sem bloquear, entao Desfazer fica desabilitado com `organizing` verdadeiro e roda fora da thread da interface (um `run_in_thread` hoje so aceita `OrganizeWorker`).
- Armadilha: `run_in_thread` devolve a `QThread` sem dono; quem chama guarda o worker e a thread, espera a thread acabar (`wait`) e so entao solta os dois. O `quit` e ligado por `DirectConnection` a `finished` e `failed`; com conexao enfileirada o `wait` do slot travava.
- Armadilha: depois de organizar tudo, a releitura da pasta devolve `PASTA_VAZIA`; `_read_folder(folder, empty_ok=True)` trata isso como lista vazia so no fim da organizacao. Fora dali, pasta sem arquivos continua sendo o erro `PASTA_VAZIA`.
- `OrganizeTab(conn)` sem `db_path` continua valido para testes; `organize()` nele mostra `BANCO_INDISPONIVEL` e nao move nada. A `MainWindow` sempre passa o caminho.

Nomes decididos:
- Os sinais da aba sao `organization_finished` e `organizing_changed`; o estado da janela segue `MainWindow.organizing`.
- O worker abre a propria conexao pelo `db_path` (a conexao SQLite de `conn` nao atravessa threads).

Padroes estabelecidos:
- Os testes que organizam de verdade esperam `qtbot.waitSignal(tab.organization_finished)` e usam `OrganizeTab(conn, folder.parent / "db" / "filepilot.db")`; falha de worker e simulada trocando `organize` em `organize_worker_module` e `QMessageBox.critical` por dubles com `monkeypatch`.
- Teste que usa `run_in_thread` chama `thread.wait()` antes de terminar, para nao derrubar o processo.

O item filepilot-v1-10 entregou a execucao da organizacao com barra de progresso, a conferencia da simulacao e os estados da aba: NAO reimplementar o `OrganizeWorker`, a releitura nem o bloqueio de fechamento.

## Features

### filepilot-v1-11-f1 HistoryTab com paginacao e detalhes por organizacao
Linhas da SPEC: .abt/SPEC.md L479-498
Arquivos:
- filepilot/ui/history_tab.py (novo)
- filepilot/ui/main_window.py (novo)
- tests/ui/test_history_tab.py (novo)
Criterios de aceite:
- A lista mostra as organizacoes da mais recente para a mais antiga, com as colunas Data e hora (formato dd/MM/yyyy HH:mm no horario local), Pasta, Movidos, Falhas e Situação ("Concluída", "Interrompida", "Desfeita", "Em andamento").
- Selecionar uma organizacao mostra, no painel direito, Arquivo, Origem, Destino final, Situação ("Movido", "Falha", "Restaurado", "Não restaurado") e Detalhe de cada operacao; sem selecao mostra "Selecione uma organização.".
- Historico vazio mostra "Nenhuma organização registrada ainda."; falha de leitura mostra a mensagem de `BANCO_INDISPONIVEL` e o botao "Tentar de novo".
- "Anterior" fica desabilitado na pagina 1 e "Próxima" quando `page * 50` e maior ou igual a `total`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_history_tab.py -> exit 0
- parser: python -m py_compile filepilot/ui/history_tab.py -> exit 0
- grep deve casar: Nenhuma organização registrada ainda. em filepilot/ui/history_tab.py
- dependencias: PySide6 em pyproject.toml
Dicas:
- Use `list_organizations` e `get_organization_detail` (item filepilot-v1-7); a aba nunca importa `sqlite3`.
- Troque o marcador "Histórico" criado por `build_tabs` (item filepilot-v1-8) pelo `HistoryTab` real; ao receber `organization_finished` recarregue a pagina 1.
- A simulacao nunca aparece no historico.

### filepilot-v1-11-f2 Estados do detalhe e show_organization
Linhas da SPEC: .abt/SPEC.md L479-498
Arquivos:
- filepilot/ui/history_tab.py (novo)
- filepilot/ui/organize_tab.py (novo)
- tests/ui/test_history_details.py (novo)
Criterios de aceite:
- Enquanto `get_organization_detail` carrega, o painel direito mostra "Carregando detalhes..."; organizacao sem operacoes mostra "Nenhum arquivo nesta organização.".
- `HistoryTab.show_organization(organization_id)` carrega a pagina que contem a organizacao, seleciona a linha e mostra os detalhes.
- O botao "Ver detalhes" da aba Organizar so aparece com `failed_count` maior que 0, abre a aba "Histórico" com aquela organizacao selecionada e some ao escolher outra pasta, atualizar ou iniciar nova organizacao.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_history_details.py -> exit 0
- grep deve casar: show_organization em filepilot/ui/history_tab.py
- grep deve casar: Carregando detalhes em filepilot/ui/history_tab.py
Dicas:
- A coluna Detalhe mostra o `error_message` ja amigavel (SPEC 6.7, L377-402).
- O botao "Ver detalhes" fica ao lado do resumo da `OrganizeTab` (SPEC 7.2).

### filepilot-v1-11-f3 Botao Desfazer ultima organizacao
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_tab.py (novo)
- tests/ui/test_undo_button.py (novo)
Criterios de aceite:
- "Desfazer última organização" so fica habilitado quando `last_undoable` nao e `None` e `organizing` e falso, reavaliado ao abrir a aba e depois de organizar ou desfazer.
- Ao clicar, executa `undo_last` e o resumo mostra "Desfeito: X arquivos restaurados."; com `not_restored` nao vazio acrescenta "Não restaurados: " seguido dos caminhos.
- Depois de desfazer, o botao fica desabilitado ate a proxima organizacao e, se a pasta for a atual, ela e relida.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_undo_button.py -> exit 0
- grep deve casar: last_undoable em filepilot/ui/organize_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Fluxo 8.2 (L541-550); nenhum dialogo de confirmacao ao desfazer (decisao registrada em 15.2, L659-669).
- `UndoResult` tem `restored_count`, `not_restored` e `removed_folders` (SPEC 6.5, L335-350).

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
