# Validacao do item filepilot-fix3-3 - Laco de atalhos detectado tambem no Windows

**Item:** filepilot-fix3-3 | **Epico:** filepilot-fix3 | **Data:** 2026-10-13
Execucao: 20261013-171258
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `mypy --platform win32` exit 0, 27 arquivos, zero erros novos contra a baseline |
| 2 Criterios de aceite | PASS | 7/8 atendidos, 1 NAO VERIFICAVEL (job windows-latest) |
| 3 Qualidade de codigo | PASS | zero TODO/placeholder/FIXME, zero Unicode tipografico, sem codigo comentado nem print |
| 4 Autorizacao e seguranca | PASS | n/a: sem endpoint; a travessia so le o disco (`is_symlink` e `readlink`) e nunca levanta |
| 5 Testes | PASS | `pytest` 498 passed, 2 skipped (ambos de plataforma, em arquivos fora do item); 3 mutacoes refeitas e pegas |
| 6 Consistencia entre documentos | PASS | codigo e testes batem com SPEC L1317-1335 (helper, ordem fixa, limite 40, testes 1 a 9) |
| 7b Varredura adversarial | PASS | consumidores `scan_folder`, `build_plan` e `_inside` passam por `resolve_folder` sem mudar; nenhum utilitario duplicado |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim"; sonda propria: relativo, `..`, raiz e laco real no Linux ok |
| 7d Matriz (backend) | PASS | BE-1 n/a; BE-2 n/a (sem service novo a registrar); BE-3 n/a (sem `Authorize`) |
| 7e Funcao irma e comando citado | PASS | nenhuma divergencia: `_crosses_symlink_loop` nao grava estado; nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix3-3-f1 | `Path.resolve` identidade e laco real: `PASTA_INVALIDA` com `__cause__ is None` | PASS | filepilot/services/scanner.py:95-96; tests/services/test_planner_loop.py:119; tests/services/test_scanner_loop.py:98 e :163 |
| filepilot-fix3-3-f1 | `RuntimeError("Symlink loop")`: `__cause__` `RuntimeError` e `_crosses_symlink_loop` nao chamado | PASS | filepilot/services/scanner.py:89-90; tests/services/test_scanner_loop.py:142 |
| filepilot-fix3-3-f1 | `_crosses_symlink_loop` nunca levanta: `OSError` em `is_symlink` ou `readlink` devolve `False` | PASS | filepilot/services/scanner.py:80-81; tests/services/test_scanner_loop.py:235 e :249; tests/services/test_planner_loop.py:182 |
| filepilot-fix3-3-f1 | Mais de 40 saltos devolve `True`; link valido e caminho inexistente devolvem `False` | PASS | filepilot/services/scanner.py:72; tests/services/test_scanner_loop.py:223, :201, :184, :192 |
| filepilot-fix3-3-f2 | `pytest` dos dois arquivos exit 0 no Linux e sem `Path.resolve nao detecta o laco nesta plataforma` | PASS | `pytest` completo: 498 passed; `grep` da mensagem em tests/services/test_planner_loop.py e test_scanner_loop.py: zero |
| filepilot-fix3-3-f2 | `_symlink` faz `pytest.skip`, exceto win32 com `GITHUB_ACTIONS` igual a `true`, onde faz `pytest.fail` | PASS | tests/services/test_planner_loop.py:27-33; tests/services/test_scanner_loop.py:27-33 |
| filepilot-fix3-3-f2 | Testes novos cobrem emulacao Windows (`build_plan` e `scan_folder`), ciclo `a -> b -> a`, link valido, `__cause__`, `readlink` EACCES e `is_symlink` PermissionError | PASS | tests/services/test_planner_loop.py:119, :136, :151, :167, :182; tests/services/test_scanner_loop.py:98, :113, :129, :142, :163, :235, :249 |
| filepilot-fix3-3-f2 | Job de testes do GitHub Actions em `windows-latest` verde, sem teste de laco pulado | NAO VERIFICAVEL | sem commit nem solicitacao ainda: nao ha run com `headSha` igual ao HEAD do item; a hipotese sobre o `Path.resolve` do Windows nao foi medida (SPEC L1317) |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | tests/services/test_scanner_loop.py | 98 | `test_pasta_que_aponta_para_si_mesma_com_resolve_do_windows_vira_pasta_invalida` e `test_ciclo_de_dois_atalhos_com_resolve_do_windows_vira_pasta_invalida` (:113) passam mesmo sem a travessia: com a chamada removida de `resolve_folder` (mutacao RM1), `folder.is_dir()` ja recusa o laco e cai em `PASTA_INVALIDA` por outro caminho. Quem prova a travessia no scanner e o espiao de :163 | Opcional: tornar as duas emulacoes sensiveis a travessia, por exemplo trocando tambem `Path.is_dir` na emulacao ou espiando `_crosses_symlink_loop`. Sem isso o job windows-latest e a unica prova do caminho `scan_folder` no Windows | nao |
| 2 | tests/services/test_planner_loop.py | 182 | O teste do `readlink` EACCES roda com `Path.resolve` emulado, nao com `resolve` real: com o `resolve` real, `posixpath.realpath` tambem chama `os.readlink` e levantaria o EACCES antes da travessia | Nenhuma: a SPEC L1334 pede o plano normal, e a emulacao e o unico jeito de isolar a travessia. Registro para a pessoa saber o escopo | nao |

Mutacoes refeitas pela Rita (suite inteira, `PYTHONUNBUFFERED=1 timeout -s INT -k 30 300 pytest`, reversao por copia de arquivo, `git status --short` e `git diff --stat` iguais aos do Passo 0):

| Mutacao | Diff | Resultado |
|---------|------|-----------|
| RM1 | remove `if _crosses_symlink_loop(folder): raise _error("PASTA_INVALIDA")` de `resolve_folder` | 3 failed, 495 passed, 2 skipped |
| RM2 | move esse `if` para antes do `try: resolved = folder.resolve()` | 1 failed (`test_resolve_que_levanta_runtime_error_nao_chama_a_travessia`), 497 passed, 2 skipped |
| RM3 | `if hops > _MAX_SYMLINK_HOPS` vira `if hops >= _MAX_SYMLINK_HOPS` | 1 failed (`test_travessia_conta_so_os_saltos_de_atalho_e_passa_de_40_devolve_true`), 497 passed, 2 skipped |
