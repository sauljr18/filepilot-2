# Validacao do item filepilot-fix2-3 - Instancia unica avisa quando nao consegue saber se ha outra janela aberta

**Item:** filepilot-fix2-3 | **Epico:** filepilot-fix2 | **Data:** 2026-10-12
Execucao: 20261012-151542
Veredito: APROVADO
**Tipo do item:** backend (logica de abertura do aplicativo; nenhuma tela, componente ou layout alterado)

Skills de stack declaradas (EF Core, .NET, Vuetify/Sneat, Go) nao lidas: o projeto e Python/PySide6.

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `mypy --platform win32 filepilot` exit 0, 23 arquivos, zero erros; zero erro novo vs baseline (`comm -13` vazio) |
| 2 Criterios de aceite | PASS | 5/5 criterios atendidos |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented, FIXME, print; zero caractere Unicode proibido; py_compile exit 0 |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint; sem credencial nem dado sensivel |
| 5 Testes | PASS | suite completa 395 passed, 2 skipped (so Windows: test_destination_checks.py:153, test_scanner_protected.py:185); 4 testes novos + 6 antigos de instancia unica verdes; teste de chmod rodou sem skip; mutacoes refeitas |
| 6 Consistencia entre documentos | PASS | texto de `_LOCK_UNAVAILABLE` identico ao da SPEC L1154; casos de teste 1 a 6 da SPEC L1162-1167 cobertos |
| 7b Varredura adversarial | PASS | consumidores de `open_main_window`: `main()` (`__main__.py:65`, trata qualquer `int`) e `tests/ui/test_close_and_db_error.py:81,95,110,124` (verdes); nenhum utilitario reinventado |
| 7c Degradacao e borda | PASS | ver abaixo; 1 achado desejavel, nenhum "sim" que decida |
| 7d Matriz (backend) | PASS | BE-1: `asyncio.new_event_loop` em `__main__.py` = 0; BE-2 e BE-3 n/a (sem DI nem policy) |
| 7e Funcao irma e comando citado | PASS | 7e-1 n/a (nenhuma funcao irma que decide e grava estado compartilhado); 7e-2 n/a (nenhuma mensagem manda rodar comando) |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix2-3-f1 | Classe falsa com `PermissionError`: `open_main_window` devolve 1, `critical` recebe o texto, `information` nao chamado | PASS | `__main__.py:48-53`; `test_single_instance_unknown.py:72-93` (asserts L88-90) |
| filepilot-fix2-3-f1 | `UnknownError`: 1 e mesmo texto; nos dois casos sem janela e sem `filepilot.db` | PASS | `test_single_instance_unknown.py:74` (parametro), L83 (`_forbid_window`), L92-93 (sem `unlock`, sem banco) |
| filepilot-fix2-3-f1 | `LockFailedError`: 0, `information` com "O FilePilot já está aberto.", `critical` nao chamado | PASS | `__main__.py:49-51`; `test_single_instance_unknown.py:96-111` (asserts L107-109) |
| filepilot-fix2-3-f1 | Pasta em `chmod 0o500` com trava real: 1 e `critical` com `_LOCK_UNAVAILABLE`; skip no Windows e sob permissao ignorada; `chmod` desfeito em `finally` | PASS | `test_single_instance_unknown.py:114-136` (skipif L114, sonda e skip L124-127, `finally` L130-131); executado, PASSED, nao pulado |
| filepilot-fix2-3-f1 | `tests/ui/test_single_instance.py` passa sem nenhuma alteracao | PASS | `git status --short` e `git diff --stat` do arquivo vazios; 6 passed |

## Mutacoes refeitas pela Rita

Reversao por copia de arquivo, `timeout` por rodada, `__main__.py` identico ao esperado no fim (`grep` e `git diff --stat` iguais ao Passo 0).

| # | Diff | Escopo | Resultado |
|---|------|--------|-----------|
| R1 | L49 `if lock.error() == _LOCK_HELD_BY_OTHER:` para `if True:` | suite completa | pega por assercao: 3 failed, 392 passed |
| R2 | L53 `return 1` para `return 0` | suite completa | pega por assercao: 3 failed, 392 passed |
| R3 | L49 `==` para `!=` | suite completa | trava (timeout 124): modal real nos testes antigos |
| R3 | L49 `==` para `!=` | so `test_single_instance_unknown.py` | pega por assercao: 4 failed |
| R4 | acrescenta `lock.unlock()` depois de L52 | suite completa | pega por assercao: 2 failed, 393 passed |
| R5 | L19 `LockFailedError` para `PermissionError` | suite completa | trava (timeout 124): modal real nos testes antigos |
| R5 | L19 `LockFailedError` para `PermissionError` | so `test_single_instance_unknown.py` | pega por assercao: 3 failed, 1 passed |
| R6 | L52 `QMessageBox.critical` para `QMessageBox.information` | suite completa | pega por assercao: 3 failed, 392 passed |

Concilia com a tabela do Carlos (M1, M2, M4 iguais; M3 igual a R3). Divergencia reportada: o resumo do Carlos cita os testes em L67-93, L96-110 e L113-133; no arquivo eles estao em L72-93, L96-111 e L114-136 (so numeracao, o codigo confere).

Armadilha de medicao: depois de R5 a suite completa travou mesmo com o fonte restaurado, porque `LockFailedError` e `PermissionError` tem o mesmo tamanho e o `.pyc` da mutacao ficou com o mesmo segundo do fonte restaurado. Corrigido com `touch filepilot/__main__.py`; suite completa reverificada: 395 passed, 2 skipped.

## Gate 7c

1. Parametro que antes degradava e agora lanca: nao. `lock.error()` devolve um enum e nao lanca.
2. Zero ou vazio que inverte classificacao: nao se aplica.
3. Fraqueza antiga que a mudanca torna material: nao. Registro, sem decidir: a falha de `mkdir` (`__main__.py:43-45`) continua usando `_DB_UNAVAILABLE`, texto que fala de historico e nao de pasta; a SPEC 37.4 (L1155, L1157) manda deixar como esta.
4. Comentario que virou falso: nao. A docstring de `open_main_window` foi atualizada (`__main__.py:37-39`); o comentario da L15 segue verdadeiro.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | tests/ui/test_single_instance_unknown.py | 72-75 | Nenhum teste cobre `QLockFile.LockError.NoError` depois de `tryLock(0)` falso, que a SPEC L1154 manda tratar como erro de acesso (`critical` e retorno 1) | Acrescentar `QLockFile.LockError.NoError` aos parametros de `test_falha_que_nao_e_outra_instancia_vira_erro_de_acesso`; nao exigido pelos casos 1 a 6 da SPEC | nao |
| 2 | tests/ui/test_single_instance.py e tests/ui/test_close_and_db_error.py | 44-70 e 81-124 | Esses testes usam a trava real sem espiao de `QMessageBox.critical`: uma regressao no ramo de erro (R3, R5) abre modal real e trava a suite em vez de falhar por assercao | Fora do escopo do item (criterio exige `test_single_instance.py` sem alteracao); considerar um item proprio para espiar `critical` nesses testes | nao |
| 3 | filepilot/__pycache__ e tests/**/__pycache__ | - | Diretorios `__pycache__` nao rastreados na area de trabalho e nao ha `.gitignore` no repositorio | Nao commitar; o commit deve ser escopado aos arquivos do item e a este relatorio | nao |
