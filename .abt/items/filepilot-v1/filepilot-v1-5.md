# filepilot-v1-5 - Organizacao com historico por arquivo
Epico: filepilot-v1 | Ordem: 5 | Pontos: 5 | Depende de: filepilot-v1-1,filepilot-v1-4

## Objetivo
organize move os arquivos do plano com os.rename, grava cada operacao no banco com commit imediato, reporta progresso e nunca sobrescreve nem apaga arquivo.

## Contexto herdado
Entregue por filepilot-v1-4 (commit 4d5a619). Nao reimplementar: a precedencia de regra, a categoria padrao, o sufixo `(n)` de nome repetido, a guarda de pasta e os testes de `tests/services/test_planner*.py`. `organize` recebe o `Plan` pronto e so o executa.

Artefatos criados:
- filepilot/services/planner.py - servico - exporta `build_plan(folder: Path, files: list[ScannedFile], rules: list[Rule]) -> Plan`
- tests/services/test_planner.py - testes - categoria, precedencia, `seq` e `skipped`
- tests/services/test_planner_conflicts.py - testes - sufixo `(n)`, maiusculas e plano sem efeitos
- tests/services/test_planner_guard.py - testes - `DESTINO_FORA_DA_PASTA`, arvore intacta e `is_empty`
- .abt/reviews/filepilot-v1-4.md - relatorio - veredito APROVADO da Rita

Contratos:
- `build_plan` (filepilot/services/planner.py): so le o disco (`os.scandir` nos destinos), nao cria pastas, nao move e nao toca no banco; nao recebe conexao. Devolve `Plan(folder, operations, skipped)` de `filepilot/domain/models.py`; `operations` segue a ordem de `files` com `seq` de 1 a N. Levanta `FilePilotError` com `DESTINO_FORA_DA_PASTA` e nenhum plano e devolvido.
- `PlannedOperation.category` guarda a CHAVE da categoria (`documentos`, `imagens`, `videos`, `compactados`), nunca a subpasta, e e `None` quando a regra vence; `rule_name` e o inverso. `destination_path` ja traz o nome final sem conflito no momento do plano.
- Armadilha: o plano e calculado antes da execucao, entao um arquivo pode surgir no destino depois dele. Reabrir o nome livre nesse caso e do `organize` (f2 deste item e SPEC 15.2, `FileExistsError` com novo sufixo): o helper privado `_free_name(name, taken)` recebe `taken` como conjunto de nomes ja em `casefold()`, e `_existing_names(directory)` le a pasta; ambos sao privados de planner.py, entao o `organize` precisa de uma funcao publica ou de importar o helper com decisao explicita, sem copiar a logica.
- Achado aberto do relatorio (nao bloqueia): a guarda de planner.py:85 e redundante com a de 76-77; a validacao de `rules.py` ja recusa `..`, `.` e segmento vazio em `destination_folder`.

Nomes decididos:
- Helpers privados de planner.py: `_error`, `_target`, `_existing_names`, `_inside` e `_free_name`; o dicionario de mensagens do modulo e `_MESSAGES` (so `DESTINO_FORA_DA_PASTA`).
- Os testes do planner ficam em `tests/services/test_planner.py` e `test_planner_<assunto>.py` (`conflicts`, `guard`), a convencao de `test_<modulo>_<assunto>.py`.

Padroes estabelecidos:
- Nomes comparados sem diferenciar maiusculas por `casefold()`, inclusive a chave do cache de pasta (`str(directory).casefold()`).
- Guarda de pasta por `destination.resolve().is_relative_to(folder.resolve())` na funcao `_inside`, aplicada antes de ler o destino e depois do sufixo.
- Os testes montam `ScannedFile` e `Rule` a mao, com um helper `_file` local por arquivo, e usam `tmp_path` sem `monkeypatch`.

## Features

### filepilot-v1-5-f1 organize move os arquivos e registra a organizacao
Linhas da SPEC: .abt/SPEC.md L292-313
Arquivos:
- filepilot/services/organizer.py (novo)
- tests/services/test_organizer.py (novo)
Criterios de aceite:
- `organize` em `tmp_path` move os N arquivos do plano e grava 1 `organizations` (status `concluida`, `moved_count` igual a N, `finished_at` preenchido) e N `operations` `movido` com `seq` de 1 a N e `destination_path` final.
- Cada operacao e gravada com `commit` imediato: dentro do `progress_callback` uma segunda conexao ja enxerga as operacoes anteriores.
- Plano vazio devolve `OrganizationResult` com contagens 0 e `organization_id` 0 sem gravar nenhuma `organizations`.
- `simulate(plan)` devolve o mesmo plano e a arvore da pasta fica identica.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_organizer.py -> exit 0
- parser: python -m py_compile filepilot/services/organizer.py -> exit 0
- grep deve casar: os.rename em filepilot/services/organizer.py
- grep nao deve casar: os.replace em filepilot/services
- grep nao deve casar: shutil.move em filepilot/services
Dicas:
- A organizacao abre com `status = 'em_andamento'` e `commit` antes do primeiro arquivo e fecha com `concluida` (SPEC 5.3, L143-186).
- Datas em UTC ISO 8601; `created_at` e `updated_at` preenchidos em cada linha.
- `mkdir(parents=True, exist_ok=True)` so cria a subpasta de destino dentro da pasta escolhida.

### filepilot-v1-5-f2 Progresso e conflito de nome durante a execucao
Linhas da SPEC: .abt/SPEC.md L292-313
Arquivos:
- filepilot/services/organizer.py (novo)
- tests/services/test_organizer_conflicts.py (novo)
Criterios de aceite:
- `progress_callback(done, total, filename)` e chamado N+1 vezes: uma antes de cada arquivo, com `done` de 0 a N-1, e uma ao final com `done` igual a `total`.
- Arquivo criado no destino entre o plano e a execucao faz o `FileExistsError` do `os.rename` recalcular o sufixo (1) e o arquivo novo ser movido; o arquivo existente mantem o mesmo conteudo.
- O `destination_path` gravado e o nome final com sufixo.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_organizer_conflicts.py -> exit 0
- grep deve casar: FileExistsError em filepilot/services/organizer.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Reutilize a funcao de sufixo do planner (item filepilot-v1-4, f2) em vez de duplicar a logica.
- O desfazer usa o nome final gravado, entao ele nunca pode ser o nome original.

### filepilot-v1-5-f3 Falha por arquivo, trava e falha de gravacao
Linhas da SPEC: .abt/SPEC.md L292-313
Arquivos:
- filepilot/services/organizer.py (novo)
- tests/services/test_organizer_failures.py (novo)
Criterios de aceite:
- `PermissionError` simulado em 1 arquivo grava `operations` `falha` com `destination_path` NULL e `error_message` preenchido, incrementa `failed_count` e os demais arquivos sao movidos.
- `OPERATION_LOCK` impede duas execucoes ao mesmo tempo: a segunda chamada de `organize` levanta `ORGANIZACAO_EM_ANDAMENTO`, e depois de uma excecao o `finally` libera a trava.
- `sqlite3.Error` ao gravar uma operacao devolve o arquivo ja movido ao lugar original e levanta `BANCO_INDISPONIVEL`.
- Todo destino e reconferido com `is_relative_to` antes do `os.rename`; fora da pasta a operacao vira `falha`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_organizer_failures.py -> exit 0
- grep deve casar: OPERATION_LOCK em filepilot/services/organizer.py
- grep deve casar: acquire(blocking=False) em filepilot/services/organizer.py
Dicas:
- `OPERATION_LOCK = threading.Lock()` e compartilhado com `undo_last` (item filepilot-v1-7); adquira sem bloquear e solte em `finally`.
- Os textos amigaveis de `error_message` entram no item filepilot-v1-6; aqui basta um texto nao vazio.
- Falha de gravacao: SPEC 6.3 penultimo item e tabela de erros em 9 (L569-592).

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
