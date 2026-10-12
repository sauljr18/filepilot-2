# filepilot-v1-10 - Aba Organizar: execucao com barra de progresso
Epico: filepilot-v1 | Ordem: 10 | Pontos: 5 | Depende de: filepilot-v1-5,filepilot-v1-6,filepilot-v1-9

## Objetivo
O botao Organizar executa o plano em thread de trabalho com barra de progresso, conferencia da simulacao exibida e resumo de movidos e falhas, sem travar a janela.

## Contexto herdado
Entregue por filepilot-v1-6 (commit 0d5f566). Nao reimplementar: as verificacoes de destino (caminho acima de 259, subpasta que e atalho em cada nivel, guarda de pasta), os textos de falha de 6.7 e a classificacao de `ERRO_INTERNO`. Elas ja existem e tem testes proprios; `organize` so as usa.

Artefatos criados:
- filepilot/services/destination_checks.py - servico - exporta `check_destination(folder, destination) -> str | None`, `has_shortcut(folder, directory) -> bool`, `failure_text(exc: OSError, creating: bool) -> str` e as constantes de texto `IN_USE`, `NO_PERMISSION`, `NOT_FOUND`, `TOO_LONG`, `SHORTCUT`, `OUTSIDE`, `MKDIR`, `OTHER`, `MAX_PATH`
- tests/services/test_destination_checks.py - testes - 259 e 260, link simbolico, cada nivel da subpasta e junction (so no Windows)
- tests/services/test_failure_messages.py - testes - os 5 textos gravados em `operations.error_message` e `internal_error`
- tests/test_repository_rules.py - testes - zero `os.replace`, `shutil.move`, `os.remove`, `unlink` e `shutil.rmtree` em `filepilot/services`, zero `socket`, `http`, `urllib` e `requests` em `filepilot`
- .abt/reviews/filepilot-v1-6.md - relatorio - veredito APROVADO da Rita

Contratos:
- `internal_error(exc: BaseException) -> FilePilotError` (filepilot/services/organizer.py:42): devolve `FilePilotError` como esta e converte qualquer outra excecao em `FilePilotError("ERRO_INTERNO", "Ocorreu um erro inesperado. Tente de novo.")`, sem o texto bruto. Armadilha: `organize` NAO a chama, e `test_a_trava_e_liberada_depois_de_uma_excecao` exige `RuntimeError` cru de `organize`; quem converte e o `OrganizeWorker` deste item, no sinal `failed(code, message)`.
- `organize` (organizer.py) mantem a assinatura `organize(plan, conn, progress_callback=None) -> OrganizationResult`; `failures` e uma lista de `(nome do arquivo, motivo)`.
- Achados abertos da Rita (nao bloqueiam): o detector de `test_repository_rules.py` nao pega alias como `import shutil as sh`; o comentario de decisao do v1-4 em organizer.py:19 ficou acima do import de `destination_checks`.

Nomes decididos:
- Os nomes `check_destination`, `has_shortcut` e `failure_text` sao publicos (sem `_`); `_is_shortcut` continua privado em destination_checks.py.

Padroes estabelecidos:
- Os testes de falha por arquivo gravam em `operations.error_message` e conferem `RAW_TEXT not in message`; a conexao do banco abre antes de qualquer `monkeypatch` global, como o de `Path.mkdir`.
- Link simbolico em teste pula com `pytest.skip` quando o sistema nega; junction usa `skipif(os.name != "nt")`.

O item filepilot-v1-6 entregou as verificacoes, os textos e a classificacao de `ERRO_INTERNO`: NAO reimplementar; o worker deste item so liga `progress_callback` a sinais e converte a excecao com `internal_error`.

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

## Features

### filepilot-v1-10-f1 OrganizeWorker e barra de progresso
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_worker.py (novo)
- filepilot/ui/organize_tab.py (novo)
- tests/ui/test_organize_worker.py (novo)
Criterios de aceite:
- Organizar roda `OrganizeWorker` em `QThread`; a barra tem faixa de 0 a N, texto "%v de %m arquivos" e termina em 100% com o resumo "Concluído: X movidos, Y falhas.".
- O worker emite `progress(done, total, filename)`, `finished(result)` e `failed(code, message)`, ligados ao `progress_callback` do servico.
- Terminado o worker, a pasta e relida, `mode` volta a `listado` e a aba emite `organization_finished` com o id da organizacao.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_worker.py -> exit 0
- parser: python -m py_compile filepilot/ui/organize_worker.py -> exit 0
- grep deve casar: QThread em filepilot/ui/organize_worker.py
- grep deve casar: %v de %m arquivos em filepilot/ui/organize_tab.py
Dicas:
- O servico `organize` nunca importa PySide6; so o worker liga o `progress_callback` a um sinal Qt (SPEC 3.2).
- Teste o worker pelos sinais com `qtbot.waitSignal`, sem janela visivel.
- Confirme na versao PySide6 6.12.0 a assinatura de `Signal` e de `qtbot.waitSignal`.

### filepilot-v1-10-f2 Conferencia da simulacao antes de organizar
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_tab.py (novo)
- tests/ui/test_organize_confirm.py (novo)
Criterios de aceite:
- Organizar relê a pasta e recalcula o plano com as regras atuais; com `mode` igual a `simulado` e plano novo diferente do exibido (compara `source_path`, `destination_path` e `rule_name`), nada e movido, a tabela mostra o plano novo e aparece "A pasta mudou desde a simulação. Confira a nova simulação e clique em Organizar de novo.".
- Com `mode` igual a `listado` (sem simulacao) ou plano igual ao exibido, a organizacao e executada.
- Plano recalculado vazio nao executa, mostra "Não há operações para executar." e desabilita Organizar.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_confirm.py -> exit 0
- grep deve casar: A pasta mudou desde a simulação em filepilot/ui/organize_tab.py
Dicas:
- Fluxo 8.1 (L524-540): sem simular, Organizar relê a pasta, recalcula e executa.
- Compare listas de tuplas `(source_path, destination_path, rule_name)` na mesma ordem.

### filepilot-v1-10-f3 Estados durante a organizacao e erro inesperado
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_tab.py (novo)
- filepilot/ui/main_window.py (novo)
- tests/ui/test_organize_states.py (novo)
Criterios de aceite:
- Durante a organizacao Simular, Organizar, Atualizar e Escolher pasta ficam desabilitados e `MainWindow.organizing` e verdadeiro; ao fim todos voltam e `organizing` e falso.
- `failed(code, message)` mostra `QMessageBox.critical` com a mensagem e `mode` vai para `erro`; excecao inesperada mostra "Ocorreu um erro inesperado. Tente de novo." e a janela continua aberta.
- Fechar a janela durante a organizacao continua bloqueado pelo `closeEvent` do item filepilot-v1-8.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_states.py -> exit 0
- grep deve casar: organizing em filepilot/ui/organize_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- A trava `OPERATION_LOCK` do servico impede a segunda organizacao; a interface so desabilita botoes (SPEC 6.3, ultimo item).
- Os textos de erro vem da tabela de codigos da secao 6 (L232-259).

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
