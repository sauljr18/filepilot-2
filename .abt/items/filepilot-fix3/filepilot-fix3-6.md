# filepilot-fix3-6 - Barra de progresso some ao desfazer a organizacao
Epico: filepilot-fix3 | Ordem: 6 | Pontos: 2 | Depende de: filepilot-v1-10,filepilot-v1-11

## Objetivo

A aba Organizar esconde a barra de progresso quando um desfazer realmente comeca, de modo que ela nao fique visivel em N de N arquivos depois de desfazer.

## Contexto herdado

Artefatos criados por filepilot-fix3-5 (commit a5d09ae):
- filepilot/ui/history_tab.py - modulo - `format_local_time(started_at)` passa a devolver o `started_at` sem alteracao quando a conversao levanta `ValueError`, `OverflowError` ou `OSError`.
- tests/ui/test_history_invalid_date.py - testes - data no ano 0001, `OSError` simulado em `history_tab.datetime` e aba Historico com duas organizacoes.

Contratos:
- `format_local_time(started_at: str) -> str` em filepilot/ui/history_tab.py: sem mudanca de assinatura nem do formato `dd/MM/yyyy HH:mm`. Armadilha: o `strftime` e o `astimezone` ficam dentro do mesmo `try`.

Padroes estabelecidos:
- Nos testes de interface, a fixture `conn` com yield e anotada `Iterator[sqlite3.Connection]` e `_add_organization` e copiada de tests/ui/test_history_tab.py (tests/ui/test_history_invalid_date.py L20-43).
- Para simular erro do sistema operacional na conversao de data, `monkeypatch.setattr(history_tab_module, "datetime", <classe>)` com `strptime` que devolve objeto cujo `replace` devolve ele mesmo e cujo `astimezone` levanta `OSError` (tests/ui/test_history_invalid_date.py L46-57).

filepilot-fix3-5 entregou o tratamento de data invalida no Historico e NAO toca em filepilot/ui/organize_tab.py: NAO reimplemente `format_local_time` aqui.

## Features

### filepilot-fix3-6-f1 undo esconde a barra ao comecar
Linhas da SPEC: .abt/SPEC.md L1341-1345
Arquivos:
- filepilot/ui/organize_tab.py L289-305
- filepilot/ui/organize_tab.py L349-390
Criterios de aceite:
- Depois de organizar e desfazer, `tab.progress.isHidden()` e `True`; antes do desfazer, depois de organizar, e `False` com `value() == maximum()`.
- Desfazer sem `_db_path` (resumo `Não foi possível acessar o histórico do FilePilot.`) e desfazer com `_undoable is None` nao escondem a barra.
- A barra tambem fica escondida nos desfechos de falha do desfazer, porque o `setVisible(False)` roda no inicio.
- Uma nova organizacao depois do desfazer mostra a barra de novo e termina com `value() == maximum()`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/ui/test_undo_progress.py -> exit 0
- testes: pytest tests/ui/test_undo_button.py tests/ui/test_undo_progress.py -> exit 0
- grep deve casar: self.progress.setVisible\(False\) em filepilot/ui/organize_tab.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/ui/organize_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/ui/organize_tab.py
Dicas:
- Contrato canonico: `OrganizeTab.undo` em `filepilot/ui/organize_tab.py` L349-365; o `setVisible(False)` entra depois da guarda de L352-356 e antes de criar o `UndoWorker`. Padrao a seguir: `refresh`, `simulate` e `organize` escondem a barra em L251, L260 e L269.
- Nao muda o botao "Ver detalhes", a barra de uma nova organizacao (L298-300) nem o texto `"%v de %m arquivos"`.
- Confirmar que `QWidget.setVisible` existe na versao instalada do PySide6 (6.12.0); ja e usado no mesmo arquivo.

### filepilot-fix3-6-f2 Testes da barra de progresso ao desfazer
Linhas da SPEC: .abt/SPEC.md L1347-1354
Arquivos:
- tests/ui/test_undo_progress.py (novo)
- tests/ui/test_undo_button.py L1-77
- tests/ui/test_undo_button.py L188-237
- tests/ui/test_undo_button.py L277-330
Criterios de aceite:
- `pytest tests/ui/test_undo_progress.py` termina com exit 0 e cobre os seis testes de 45.5.
- Todo teste que prova o sumico da barra roda `_organize` antes, porque sem ele a barra ja nasce escondida e o teste passaria antes da correcao.
- Para a guarda, o teste atribui `tab._undoable = None` depois de `_organize`, chama `tab.undo()` e confere que a barra continua visivel.
- A visibilidade e lida com `isHidden()`, que nao depende de a janela estar mostrada.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/ui/test_undo_progress.py -> exit 0
- testes: pytest tests/ui/test_undo_progress.py -> exit 0
- grep deve casar: isHidden em tests/ui/test_undo_progress.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/ui/test_undo_progress.py
Dicas:
- Padrao a seguir: `tests/ui/test_undo_button.py` L48-77 (`_window`, `_organize`, `_undo`), L188-211 (organizacao de outra pasta), L277-312 (worker lento com `threading.Event`) e L315-330 (falha inesperada), copiados para o arquivo novo.
- Para a organizacao de outra pasta, insira uma organizacao com `started_at="2999-01-01T00:00:00Z"` depois de `_organize` e rode `tab.refresh_undo()`.
- Regra de 45.7: fixture com yield no arquivo novo e anotada `Iterator[tipo]`.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests/ui/test_undo_progress.py -> exit 0 (o comando completo de 45.7 so passa depois do item filepilot-fix3-1)
- testes: pytest -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix3/*.md
```
