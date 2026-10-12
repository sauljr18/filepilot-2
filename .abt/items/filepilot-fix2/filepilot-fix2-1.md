# filepilot-fix2-1 - Desfazer com banco indisponivel faz rollback e permite novo desfazer
Epico: filepilot-fix2 | Ordem: 1 | Pontos: 3 | Depende de: filepilot-v1-7

## Objetivo

Depois de uma falha do banco no meio do desfazer, nenhuma transacao fica aberta: o arquivo da falha continua no destino com a linha movido e um segundo desfazer o restaura de verdade, em vez de pular a linha e marcar a organizacao como desfeita com o arquivo fora do lugar.

## Contexto herdado

-

## Features

### filepilot-fix2-1-f1 Rollback da transacao aberta quando o banco falha no desfazer
Linhas da SPEC: .abt/SPEC.md L1104-1125
Arquivos:
- filepilot/services/undo.py L50-158
- tests/services/test_undo_rollback.py (novo)
- tests/services/test_undo.py L1-60
- tests/services/test_undo.py L344-372
Criterios de aceite:
- Com undo._record_status trocado por monkeypatch por uma funcao que executa o UPDATE real sem commit e levanta sqlite3.OperationalError("disco cheio"), undo_last levanta FilePilotError com code BANCO_INDISPONIVEL, conn.in_transaction e False, o arquivo esta em Documentos/a.pdf e o status da operacao e movido.
- Com o monkeypatch desfeito, o segundo undo_last devolve restored_count igual a 1, o arquivo volta a folder/a.pdf, o status vira restaurado e last_undoable(conn) passa a devolver None.
- Em plano de 3 arquivos com falha so na segunda chamada de _record_status, depois do segundo undo_last os tres arquivos estao nos caminhos originais e os tres status sao restaurado.
- Com um TRIGGER BEFORE UPDATE ON organizations WHEN NEW.status = 'desfeita' que levanta RAISE(ABORT), undo_last levanta BANCO_INDISPONIVEL e conn.in_transaction e False; com o gatilho removido, o segundo undo_last devolve restored_count igual a 0 e last_undoable(conn) devolve None.
- Com _record_status fechando a conexao (conn.close()) e levantando sqlite3.OperationalError, undo_last levanta BANCO_INDISPONIVEL sem levantar ProgrammingError e o arquivo esta de volta em Documentos/a.pdf.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_undo_rollback.py tests/services/test_undo.py -> exit 0
- parser: python -m py_compile filepilot/services/undo.py -> exit 0
- grep deve casar: def _rollback em filepilot/services/undo.py
- grep deve casar: conn.rollback em filepilot/services/undo.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/services/undo.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/undo.py
Dicas:
- Hoje _record_status (undo.py L66-77) faz execute e commit; se o commit levanta sqlite3.Error, _run (L117-124) devolve o arquivo ao destino com os.rename e levanta BANCO_INDISPONIVEL sem rollback, e a linha continua restaurado na transacao aberta da mesma conexao. Medicao da SPEC 37.2: depois de UPDATE sem commit, conn.in_transaction e True e uma leitura na mesma conexao ve o valor novo.
- Crie o helper _rollback(conn) com contextlib.suppress(sqlite3.Error) em volta de conn.rollback(); contextlib ja esta importado em undo.py (L7). Ele nunca levanta: o erro que sobe e sempre o BANCO_INDISPONIVEL original.
- Chame _rollback(conn) em dois pontos: no except sqlite3.Error de _run (L119), ANTES do os.rename que devolve o arquivo ao destino e antes do raise; e no except sqlite3.Error de undo_last (L155), antes do raise, para a falha do UPDATE final de organizations (L130-136). Nao mude o resto: OPERATION_LOCK continua liberado pelo finally de undo_last e o os.rename de volta continua em contextlib.suppress(OSError).
- Padrao de teste com monkeypatch de undo._record_status: tests/services/test_undo.py L344-362. O novo teste executa o UPDATE de verdade sem commit (conn.execute("UPDATE operations SET status = ? WHERE id = ?", ...)) e depois levanta, porque o teste existente troca a funcao inteira e nao deixa transacao aberta.
- Para a falha so na segunda chamada, guarde a funcao original (undo._record_status) antes do monkeypatch e chame-a na primeira vez. A ordem do laco e seq decrescente (undo.py L103-108): a segunda chamada trata o segundo arquivo na ordem inversa.
- Reaproveite _plan, _statuses e as fixtures conn e folder de tests/services/test_undo.py L1-50 (copie ou importe). O gatilho do teste do UPDATE final cria-se com conn.execute("CREATE TRIGGER ...") e remove-se com DROP TRIGGER.
- O teste existente test_banco_fechado_levanta_banco_indisponivel (tests/services/test_undo.py L365-372) continua passando mas NAO prova o rollback na conexao fechada, porque a falha acontece antes, em last_undoable (services/history.py L136).
- Fora de escopo (SPEC 37.6): o resolve() do desfazer em undo.py L47 e L93 e a falha do os.rename de volta nao sao corrigidos aqui.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix2/*.md
```
