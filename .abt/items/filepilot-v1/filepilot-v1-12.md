# filepilot-v1-12 - Aba Regras e dialogo de regra
Epico: filepilot-v1 | Ordem: 12 | Pontos: 5 | Depende de: filepilot-v1-3,filepilot-v1-8

## Objetivo
A aba Regras permite criar, editar, excluir com confirmacao e reordenar regras pelo dialogo, com a mensagem exata por campo invalido.

## Contexto herdado
Entregue por filepilot-v1-3 (commit 7dfc71c). Nao reimplementar: o servico de regras (CRUD, validacao por campo, normalizacao de extensoes, reordenacao sem lacuna e transacao unica por gravacao) e os testes de `tests/services`. A aba chama o servico; nao repete validacao nem renumeracao.

Artefatos criados:
- filepilot/services/rules.py - servico - exporta `list_rules`, `create_rule`, `update_rule`, `delete_rule` e `move_rule`
- tests/services/test_rules.py - testes - criar, listar e validacao por campo
- tests/services/test_rules_order.py - testes - editar, excluir e reordenar
- tests/services/test_rules_storage.py - testes - extensoes em `rule_extensions`, historico preservado e desfazer em falha
- .abt/reviews/filepilot-v1-3.md - relatorio - veredito APROVADO da Rita

Contratos:
- Todas as funcoes de `filepilot/services/rules.py` recebem `conn: sqlite3.Connection` primeiro (a de `open_connection`, em filepilot/db/connection.py). `list_rules(conn) -> list[Rule]` por `position` crescente; `create_rule(conn, name, extensions: list[str], destination_folder) -> Rule` (entra na ultima posicao); `update_rule(conn, rule_id, name, extensions, destination_folder) -> Rule` (mantem a `position`); `delete_rule(conn, rule_id) -> None`; `move_rule(conn, rule_id, new_position) -> list[Rule]` ja reordenada.
- `Rule` (filepilot/domain/models.py): `id`, `name`, `destination_folder`, `position`, `extensions: frozenset[str]` (sem ordem; a aba ordena para exibir).
- Erros (`FilePilotError` com `code`, `message` e `fields`): `REGRA_INVALIDA` traz `fields` por campo com chaves `name`, `extensions` e `destination_folder` (e `position` no `move_rule`) e o texto exato de 6.6, pronto para exibir no dialogo; `REGRA_NAO_ENCONTRADA` (id inexistente); `BANCO_INDISPONIVEL`. Todos os campos invalidos vem juntos em um so erro.
- Armadilha: cada gravacao abre a propria transacao com `BEGIN`; `conn` nao pode chegar com transacao aberta (o `BEGIN` falharia e viraria `BANCO_INDISPONIVEL`). O servico ja faz commit: a aba nao chama `conn.commit()`.
- Armadilha: o servico devolve o nome ja sem espacos nas pontas e as extensoes normalizadas; o dialogo deve reexibir o valor devolvido, nao o digitado. `move_rule` fora de 1 ate o total levanta `REGRA_INVALIDA`: a aba desabilita "Subir" e "Descer" nos extremos para nunca chegar a esse caso.
- Achados abertos do relatorio da Rita, que nao bloqueiam: destino com caractere de controle e aceito, `con.txt` e aceito (a SPEC reserva so o nome exato) e `BEGIN` deferido pode colidir em `UNIQUE (position)` com dois escritores (a instancia unica de filepilot-v1-8 mitiga).

Nomes decididos:
- Os helpers privados de rules.py sao `_validate`, `_transaction`, `_renumber`, `_normalize_extensions` e `_current_position`; os textos de erro ficam em `_MESSAGES` e `_FIELD_MESSAGES` do proprio modulo.
- A fixture `conn` dos testes de regras abre `open_connection(tmp_path / "filepilot.db")` e fecha ao fim.

Padroes estabelecidos:
- O servico levanta `FilePilotError` pelo helper `_error(code, fields=None)`, com `message` do dicionario do proprio modulo (mesmo padrao de scanner.py).
- Falha de gravacao e simulada em teste com `monkeypatch` de `rules._normalize_extensions`, forcando uma extensao que o `CHECK` do banco recusa.
- Reordenar usa duas etapas na mesma transacao: `position = -position` e depois a posicao final, por causa do `UNIQUE (position)`.

Entregue por filepilot-v1-8 (commit e0c61a3). Nao reimplementar: a janela principal, a instancia unica e o bloqueio de fechamento. A aba Regras entra no lugar do marcador.

Artefatos criados:
- filepilot/__main__.py - ponto de entrada - exporta `main` e `open_main_window(data_dir) -> MainWindow | int`
- filepilot/ui/main_window.py - interface - exporta `MainWindow`, `build_tabs`, `PlaceholderTab`, `Reloadable` e `TAB_TITLES`

Contratos:
- `build_tabs(conn: sqlite3.Connection) -> list[tuple[str, QWidget]]` devolve `(titulo, widget)` na ordem "Organizar", "Histórico", "Regras"; trocar o marcador de "Regras" e trocar o widget do terceiro item por `RulesTab(conn)`.
- `Reloadable` e um `Protocol` com `reload() -> None`; `MainWindow` chama `reload()` na aba de indice 1 ou 2 em `currentChanged`. `RulesTab` implementa `reload()` e recarrega com `list_rules(conn)`.
- Armadilha: `MainWindow.conn` e unica e e a mesma entregue a `build_tabs`; a aba Regras nao abre nem fecha conexao propria.

## Features

### filepilot-v1-12-f1 RulesTab com a lista de regras e os botoes
Linhas da SPEC: .abt/SPEC.md L499-521
Arquivos:
- filepilot/ui/rules_tab.py (novo)
- filepilot/ui/main_window.py (novo)
- tests/ui/test_rules_tab.py (novo)
Criterios de aceite:
- A lista mostra as regras por prioridade com as colunas Prioridade, Nome, Extensões (separadas por virgula) e Subpasta.
- Sem regras mostra "Nenhuma regra personalizada. Use \"Nova regra\" para criar a primeira."; carregando mostra "Carregando regras..."; erro mostra a mensagem do servico.
- Editar, Excluir, Subir e Descer so ficam habilitados com uma linha selecionada; Subir na primeira linha e Descer na ultima ficam desabilitados.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_rules_tab.py -> exit 0
- parser: python -m py_compile filepilot/ui/rules_tab.py -> exit 0
- grep deve casar: Carregando regras em filepilot/ui/rules_tab.py
- dependencias: PySide6 em pyproject.toml
Dicas:
- Use `list_rules` e `move_rule` (item filepilot-v1-3); a aba nunca toca no banco direto.
- Troque o marcador "Regras" criado por `build_tabs` (item filepilot-v1-8) pelo `RulesTab` real; a aba recarrega ao receber `currentChanged`.

### filepilot-v1-12-f2 RuleEditorDialog para criar e editar
Linhas da SPEC: .abt/SPEC.md L499-521
Arquivos:
- filepilot/ui/rule_editor_dialog.py (novo)
- tests/ui/test_rule_editor_dialog.py (novo)
Criterios de aceite:
- O dialogo tem os campos Nome, Extensões (separadas por virgula) e Subpasta de destino, todos obrigatorios, com os botoes "Salvar" e "Cancelar".
- Salvar uma regra valida chama `create_rule` ou `update_rule`, emite `saved(rule_id)`, fecha com `accept` e a lista seleciona a regra salva.
- `REGRA_INVALIDA` mostra a mensagem exata de `fields` em vermelho abaixo de cada campo com erro, sem fechar o dialogo; durante a gravacao o botao fica "Salvando..." e desabilitado.
- `BANCO_INDISPONIVEL` mostra `QMessageBox.critical` e o dialogo continua aberto.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_rule_editor_dialog.py -> exit 0
- parser: python -m py_compile filepilot/ui/rule_editor_dialog.py -> exit 0
- grep deve casar: Salvando... em filepilot/ui/rule_editor_dialog.py
Dicas:
- Textos de exemplo dos campos: "Planilhas do trabalho", "xlsx, csv" e "Trabalho/Planilhas".
- As mensagens por campo vem de `fields` do `FilePilotError` (SPEC 6.6, L351-376); nao reescreva o texto na interface.

### filepilot-v1-12-f3 Excluir com confirmacao e reordenar
Linhas da SPEC: .abt/SPEC.md L499-521
Arquivos:
- filepilot/ui/rules_tab.py (novo)
- tests/ui/test_rules_delete_move.py (novo)
Criterios de aceite:
- Excluir abre `QMessageBox.question` com "Excluir a regra \"<nome>\"? O histórico não será alterado." e botoes "Excluir" e "Cancelar"; Cancelar mantem a regra e Excluir chama `delete_rule`.
- Subir e Descer chamam `move_rule`, atualizam a coluna Prioridade e mantem a regra selecionada.
- Depois de excluir ou mover, as posicoes continuam de 1 a N sem lacuna.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_rules_delete_move.py -> exit 0
- grep deve casar: O histórico não será alterado em filepilot/ui/rules_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Fluxo 8.3 (L551-560): a mudanca vale da proxima simulacao em diante e o historico ja gravado nao muda.
- Dublê de `QMessageBox.question` retornando cada botao nos testes.

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
