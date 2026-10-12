# filepilot-fix-4 - Organizacao interrompida e recuperacao ao abrir o banco
Epico: filepilot-fix | Ordem: 4 | Pontos: 8 | Depende de: filepilot-v1-6

## Objetivo

Uma organizacao nunca fica em andamento depois de BANCO_INDISPONIVEL: ela vira interrompida na hora, quando o banco ainda aceita a gravacao, ou ao reabrir o banco, com as contagens das operacoes gravadas, e continua desfazivel.

## Contexto herdado

-

## Features

### filepilot-fix-4-f1 Helper que marca a organizacao como interrompida e rollback na abertura
Linhas da SPEC: .abt/SPEC.md L978-989
Arquivos:
- filepilot/services/organizer.py L130-237
- filepilot/domain/models.py L1-62
Criterios de aceite:
- Quando a gravacao da segunda operacao de um plano de 3 arquivos falha com sqlite3.Error, organize levanta FilePilotError com code BANCO_INDISPONIVEL e a linha de organizations fica com status interrompida, moved_count 1, failed_count 0 e finished_at preenchido.
- Depois do erro, conn.in_transaction e False e o arquivo da segunda operacao esta de volta na pasta original.
- Quando o UPDATE de fechamento falha, a linha fica interrompida com as contagens finais do plano.
- O UPDATE do helper leva AND status = em_andamento: com a linha ja em concluida, chamar o helper nao altera status, contagens nem finished_at.
- Depois de qualquer falha, OPERATION_LOCK.acquire(blocking=False) devolve True.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_organizer_interrupted.py -> exit 0
- parser: python -m py_compile filepilot/services/organizer.py -> exit 0
- grep deve casar: def _interrupt_organization em filepilot/services/organizer.py
- grep deve casar: AND status = em filepilot/services/organizer.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/organizer.py
Dicas:
- Este item depende de filepilot-v1-6, que esta em andamento e move codigo de organizer.py para destination_checks.py: confira o arquivo depois da mesclagem dele e trabalhe pelas funcoes _run, _open_organization e _close_organization, nao pelos numeros de linha citados aqui.
- _interrupt_organization(conn, organization_id, result) faz, dentro de contextlib.suppress(sqlite3.Error): conn.rollback(); UPDATE organizations SET finished_at, status = interrompida, moved_count, failed_count, updated_at WHERE id AND status = em_andamento, com parametros de SQL; conn.commit(). Nunca levanta: se o banco continuar indisponivel a linha fica como esta e a recuperacao da proxima feature a corrige.
- Pontos de chamada: (a) no except sqlite3.Error do registro da operacao em _run, depois do os.rename que devolve o arquivo ao lugar; (b) dentro de _close_organization, no except que hoje so levanta BANCO_INDISPONIVEL. O erro que sobe e sempre o BANCO_INDISPONIVEL original.
- _open_organization ganha conn.rollback() dentro de contextlib.suppress(sqlite3.Error) antes de levantar BANCO_INDISPONIVEL; nesse ponto ainda nao ha linha confirmada.
- O fechamento (b) e testado sem trocar _close_organization: crie no banco, antes de organize, um TRIGGER BEFORE UPDATE ON organizations WHEN NEW.status = 'concluida' com SELECT RAISE(ABORT, 'falha'); o UPDATE do helper, com status interrompida, passa pelo gatilho.
- Para o teste de falha na primeira operacao e a verificacao de last_undoable use a condicao em SQL de 6.4, status IN ('concluida','interrompida') AND moved_count >= 1, e nao importe history: filepilot/services/history.py ainda nao existe (e do item filepilot-v1-7).
- Padrao dos testes: tests/services/test_organizer_failures.py (open_connection em tmp_path, monkeypatch de funcoes do modulo organizer, Plan montado com build_plan).
- Banco inteiramente indisponivel no teste: feche a conexao com conn.close() dentro do monkeypatch de _record_operation antes de levantar sqlite3.OperationalError; o helper nao pode propagar ProgrammingError.
- Ver 5.3 (status interrompida) e 6.3 (organize) para o contrato que esta feature completa.

### filepilot-fix-4-f2 Recuperacao de organizacao em andamento ao abrir o banco
Linhas da SPEC: .abt/SPEC.md L991-1005
Arquivos:
- filepilot/db/connection.py L1-28
- tests/db/test_connection_recovery.py (novo)
- tests/db/test_migrations.py L1-40
Criterios de aceite:
- open_connection sobre um banco com uma organizacao em_andamento e 3 operacoes gravadas (2 movido e 1 falha) a deixa com status interrompida, moved_count 2, failed_count 1, finished_at e updated_at preenchidos.
- Linhas em concluida, interrompida e desfeita ficam identicas (status, contagens e finished_at) depois de open_connection.
- Banco novo, ou sem organizacao em_andamento, abre sem alterar nenhuma linha.
- Com _recover_interrupted trocada por monkeypatch para levantar sqlite3.OperationalError, open_connection levanta FilePilotError com code BANCO_INDISPONIVEL.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/db/test_connection_recovery.py tests/db/test_migrations.py -> exit 0
- parser: python -m py_compile filepilot/db/connection.py -> exit 0
- grep deve casar: def _recover_interrupted em filepilot/db/connection.py
- grep deve casar: interrompida em filepilot/db/connection.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/db/connection.py
Dicas:
- _recover_interrupted(conn) e chamada por open_connection logo depois de apply_migrations(conn), dentro do mesmo try (connection.py L19-24): um sqlite3.Error cai no except que ja fecha a conexao e levanta BANCO_INDISPONIVEL, sem texto novo.
- O UPDATE recalcula as contagens das linhas de operations, porque organizations.moved_count so e gravado no fechamento: SET status = interrompida, finished_at, updated_at, moved_count = (SELECT COUNT(*) FROM operations o WHERE o.organization_id = organizations.id AND o.status = movido), failed_count = (mesma contagem com status falha) WHERE status = em_andamento, com parametros de SQL para as horas e os status; depois conn.commit(). Sem o recalculo a linha recuperada fica com moved_count 0 e last_undoable (6.4) a recusa, contra 5.3.
- finished_at e updated_at recebem a hora UTC da recuperacao no formato AAAA-MM-DDTHH:MM:SSZ, por uma _utc_now() local de connection.py, igual a de migrations.py (L95).
- Premissa: nenhuma organizacao esta em curso quando open_connection roda (7.1: conexao unica e instancia unica). Nao verifique isso em codigo: a camada db nao importa a de servicos (3.2).
- filepilot-v1-7-f2 (na fila) tambem descreve esta recuperacao; a decisao da pessoa (opcao A) e que este item e o dono. Nao implemente de novo nem apague codigo de v1-7: o criterio equivalente de v1-7-f2 sera retirado a parte.
- Os testes inserem as linhas de organizations e operations com SQL direto numa conexao aberta e a fecham; depois chamam open_connection no mesmo arquivo. Padrao: tests/db/test_migrations.py (open_connection em tmp_path, helper _insert_organization, L163-170).
- Para conferir o desfazer sem importar history, use a condicao em SQL de 6.4: status IN ('concluida','interrompida') AND moved_count >= 1.
- Ver 5.3 para a regra de recuperacao e os status validos.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix/*.md
```
