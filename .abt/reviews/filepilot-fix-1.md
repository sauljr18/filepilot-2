# Validacao do item filepilot-fix-1 - Laco de atalhos na leitura da pasta vira PASTA_INVALIDA

**Item:** filepilot-fix-1 | **Epico:** filepilot-fix | **Data:** 2026-10-12
Execucao: 20261012-104146
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "no issues found in 14 source files"; `comm` contra a baseline: zero erro novo |
| 2 Criterios de aceite | PASS | 4/4 criterios atendidos |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented e FIXME; sem codigo comentado nem print; sem unicode proibido |
| 4 Autorizacao e seguranca | PASS | n/a: nao ha endpoint; a pasta de rede continua recusada antes de resolver (scanner.py:105-106) |
| 5 Testes | PASS | suite completa 225 passed, 2 skipped (ambos so do Windows, com justificativa no `skipif`); mutacoes refeitas |
| 6 Consistencia entre documentos | PASS | codigo bate com SPEC 27.2 (L919-939): helper, tipos convertidos, ordem das verificacoes, mensagem fixa |
| 7b Varredura adversarial | PASS | unico chamador de `_is_protected` e `scan_folder`; ver achado 1 (desejavel) |
| 7c Degradacao e borda | PASS | uma resposta "sim" na pergunta 3, registrada como achado 1 (desejavel) |
| 7d Matriz (backend) | PASS | BE-1 n/a; BE-2 n/a (sem service novo a registrar); BE-3 n/a (Python) |
| 7e Funcao irma e comando citado | PASS | nenhuma divergencia: `_resolve_folder` nao escreve estado e nenhuma mensagem cita comando |

## Evidencias dos gates

- Gate 1: saida em `abt-review-filepilot-fix-1.typecheck` (diretorio git da area de trabalho); baseline `abt-typecheck-filepilot-fix-1.base` com a mesma saida (exit 0).
- Gate 5 (comandos): `pytest tests/services/test_scanner_loop.py tests/services/test_scanner_protected.py -v` = 22 passed, 1 skipped; `pytest -q -rs` = 225 passed, 2 skipped (`tests/services/test_destination_checks.py:153` e `tests/services/test_scanner_protected.py:150`, ambos "so existe no Windows").
- Gate 5 (mutacoes refeitas por Rita, suite completa, revertidas por copia de arquivo, `git status --short` e `git diff --stat` iguais aos do inicio):

| # | Diff da mutacao em filepilot/services/scanner.py | Resultado |
|---|---|---|
| M1 | L56 `except RuntimeError as exc:` -> `except ZeroDivisionError as exc:` | 2 failed (test_laco_de_atalhos_levantado_como_runtime_error_vira_pasta_invalida, test_laco_real_de_atalhos_vira_pasta_invalida), 223 passed |
| M2 | L59 remove `exc.errno == errno.ELOOP or ` | 1 failed (test_oserror_eloop_na_resolucao_vira_pasta_invalida), 224 passed |
| M3 | L59 condicao substituida por `if True:` (todo OSError vira PASTA_INVALIDA) | 1 failed (test_oserror_eacces_na_resolucao_continua_sendo_oserror), 224 passed |
| M4 | remove a checagem de rede `\\` de `scan_folder` (L105-106) e de `_is_protected` (L66-67) | 1 failed (test_caminho_unc_e_protegido), 224 passed |

Os numeros de M1 a M3 coincidem com os do Carlos (mesmo escopo: suite completa). M4 e acrescimo da Rita.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix-1-f1 | Com `Path.resolve` trocado por monkeypatch para levantar `RuntimeError("Symlink loop")`, `scan_folder` levanta `FilePilotError` PASTA_INVALIDA, message igual ao texto de 6 e sem "Symlink loop" | PASS | filepilot/services/scanner.py:55-57 e :13; tests/services/test_scanner_loop.py:31-43 |
| filepilot-fix-1-f1 | `OSError` com `errno.ELOOP` na resolucao da PASTA_INVALIDA; com `errno.EACCES` continua `OSError` | PASS | filepilot/services/scanner.py:58-61; tests/services/test_scanner_loop.py:46-72 |
| filepilot-fix-1-f1 | Laco real a -> b e b -> a criado com `Path.symlink_to` da PASTA_INVALIDA; `pytest.skip` se o sistema recusar o link | PASS | tests/services/test_scanner_loop.py:24-28 e :75-85 (executou e passou nesta maquina) |
| filepilot-fix-1-f1 | Pasta valida com link `up` apontando para `..` continua listando so os arquivos regulares | PASS | tests/services/test_scanner_loop.py:88-92 (passou); filepilot/services/scanner.py:91 (`_scan_entry` descarta nao regulares) |

Verificacao do detalhe: py_compile exit 0; `def _resolve_folder` casa em scanner.py:52; `winerror` casa em scanner.py:59; grep de unicode proibido em scanner.py sem resultado; gate de placeholder (`awk`) com saida vazia; ordem de `scan_folder` (rede, resolve, protegida, is_dir, listagem) em scanner.py:105-110.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/services/planner.py | 49 | `_inside` chama `destination.resolve()` e `folder.resolve()` sem converter laco de atalhos: a mesma fraqueza antiga (RuntimeError) existe fora do escopo do item; o item a deixa de fora e `scan_folder` ja barra a pasta de origem antes | Decidir no ponto de checagem se vira item proprio de correcao; nenhuma mudanca neste item | nao |
| 2 | .abt/items/filepilot-fix/filepilot-fix-1.md | 8-10 | `## Contexto herdado` esta com `-` apesar de `Depende de: filepilot-v1-2` | Registrado pelo Ivan no preflight; sem impacto no codigo entregue | nao |
