# Validacao do item filepilot-v1-5 - Organizacao com historico por arquivo

**Item:** filepilot-v1-5 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-013558
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "Success: no issues found in 13 source files"; baseline do Carlos com 0 erros (12 arquivos); o unico delta do `comm` e a contagem de arquivos |
| 2 Criterios de aceite | PASS | 11/11 criterios atendidos, evidencia propria abaixo |
| 3 Qualidade de codigo | PASS | zero `TODO`, `FIXME`, `placeholder`, `not implemented`, `print(`; zero unicode tipografico em `filepilot`; sem bloco comentado |
| 4 Autorizacao e seguranca | PASS | sem endpoint; a guarda `is_relative_to` (organizer.py:105) e a recusa de atalho (organizer.py:103) impedem escrita fora da pasta; `error_message` nunca grava o texto bruto do sistema |
| 5 Testes | PASS | suite completa 172 passed, 1 skipped (`test_scanner_protected.py:150`, "so vale no Windows", pre-existente); 17 testes novos do item; todo service novo (`organize`, `simulate`) tem teste |
| 6 Consistencia entre documentos | PASS | colunas e status de `organizations` e `operations` batem com SPEC 5.3 (L147-185); textos de 6.7 (L389-397) e de `ORGANIZACAO_EM_ANDAMENTO` (L252) literais; `OrganizationResult` de `models.py:55-62` reaproveitado |
| 7b Varredura adversarial | FAIL (nao decide) | `_utc_now` em organizer.py:49 repete `rules._utc_now` (rules.py:40): duas fontes de verdade; os helpers do planner foram reaproveitados, nao reinventados |
| 7c Degradacao e borda | PASS | as 4 perguntas sem "sim"; sondagens: plano vazio, `FileExistsError` real do `os.rename`, subpasta que e arquivo, excecao no callback |
| 7d Matriz (backend) | PASS | BE-1: `os.replace` e `shutil.move` com zero ocorrencia em `filepilot/services`; BE-2 e BE-3 n/a (sem injecao de dependencia nem policy) |
| 7e Funcao irma e comando citado | FAIL (nao decide) | organizer.py:190-221 nao replica o `rollback` que a irma `rules._transaction` usa (rules.py:54-55); 7e-2 n/a (nenhum comando citado em mensagem) |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-5-f1 | `organize` move os N arquivos e grava 1 `organizations` (`concluida`, `moved_count` N, `finished_at`) e N `operations` `movido` com `seq` 1..N e `destination_path` final | PASS | organizer.py:130-143, 147-172, 175-187; tests/services/test_organizer.py:29 |
| filepilot-v1-5-f1 | Cada operacao gravada com `commit` imediato: segunda conexao enxerga as anteriores | PASS | organizer.py:172; tests/services/test_organizer.py:64 (sequencia `(0,0),(1,1),(2,2),(3,3)`) |
| filepilot-v1-5-f1 | Plano vazio devolve contagens 0 e `organization_id` 0 sem gravar `organizations` | PASS | organizer.py:230-231; tests/services/test_organizer.py:107 |
| filepilot-v1-5-f1 | `simulate(plan)` devolve o mesmo plano e a arvore fica identica | PASS | organizer.py:53-55; tests/services/test_organizer.py:122 |
| filepilot-v1-5-f2 | `progress_callback` chamado N+1 vezes, `done` de 0 a N-1 e depois `done == total` | PASS | organizer.py:203 e 220; tests/services/test_organizer_conflicts.py:20 |
| filepilot-v1-5-f2 | Arquivo criado no destino entre plano e execucao recebe sufixo (1) e o existente mantem o conteudo | PASS | organizer.py:113-127; tests/services/test_organizer_conflicts.py:36; sondagem propria com `FileExistsError` levantado pelo proprio `os.rename`: `['a (1).pdf', 'a.pdf']`, original intacto |
| filepilot-v1-5-f2 | `destination_path` gravado e o nome final com sufixo | PASS | organizer.py:147-172; tests/services/test_organizer_conflicts.py:55 |
| filepilot-v1-5-f3 | `PermissionError` em 1 arquivo grava `falha` com `destination_path` NULL e `error_message`, incrementa `failed_count`, os demais sao movidos | PASS | organizer.py:82-92 e 216-221; tests/services/test_organizer_failures.py:36 |
| filepilot-v1-5-f3 | `OPERATION_LOCK` impede duas execucoes (`ORGANIZACAO_EM_ANDAMENTO`) e o `finally` libera a trava depois de excecao | PASS | organizer.py:24 e 232-237; tests/services/test_organizer_failures.py:84 e 103; sondagem propria: `locked()` False depois de excecao no callback |
| filepilot-v1-5-f3 | `sqlite3.Error` ao gravar devolve o arquivo ao lugar e levanta `BANCO_INDISPONIVEL` | PASS | organizer.py:205-212; tests/services/test_organizer_failures.py:119 |
| filepilot-v1-5-f3 | Todo destino reconferido com `is_relative_to` antes do `os.rename`; fora da pasta vira `falha` | PASS | organizer.py:105-106 e 124; tests/services/test_organizer_failures.py:144; atalho e caminho longo nos testes de :165 e :203 |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/services/organizer.py | 205-212 | Depois de `BANCO_INDISPONIVEL` a conexao fica em transacao aberta (`conn.in_transaction` True na sondagem), segurando a trava de escrita ate o proximo commit; `rules._transaction` faz `conn.rollback()` no mesmo caso (rules.py:55) | Chamar `conn.rollback()` (com `contextlib.suppress(sqlite3.Error)`) antes do `raise _error("BANCO_INDISPONIVEL")`, tambem em `_open_organization` e `_close_organization`, e acrescentar um assert de `conn.in_transaction` falso no teste de :119 | nao |
| 2 | filepilot/services/organizer.py | 49 | `_utc_now` duplica `_utc_now` de rules.py:40 | Mover para um modulo comum (ex.: `filepilot/db/` ou `filepilot/domain/`) e usar nos dois | nao |
| 3 | tests/services/test_organizer_conflicts.py | 36 | O ramo `except FileExistsError` do `os.rename` real (corrida entre `lexists` e `rename`) so foi exercitado na sondagem da Rita, nao na suite | Acrescentar teste com `monkeypatch` de `organizer.os.rename` que cria o arquivo e levanta `FileExistsError` na primeira chamada | nao |
