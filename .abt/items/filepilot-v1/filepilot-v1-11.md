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
