# Validacao do item filepilot-fix-4 - Organizacao interrompida e recuperacao ao abrir o banco

**Item:** filepilot-fix-4 | **Epico:** filepilot-fix | **Data:** 2026-10-12
Execucao: 20261012-112617
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, 14 arquivos; `comm -13` contra a baseline do Carlos: zero erros novos |
| 2 Criterios de aceite | PASS | 9/9 criterios atendidos (5 em f1, 4 em f2) |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented, FIXME ou print nos 4 arquivos do diff; grep de unicode tipografico vazio; `py_compile` exit 0 |
| 4 Autorizacao e seguranca | PASS | n/a: sem endpoint; todo SQL novo usa parametros (`organizer.py:126-131`, `connection.py:26-35`) |
| 5 Testes | PASS | `pytest` 251 passed, 2 skipped (os 2 so valem no Windows: `test_destination_checks.py:153` e `test_scanner_protected.py:185`); 13 testes novos; mutacoes refeitas por mim, ver abaixo |
| 6 Consistencia entre documentos | PASS | SPEC L978-1005 conferida contra o codigo; nomes e status batem com 5.3; os 8 testes obrigatorios de organizer e os 4 de recuperacao existem |
| 7b Varredura adversarial | PASS | nenhum consumidor novo; nenhuma chamada a `open_connection` no codigo de producao (so em testes), logo a premissa da recuperacao nao e violada hoje; `_utc_now` local em `connection.py` e decisao da SPEC |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim" as 4 perguntas; ver nota 1 da lista de correcoes (cobertura) |
| 7d Matriz (backend) | PASS | BE-1 sem criterio "nenhum ponto faz X"; BE-2 e BE-3 n/a (sem conteiner de injecao nem policies) |
| 7e Funcao irma e comando citado | PASS | `_interrupt_organization` nao pega trava, como as irmas `_open_organization`, `_record_operation` e `_close_organization` (a trava e de `organize`); nenhuma mensagem nova manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix-4-f1 | 2a gravacao falha em plano de 3: `BANCO_INDISPONIVEL`, linha `interrompida`, moved 1, failed 0, `finished_at` preenchido | PASS | `organizer.py:195-202`; `test_organizer_interrupted.py:64` |
| filepilot-fix-4-f1 | `conn.in_transaction` False e arquivo da 2a operacao de volta | PASS | `organizer.py:197-201` (`os.rename` antes do helper, que faz `rollback` em `:124`); `test_organizer_interrupted.py:64` |
| filepilot-fix-4-f1 | UPDATE de fechamento falha: linha `interrompida` com as contagens finais | PASS | `organizer.py:174-176`; `test_organizer_interrupted.py:109` (trigger real, 3/0) |
| filepilot-fix-4-f1 | UPDATE do helper leva `AND status = em_andamento`: linha `concluida` fica intacta | PASS | `organizer.py:129`; `test_organizer_interrupted.py:133` |
| filepilot-fix-4-f1 | `OPERATION_LOCK.acquire(blocking=False)` True depois de qualquer falha | PASS | `finally` em `organizer.py:226-227`; `test_organizer_interrupted.py:192` (falha na 1a e na 2a) |
| filepilot-fix-4-f2 | `open_connection` com `em_andamento` e 3 operacoes (2 movido, 1 falha): `interrompida`, 2/1, `finished_at` e `updated_at` preenchidos | PASS | `connection.py:25-36` e `:52`; `test_connection_recovery.py:57` |
| filepilot-fix-4-f2 | Linhas `concluida`, `interrompida` e `desfeita` identicas | PASS | `connection.py:33`; `test_connection_recovery.py:98` |
| filepilot-fix-4-f2 | Banco novo ou sem `em_andamento` abre sem alterar linhas | PASS | `test_connection_recovery.py:113` (compara tambem `updated_at`) |
| filepilot-fix-4-f2 | `_recover_interrupted` com `OperationalError`: `BANCO_INDISPONIVEL` | PASS | `connection.py:53-56`; `test_connection_recovery.py:133` |

## Mutacoes refeitas pela Rita

Escopo: suite inteira (251 testes + 2 skipped); cada mutacao revertida por copia de arquivo; ao fim `git status --short` e `git diff --stat` iguais aos do inicio (2 arquivos alterados, +56 -1, 2 arquivos novos).

| # | Mutacao (diff) | Resultado |
|---|---|---|
| R1 | `organizer.py:201`: remove `_interrupt_organization(...)` do ponto (a) | 2 falhas, pegou |
| R2 | `organizer.py:175`: remove `_interrupt_organization(...)` do ponto (b) | 1 falha, pegou |
| R3 | `organizer.py:129`: `WHERE id = ? AND status = 'em_andamento'` vira `WHERE id = ?` | 1 falha, pegou |
| R4 | `organizer.py:124`: remove `conn.rollback()` do helper | 1 falha, pegou |
| R5 | `organizer.py:106-107`: remove o `rollback` de `_open_organization` | 0 falhas, NAO pegou (nota 1) |
| R6 | `connection.py:52`: remove `_recover_interrupted(conn)` | 3 falhas, pegou |
| R7 | `connection.py:33`: remove `WHERE status = 'em_andamento'` | 2 falhas, pegou |
| R8 | `connection.py:30`: o recalculo de `moved_count` passa a contar `AND 0` | 1 falha, pegou |

Divergencia com o relato do Carlos: ele declarou 7 mutacoes, todas pegas; a R5 acima e a unica que nenhum teste pega, e ele nao a testou.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | tests/services/test_organizer_interrupted.py | 172 | O `rollback` novo de `_open_organization` (`organizer.py:106-107`) nao tem teste: o teste `test_falha_ao_abrir_a_organizacao_nao_deixa_transacao_aberta` derruba as tabelas, entao o INSERT falha sem abrir transacao e a R5 passa. O caso real e o `commit()` falhar com a insercao pendente | Usar um proxy de conexao cuja `commit` levanta `sqlite3.OperationalError` depois de um INSERT real e afirmar `conn.in_transaction` False | nao |
| 2 | filepilot/services/organizer.py | 120 | O grep `AND status = em` da `Verificacao:` de f1 so casa no docstring; o SQL real (`:129`) tem aspas (`'em_andamento'`) e o grep literal nao o acha. O codigo esta correto; o grep do detalhe do item nao reflete o SQL | Corrigir o grep no detalhe do item (product-spec) ou aceitar o docstring como a prova | nao |
| 3 | tests/services/test_organizer_interrupted.py | 31 | O parametro `conn` de `_fail_record_on` nao e usado | Remover o parametro e ajustar as 3 chamadas (`:71`, `:96`, `:199`) | nao |
