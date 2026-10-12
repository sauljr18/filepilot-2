# filepilot-v1-6 - Verificacoes de destino e textos de falha
Epico: filepilot-v1 | Ordem: 6 | Pontos: 3 | Depende de: filepilot-v1-5

## Objetivo
A organizacao recusa caminho de destino acima de 259 caracteres e subpasta de destino que e atalho, e grava os textos amigaveis de falha por arquivo, sem nenhuma chamada proibida nos servicos.

## Contexto herdado
Entregue por filepilot-v1-5 (commit c297d88). Nao reimplementar: `organize`, `simulate`, a trava, o sufixo `(n)` na execucao, a gravacao do historico e os testes de `tests/services/test_organizer*.py`. As verificacoes de 6.7 e os textos de falha desta feature JA existem dentro de `organize`: este item os move para `destination_checks.py` e os cobre com testes proprios, sem mudar o comportamento.

Artefatos criados:
- filepilot/services/organizer.py - servico - exporta `OPERATION_LOCK`, `simulate(plan: Plan) -> Plan` e `organize(plan, conn, progress_callback=None) -> OrganizationResult`
- tests/services/test_organizer.py - testes - historico, commit imediato, plano vazio e `simulate`
- tests/services/test_organizer_conflicts.py - testes - progresso N+1 e sufixo na execucao
- tests/services/test_organizer_failures.py - testes - `PermissionError`, trava, `sqlite3.Error`, guarda de pasta, atalho por link simbolico e caminho longo
- .abt/reviews/filepilot-v1-5.md - relatorio - veredito APROVADO da Rita

Contratos:
- `organize` (organizer.py:224): plano vazio devolve `OrganizationResult(0, 0, 0)` sem gravar; a trava e tomada com `acquire(blocking=False)` e solta em `finally`; `sqlite3.Error` devolve o arquivo ao lugar e levanta `BANCO_INDISPONIVEL`. `failures` e uma lista de `(nome do arquivo, motivo)`.
- A ordem por arquivo esta em `_move_file` (organizer.py:95): caminho acima de 259, atalho em cada nivel da subpasta, `_inside`, `mkdir`, `os.rename`; cada falha devolve `(None, texto)` e o destino final vem como `(Path, None)`. O texto da falha vai para `operations.error_message`.
- Os textos de 6.7 sao as constantes `_IN_USE`, `_NO_PERMISSION`, `_NOT_FOUND`, `_TOO_LONG`, `_SHORTCUT`, `_OUTSIDE`, `_MKDIR` e `_OTHER` (organizer.py:33-40), escolhidas por `_failure_text(exc, creating)` (organizer.py:82); `_is_shortcut` e `_has_shortcut` (organizer.py:58 e 68) fazem a checagem de link simbolico, junction e `FILE_ATTRIBUTE_REPARSE_POINT`.
- Armadilha: no Linux `os.rename` sobrescreve em silencio, por isso `_move_file` recusa com `os.path.lexists` antes (organizer.py:115). Mantenha essa recusa ao mover o codigo.
- Achados abertos da Rita (nao bloqueiam): depois de `BANCO_INDISPONIVEL` a conexao fica em transacao aberta, sem o `rollback` que `rules._transaction` faz (organizer.py:205-212); `_utc_now` repete o de rules.py:40; falta teste do `FileExistsError` levantado pelo `os.rename` real.

Nomes decididos:
- Os helpers de organizer.py importam `_existing_names`, `_free_name` e `_inside` do planner por decisao explicita; ao extrair para `destination_checks.py`, o import do planner nao deve voltar a ser copia de logica.
- Os testes do organizer ficam em `tests/services/test_organizer.py` e `test_organizer_<assunto>.py` (`conflicts`, `failures`).

Padroes estabelecidos:
- Os testes criam o banco com `open_connection(tmp_path / "historico.db")` e montam o plano com `build_plan` ou, para forcar o destino, com `Plan` e `PlannedOperation` a mao.
- Falha de gravacao no banco e simulada com um `TRIGGER ... RAISE(ABORT, ...)` em `operations`, sem mock da conexao.
- Falha de `os.rename` e simulada com `monkeypatch.setattr(organizer.os, "rename", ...)`.

O item filepilot-v1-5 entregou toda a execucao de `organize`, inclusive as verificacoes e os textos de 6.7: NAO reimplementar, so reorganizar em `destination_checks.py` e acrescentar a classificacao de `ERRO_INTERNO` e o teste de chamadas proibidas.

## Features

### filepilot-v1-6-f1 Caminho longo e subpasta de destino que e atalho
Linhas da SPEC: .abt/SPEC.md L377-402
Arquivos:
- filepilot/services/destination_checks.py (novo)
- filepilot/services/organizer.py (novo)
- tests/services/test_destination_checks.py (novo)
Criterios de aceite:
- Destino com mais de 259 caracteres vira `falha` com "caminho de destino muito longo" e nenhum `os.rename` e chamado para ele.
- Subpasta `Documentos` que ja existe como junction ou link simbolico para fora da pasta resulta em `falha` com "a subpasta de destino é um atalho" para todos os arquivos desse destino e zero arquivos movidos para fora da pasta (teste no windows-latest).
- A verificacao vale para cada nivel da subpasta de uma regra com varios segmentos.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_destination_checks.py -> exit 0
- parser: python -m py_compile filepilot/services/destination_checks.py -> exit 0
- grep deve casar: isjunction em filepilot/services/destination_checks.py
- grep deve casar: 259 em filepilot/services/destination_checks.py
Dicas:
- Link simbolico: `Path.is_symlink()`; junction: `os.path.isjunction()` ou `FILE_ATTRIBUTE_REPARSE_POINT` em `st_file_attributes` (SPEC 6.7, item 2).
- As verificacoes rodam antes do `mkdir` e do `os.rename` da secao 6.3 (passo 0).
- Testes de junction usam `skipif` fora do Windows e rodam no windows-latest.

### filepilot-v1-6-f2 Textos amigaveis de falha por arquivo
Linhas da SPEC: .abt/SPEC.md L377-402
Arquivos:
- filepilot/services/destination_checks.py (novo)
- filepilot/services/organizer.py (novo)
- tests/services/test_failure_messages.py (novo)
Criterios de aceite:
- `error_message` usa "arquivo em uso por outro programa" para `winerror` 32, "sem permissão para mover o arquivo" para outro `PermissionError`, "arquivo não encontrado" para `FileNotFoundError`, "não foi possível criar a subpasta de destino" para falha de `mkdir` e "erro ao mover o arquivo" para qualquer outro `OSError`.
- O texto bruto do sistema nunca e gravado em `operations.error_message`.
- Excecao inesperada fora do tratamento por arquivo vira `FilePilotError("ERRO_INTERNO", "Ocorreu um erro inesperado. Tente de novo.")`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_failure_messages.py -> exit 0
- grep deve casar: arquivo em uso por outro programa em filepilot/services
- grep deve casar: ERRO_INTERNO em filepilot
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Tabela de condicao e texto em 6.7 (ultima tabela); o desfazer usa "erro ao mover o arquivo" para `OSError` ao restaurar.
- `winerror` so existe no Windows; use `getattr(exc, "winerror", None)`.

### filepilot-v1-6-f3 Teste de repositorio contra chamadas proibidas
Linhas da SPEC: .abt/SPEC.md L597-622
Arquivos:
- tests/test_repository_rules.py (novo)
Criterios de aceite:
- `os.replace`, `shutil.move`, `os.remove`, `Path.unlink` e `shutil.rmtree` aparecem 0 vezes em `filepilot/services`.
- Importacao de `socket`, `http`, `urllib` e `requests` aparece 0 vezes em `filepilot`.
- O teste falha se alguma dessas chamadas for acrescentada.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/test_repository_rules.py -> exit 0
- grep nao deve casar: shutil.rmtree em filepilot/services
- grep nao deve casar: import socket em filepilot
Dicas:
- Lista de verificacao da secao 11: NFR-001 exige zero sobrescritas e zero operacoes fora da pasta; o teste le os arquivos `.py` com `pathlib` e procura os nomes.
- O `rmdir` do desfazer (item filepilot-v1-7) usa `Path.rmdir`, que nao esta na lista proibida.

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
