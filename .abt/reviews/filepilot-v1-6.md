# Validacao do item filepilot-v1-6 - Verificacoes de destino e textos de falha

**Item:** filepilot-v1-6 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-102352
Veredito: APROVADO
**Tipo do item:** backend (com refatoracao: `organizer.py` delega as verificacoes e os textos a `destination_checks.py`)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "no issues found in 14 source files"; baseline do Carlos exit 0 (13 arquivos); zero erro novo |
| 2 Criterios de aceite | PASS | 9/9 criterios atendidos (ressalva no criterio f2-3, ver lista de correcoes) |
| 3 Qualidade de codigo | PASS | zero `TODO`, `placeholder`, `not implemented`, `FIXME`, `print` e codigo comentado nos 5 arquivos do diff; zero caractere Unicode proibido em `filepilot` |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint; as verificacoes so recusam, nunca ampliam o que e movido |
| 5 Testes | PASS | `pytest` 220 passed, 2 skipped; os 2 skips sao so Windows (`test_destination_checks.py:153` junction e `test_scanner_protected.py:150`), com motivo escrito; 48 testes novos/alterados do item verdes |
| 6 Consistencia entre documentos | PASS | nomes e textos batem com a tabela de 6.7 (SPEC L387-397) e com o contexto herdado (`_failure_text`, `_has_shortcut` agora `failure_text`, `has_shortcut` em `destination_checks.py`) |
| 7b Varredura adversarial | PASS | nenhum consumidor dos nomes antigos (`grep` de `_is_shortcut`, `_failure_text`, `_MAX_PATH` etc. fora de `destination_checks.py`: zero); `_inside` importado do planner, sem copia |
| 7c Degradacao e borda | PASS | ver lista de correcoes (itens 2 e 3); nenhum 5xx novo; ordem 259, atalho, guarda, `mkdir`, `os.path.lexists` preservada |
| 7d Matriz (backend, refatoracao) | PASS | BE-1: `grep` de `shutil.rmtree` e `import socket` em `filepilot` = zero; BE-2 e BE-3 n/a; RF-1 suite completa verde, nenhum teste existente alterado; RF-2 `grep` dos nomes antigos = zero; RF-3 verificacoes e textos agora so em `destination_checks.py` |
| 7e Funcao irma e comando citado | PASS | `check_destination` e `failure_text` nao leem nem gravam estado compartilhado; nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-6-f1 | Destino com mais de 259 caracteres vira `falha` com "caminho de destino muito longo" e nenhum `os.rename` e chamado | PASS | `destination_checks.py:48-49`; `organizer.py:68-70`; `test_destination_checks.py:61` (`calls == []`), `:43` e `:52` (limite 259 e 260) |
| filepilot-v1-6-f1 | Subpasta existente como junction ou link para fora resulta em `falha` "a subpasta de destino é um atalho" para todos os arquivos e zero movidos para fora | PASS | `destination_checks.py:29-36` (`is_symlink`, `isjunction`, `FILE_ATTRIBUTE_REPARSE_POINT`) e `:50-51`; `test_destination_checks.py:84` (link real, `outside` vazio); junction real so em `:153`, que pula fora do Windows |
| filepilot-v1-6-f1 | A verificacao vale para cada nivel da subpasta | PASS | `destination_checks.py:39-50` (percorre `relative.parts`); `test_destination_checks.py:109` e `:122` |
| filepilot-v1-6-f2 | `error_message` usa os 5 textos da tabela (winerror 32, outro `PermissionError`, `FileNotFoundError`, `mkdir`, outro `OSError`) | PASS | `destination_checks.py:17-24` e `:64-74`; `test_failure_messages.py:62`, `:72`, `:82`, `:92`, `:102`, `:120`, gravados em `operations.error_message` |
| filepilot-v1-6-f2 | O texto bruto do sistema nunca e gravado em `operations.error_message` | PASS | `test_failure_messages.py:58` (`RAW_TEXT not in row[2]`) em todos os casos que passam por `_stored_message` |
| filepilot-v1-6-f2 | Excecao inesperada fora do tratamento por arquivo vira `FilePilotError("ERRO_INTERNO", "Ocorreu um erro inesperado. Tente de novo.")` | PASS | `organizer.py:34` e `:42-50`; `test_failure_messages.py:136` e `:145`. Ressalva: a funcao `internal_error` existe e e testada, mas nao e chamada por `organize` nem por outro codigo (lista de correcoes, item 1) |
| filepilot-v1-6-f3 | `os.replace`, `shutil.move`, `os.remove`, `Path.unlink` e `shutil.rmtree` aparecem 0 vezes em `filepilot/services` | PASS | `test_repository_rules.py:24` e `:67`; `grep` independente de `shutil.rmtree` em `filepilot` = zero |
| filepilot-v1-6-f3 | Importacao de `socket`, `http`, `urllib` e `requests` aparece 0 vezes em `filepilot` | PASS | `test_repository_rules.py:45` e `:76`; `grep` independente de `import socket` = zero |
| filepilot-v1-6-f3 | O teste falha se alguma dessas chamadas for acrescentada | PASS | `test_repository_rules.py:101` (10 trechos proibidos, inclusive `from shutil import move as ...`) e `:132` (9 trechos de rede); as mutacoes nao foram refeitas, ver divergencia abaixo |

## Divergencias e o que NAO foi verificado

- Prova por mutacao do Carlos (f3: `os.replace` em `organizer.py` e `import socket` em `scanner.py`, cada uma derrubando 1 teste, 219 passed): NAO refiz. O comando das mutacoes (copia, `sed` e reversao em `filepilot/services`) foi negado pelo modo de permissao da sessao e a pessoa pediu o caminho mais simples. Fechei pela leitura do detector (`test_repository_rules.py:24-64`) e pelos testes parametrizados dele (`:101`, `:114`, `:132`, `:145`), que provam que ele acusa e aceita os trechos certos. Quem quiser a prova por mutacao medida por mim precisa liberar o comando e revalidar.
- Junction real: so o `windows-latest` roda `test_destination_checks.py:153`; no Linux a cobertura e por link simbolico.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/services/organizer.py | 42 | `internal_error` nao e usada fora dos testes; ninguem converte hoje excecao inesperada em `ERRO_INTERNO` (a SPEC 6.7 manda no `OrganizeWorker`, que ainda nao existe, e `test_a_trava_e_liberada_depois_de_uma_excecao` exige `RuntimeError` cru de `organize`) | Chamar `internal_error` no `OrganizeWorker` e no desfazer quando eles forem criados (itens seguintes) | nao |
| 2 | tests/test_repository_rules.py | 24 | O detector nao pega alias: `import shutil as sh; sh.move(...)` e `import os as o; o.replace(...)` passam (sonda feita so por leitura, nao executada) | Resolver os aliases de `import ... as` na arvore antes de comparar os nomes | nao |
| 3 | filepilot/services/organizer.py | 19 | O comentario "Decisao explicita (filepilot-v1-4)" agora fica acima do `import` de `destination_checks`, nao do import do planner a que se refere | Mover o comentario para junto de `from filepilot.services.planner import ...` (linha 27) | nao |

Nota: o detalhe do item lista `organizer.py` como "(novo)", mas ele ja existia desde o filepilot-v1-5; o item so o alterou.
