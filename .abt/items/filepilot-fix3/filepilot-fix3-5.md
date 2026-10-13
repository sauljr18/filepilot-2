# filepilot-fix3-5 - Historico mostra a data como veio quando ela e invalida
Epico: filepilot-fix3 | Ordem: 5 | Pontos: 2 | Depende de: filepilot-v1-11

## Objetivo

A aba Historico carrega a pagina e mostra o started_at sem alteracao quando ele nao pode virar horario local, como no ano 0001, em vez de derrubar o carregamento com erro interno.

## Contexto herdado

Artefatos criados por filepilot-fix3-4 (commit 3ac38f8):
- filepilot/services/undo.py - modulo - `undo_last(conn)` passa a poder levantar `FilePilotError` com `code == "PASTA_INVALIDA"`; `_is_inside` e a subida de `_remove_empty_folders` resolvem por `resolve_folder`.

Contratos:
- `undo_last(conn) -> UndoResult` em filepilot/services/undo.py: laco de atalhos em `source_path` ou em `folder_path` levanta `PASTA_INVALIDA` com o texto de contrato; na limpeza de pastas vazias o laco encerra so a subida daquele destino e a organizacao fecha como `desfeita`. Armadilha: `OSError` com `errno.EACCES` continua `OSError`.

Padroes estabelecidos:
- Nos testes de servico, `_fail_resolve_for(target, error)` troca `Path.resolve` por `monkeypatch` e levanta so quando `self == target` (tests/services/test_undo_loop.py L21-30).
- Nos testes de interface, `_window`, `_organize` e `_undo` sao copiados de tests/ui/test_undo_button.py e o servico e trocado por `monkeypatch` em `organize_worker_module.undo_last` (tests/ui/test_undo_loop.py L18-48).

filepilot-fix3-4 entregou o tratamento de laco no desfazer e NAO toca em filepilot/ui/history_tab.py: NAO reimplemente a deteccao de laco aqui.

## Features

### filepilot-fix3-5-f1 format_local_time tolera data fora do intervalo
Linhas da SPEC: .abt/SPEC.md L1279-1283
Arquivos:
- filepilot/ui/history_tab.py L1-7
- filepilot/ui/history_tab.py L60-66
- filepilot/ui/history_tab.py L113-120
Criterios de aceite:
- `format_local_time("0001-01-01T00:00:00Z")` devolve `"0001-01-01T00:00:00Z"` sem levantar.
- `format_local_time("2026-10-12T09:30:00Z")` continua devolvendo o horario local no formato `dd/MM/yyyy HH:mm` e `format_local_time("ontem")` continua devolvendo `"ontem"`.
- `ValueError`, `OverflowError` e `OSError` na conversao devolvem o `started_at` sem alteracao.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/ui/test_history_invalid_date.py -> exit 0
- testes: pytest tests/ui/test_history_tab.py tests/ui/test_history_details.py tests/ui/test_history_invalid_date.py -> exit 0
- grep deve casar: OverflowError em filepilot/ui/history_tab.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/ui/history_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/ui/history_tab.py
Dicas:
- Contrato canonico: `format_local_time` em `filepilot/ui/history_tab.py` L60-66; hoje captura so `ValueError`.
- Medicao desta especificacao (Python 3.12.3, Linux): `datetime.strptime("0001-01-01T00:00:00Z", "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC).astimezone()` levanta `OverflowError: date value out of range`; no Windows a mesma conversao levanta `OSError`.
- `_load_page` (L266-278) captura so `FilePilotError`: sem a correcao o erro sobe do slot e a pagina nao carrega.
- Nao muda a ordenacao por `started_at DESC, id DESC` nem as demais colunas.

### filepilot-fix3-5-f2 Testes de data invalida no Historico
Linhas da SPEC: .abt/SPEC.md L1285-1290
Arquivos:
- tests/ui/test_history_invalid_date.py (novo)
- tests/ui/test_history_tab.py L1-45
- tests/ui/test_history_tab.py L100-130
Criterios de aceite:
- `pytest tests/ui/test_history_invalid_date.py` termina com exit 0 e cobre os quatro testes de 45.2: ano 0001, `OSError` simulado em `history_tab.datetime`, pagina com duas organizacoes e regressao.
- Com duas organizacoes, `started_at` `"0001-01-01T00:00:00Z"` e `"2026-10-12T09:30:00Z"`, `tab.reload()` nao levanta, `rowCount() == 2`, a celula "Data e hora" da primeira linha e o horario local da data valida e a da segunda e `"0001-01-01T00:00:00Z"`.
- `status_label.text() == ""` e `retry_button` escondido depois do carregamento.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/ui/test_history_invalid_date.py -> exit 0
- testes: pytest tests/ui/test_history_invalid_date.py -> exit 0
- grep deve casar: 0001-01-01T00:00:00Z em tests/ui/test_history_invalid_date.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/ui/test_history_invalid_date.py
Dicas:
- Padrao a seguir: `tests/ui/test_history_tab.py` L20-45 (fixture `conn` e `_add_organization`) e L100-130 (comparacao das celulas com `format_local_time`), copiados para o arquivo novo.
- Para o `OSError`, troque `history_tab.datetime` por uma classe com `strptime` que devolve um objeto cujo `replace` devolve ele mesmo e cujo `astimezone` levanta `OSError(errno.EINVAL, "Invalid argument")`.
- Regra de 45.7: a fixture `conn` com yield no arquivo novo e anotada `Iterator[sqlite3.Connection]`, mesmo copiada de arquivo ainda nao corrigido.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests/ui/test_history_invalid_date.py -> exit 0 (o comando completo de 45.7 so passa depois do item filepilot-fix3-1)
- testes: pytest -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix3/*.md
```
