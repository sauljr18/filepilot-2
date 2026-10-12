# Itens - Correcao de quatro defeitos de desfazer, aba Organizar, instancia unica e planejamento

Epico: filepilot-fix2
Titulo do epico: Correcao de quatro defeitos de desfazer, aba Organizar, instancia unica e planejamento

**Data:** 2026-10-12
**Modo:** so SPEC + itens

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-fix2-1 | Desfazer com banco indisponivel faz rollback e permite novo desfazer | 3 | filepilot-v1-7 | Depois de uma falha do banco no meio do desfazer, nenhuma transacao fica aberta, o arquivo da falha continua no destino com a linha movido e um segundo desfazer o restaura de verdade |
| 2 | filepilot-fix2-2 | Aba Organizar sai de carregando quando a leitura da pasta falha com erro do sistema | 2 | filepilot-v1-9 | Um OSError na leitura da pasta leva a aba Organizar ao estado de erro com a mensagem de PASTA_ILEGIVEL e os botoes Escolher pasta e Atualizar voltam a funcionar |
| 3 | filepilot-fix2-3 | Instancia unica avisa quando nao consegue saber se ha outra janela aberta | 3 | filepilot-v1-8 | Quando a trava falha por motivo diferente de LockFailedError, o programa mostra o texto de falha de acesso a pasta de dados e sai com 1 em vez de fechar em silencio com 0 |
| 4 | filepilot-fix2-4 | Planejamento com laco de atalhos vira PASTA_INVALIDA | 3 | filepilot-fix-1,filepilot-v1-4 | O planejamento de uma pasta ou de um destino com laco de atalhos levanta PASTA_INVALIDA com a mensagem de 6 em vez de RuntimeError, sem bloquear o plano por laco em subpasta que nenhum arquivo usa |

## 2. Criterios de aceite

- filepilot-fix2-1:
    - `python -m pytest tests/services/test_undo_rollback.py` sai com codigo 0 e executa os 5 testes de 37.2.
    - Com `_record_status` trocado para executar o UPDATE sem commit e levantar `sqlite3.OperationalError`, `undo_last` levanta `BANCO_INDISPONIVEL`, `conn.in_transaction` e `False` e o status da operacao e `movido`.
    - O segundo `undo_last` devolve `restored_count == 1`, o arquivo volta ao caminho original e o status vira `restaurado`.
    - `python -m pytest tests/services/test_undo.py` continua com todos os testes passando e `python -m mypy --platform win32 filepilot` sai com `Success: no issues found`.
- filepilot-fix2-2:
    - `python -m pytest tests/ui/test_organize_tab_read_error.py` sai com codigo 0 e executa os 6 testes de 37.3.
    - Com `scan_folder` levantando `PermissionError`, `tab.mode == "erro"` e `tab.summary.text() == "Não foi possível ler a pasta escolhida."`, sem o texto bruto da excecao.
    - Nesse estado, Simular e Organizar ficam desabilitados e Escolher pasta e Atualizar ficam habilitados; `tab.refresh()` com o servico normal leva a `mode == "listado"`.
    - `python -m pytest tests/ui/test_organize_tab_folder.py tests/ui/test_organize_tab_simulate.py` continua passando e o mypy do comando unico sai com `Success: no issues found`.
- filepilot-fix2-3:
    - `python -m pytest tests/ui/test_single_instance_unknown.py` sai com codigo 0 e executa os 6 testes de 37.4 (o de `chmod` pode sair como `skipped`).
    - Com a trava devolvendo `PermissionError` ou `UnknownError`, `open_main_window` devolve `1`, `QMessageBox.critical` recebe o texto de `_LOCK_UNAVAILABLE`, a janela nao e criada e `filepilot.db` nao existe.
    - Com `LockFailedError`, `open_main_window` devolve `0` e `QMessageBox.information` recebe "O FilePilot já está aberto.".
    - `python -m pytest tests/ui/test_single_instance.py` continua passando sem alteracao e o mypy do comando unico sai com `Success: no issues found`.
- filepilot-fix2-4:
    - `python -m pytest tests/services/test_planner_loop.py tests/ui/test_organize_tab_plan_loop.py` sai com codigo 0 e executa os 8 e 1 testes de 37.5 (os de laco real podem sair como `skipped`).
    - Com `Path.resolve` levantando `RuntimeError("Symlink loop")` no destino, `build_plan` levanta `PASTA_INVALIDA` com "A pasta escolhida não existe ou não é uma pasta." e sem o texto `Symlink loop`; com `EACCES`, continua `OSError`.
    - Pasta com `a.pdf` e laco em `Imagens` devolve o plano com a operacao do PDF e sem erro.
    - `python -m pytest tests/services/test_scanner_loop.py tests/services/test_planner_guard.py` continua passando e o mypy do comando unico sai com `Success: no issues found`.

## 3. Mapa para a SPEC

- filepilot-fix2-1: 37.2 E1: banco indisponivel no meio do desfazer; 6.5 undo.undo_last.
- filepilot-fix2-2: 37.3 E2: aba Organizar presa em carregando; 7.2 OrganizeTab.
- filepilot-fix2-3: 37.4 E3: instancia unica sem fechar em silencio; 7.1 MainWindow.
- filepilot-fix2-4: 37.5 E4: planejamento com laco de atalhos; 6.2 planner.build_plan; 27.2 D1: pasta com laco de atalhos e pasta invalida.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| E2 e E4 editam arquivos que as proximas telas (filepilot-v1-10, v1-11 e v1-13, na fila) tambem editam: conflito de mesclagem se as telas forem implementadas antes | Medio | Implementar os quatro itens antes das proximas telas e reabrir os itens das telas sobre a main atualizada |
| O teste de permissao de filepilot-fix2-3 (`chmod 0o500`) depende do sistema e do usuario | Baixo | O teste faz `skip` com verificacao previa; os outros testes do item nao dependem do sistema |
| O teste de laco real de filepilot-fix2-4 depende de o sistema permitir `symlink_to` | Baixo | O teste faz `skip`; os testes com `monkeypatch` rodam em qualquer sistema |
| filepilot-fix2-4 renomeia `scanner._resolve_folder` para `resolve_folder` | Baixo | Nenhum teste nem modulo cita o nome antigo alem de `scanner.py`; o item roda a suite e o mypy |
| A suite de interface depende de PySide6, ausente no ambiente de especificacao | Baixo | Rodar pytest e o comando unico de mypy no ambiente do item |

## 5. Cobertura

| Item do escopo | Item que o cobre |
|---|---|
| F1: banco indisponivel no meio do desfazer | filepilot-fix2-1 |
| F2: leitura da pasta com erro do sistema na aba Organizar | filepilot-fix2-2 |
| F3: sem saber se ha outra janela aberta o programa avisa | filepilot-fix2-3 |
| F4: planejamento com laco de atalho | filepilot-fix2-4 |
| F5: um item de correcao com ao menos um teste por defeito | filepilot-fix2-1, filepilot-fix2-2, filepilot-fix2-3 e filepilot-fix2-4 |
| Metrica: 4 defeitos corrigidos, 4 testes novos passando, nenhum teste existente quebrado | filepilot-fix2-1, filepilot-fix2-2, filepilot-fix2-3 e filepilot-fix2-4 |
| Fora de escopo: proximas telas, novas funcionalidades, refatoracoes, outros defeitos | nenhum item, de proposito |
