# filepilot-fix3-4 - Desfazer com laco de atalhos vira PASTA_INVALIDA
Epico: filepilot-fix3 | Ordem: 4 | Pontos: 4 | Depende de: filepilot-fix2-4,filepilot-v1-11

## Objetivo

O desfazer com laco de atalhos em source_path ou em folder_path termina com PASTA_INVALIDA em vez de erro interno, sem alterar o que ja foi restaurado, e a aba mostra a mensagem de contrato.

## Contexto herdado

-

## Features

### filepilot-fix3-4-f1 Desfazer usa resolve_folder e levanta PASTA_INVALIDA
Linhas da SPEC: .abt/SPEC.md L1296-1302
Arquivos:
- filepilot/services/undo.py L1-16
- filepilot/services/undo.py L46-63
- filepilot/services/undo.py L90-110
- filepilot/services/undo.py L152-172
- filepilot/services/scanner.py L52-61
Criterios de aceite:
- Laco em `source_path` ou em `folder_path` faz `undo_last` levantar `FilePilotError` com `code == "PASTA_INVALIDA"` e a mensagem `A pasta escolhida não existe ou não é uma pasta.`, sem o texto da excecao original e com `__cause__` do tipo `RuntimeError` quando a origem e `Path.resolve`.
- Depois do erro, as operacoes ja restauradas continuam `restaurado`, as demais `movido`, a organizacao nao fica `desfeita`, `conn.in_transaction` e `False` e o `OPERATION_LOCK` esta livre.
- Laco numa pasta de destino ou em algum pai dela na limpeza de pastas vazias nao levanta erro: `removed_folders == []`, a pasta continua existindo e a organizacao fica `desfeita`.
- `OSError` com `errno.EACCES` na resolucao continua `OSError` e nao vira `PASTA_INVALIDA`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/services/test_undo_loop.py tests/ui/test_undo_loop.py -> exit 0
- testes: pytest tests/services/test_undo.py tests/services/test_undo_rollback.py tests/services/test_undo_loop.py -> exit 0
- grep deve casar: resolve_folder em filepilot/services/undo.py
- grep nao deve casar: \.resolve\(\) em filepilot/services/undo.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/services/undo.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/undo.py
Dicas:
- Contrato canonico: `resolve_folder` em `filepilot/services/scanner.py` L52-61, ja publico; `undo.py` importa dele (nao ha ciclo, `scanner` nao importa `undo`).
- Trocar as chamadas de `resolve()` em `_is_inside` (L46-47) e em `_remove_empty_folders` (L103); na limpeza, o `FilePilotError` da resolucao encerra so a subida daquele destino.
- `internal_error` (`filepilot/services/organizer.py` L42-50) devolve o `FilePilotError` como esta, entao o codigo chega a `OrganizeTab._on_undo_failed` sem virar `ERRO_INTERNO`.
- Opcao A escolhida pela pessoa em 45.3: o texto de `PASTA_INVALIDA` de 6 e mantido; nenhuma mensagem nova.
- Confirmar que `Path.resolve` levanta `RuntimeError` em laco no Python 3.12 (medido nesta especificacao).

### filepilot-fix3-4-f2 Testes do desfazer com laco, em servico e interface
Linhas da SPEC: .abt/SPEC.md L1304-1311
Arquivos:
- tests/services/test_undo_loop.py (novo)
- tests/ui/test_undo_loop.py (novo)
- tests/services/test_undo.py L1-50
- tests/ui/test_undo_button.py L48-77
- tests/ui/test_undo_button.py L315-330
Criterios de aceite:
- `pytest tests/services/test_undo_loop.py tests/ui/test_undo_loop.py` termina com exit 0 e cobre os seis testes de 45.3: `RuntimeError`, `ELOOP` e `EACCES`, laco real, falha no meio com segundo desfazer, laco so na limpeza e a interface.
- Na interface, depois de organizar e de `undo_last` levantar `FilePilotError("PASTA_INVALIDA", ...)`, `tab.summary.text()` e o texto de contrato, nao e `Ocorreu um erro inesperado. Tente de novo.`, `tab.undo_button.isEnabled()` e verdadeiro e `window.organizing is False`.
- Laco real: `pytest.skip` se o sistema recusar criar o link, exceto no runner Windows do GitHub Actions, onde falha.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/services/test_undo_loop.py tests/ui/test_undo_loop.py -> exit 0
- testes: pytest tests/services/test_undo_loop.py tests/ui/test_undo_loop.py -> exit 0
- grep deve casar: PASTA_INVALIDA em tests/services/test_undo_loop.py
- grep deve casar: PASTA_INVALIDA em tests/ui/test_undo_loop.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/services/test_undo_loop.py
Dicas:
- Padrao a seguir: `tests/services/test_undo.py` L16-50 (`_plan`, `_statuses`, fixtures `conn` e `folder`) e `tests/ui/test_undo_button.py` L48-77 (`_window`, `_organize`, `_undo`), copiados para os arquivos novos.
- Modelo da falha inesperada na interface: `test_falha_inesperada_no_desfazer_mostra_o_texto_generico` em `tests/ui/test_undo_button.py` L315-330.
- Regra de 45.7: toda fixture com yield nos arquivos novos e anotada `Iterator[tipo]`, mesmo copiada.
- Ordem recomendada pelo relatorio de prontidao: este item depois do item filepilot-fix3-3, que muda o corpo de `resolve_folder`.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests/services/test_undo_loop.py tests/ui/test_undo_loop.py -> exit 0 (o comando completo de 45.7 so passa depois do item filepilot-fix3-1)
- testes: pytest -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix3/*.md
```
