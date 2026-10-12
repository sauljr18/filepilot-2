# filepilot-v1-4 - Planejamento das operacoes e conflitos de nome
Epico: filepilot-v1 | Ordem: 4 | Pontos: 6 | Depende de: filepilot-v1-1,filepilot-v1-2

## Objetivo
build_plan calcula a lista de operacoes com categoria padrao, precedencia de regra, sufixo de nome repetido e guarda de pasta, sem tocar no disco nem no banco.

## Contexto herdado
Entregue por filepilot-v1-2 (commit fe1ae8b). Nao reimplementar: a leitura do nivel da pasta (`scan_folder`), a normalizacao de extensao, a recusa de pasta invalida, ilegivel, vazia, protegida ou de rede e os testes de `tests/services`.

Artefatos criados:
- filepilot/services/__init__.py - pacote - docstring apenas; `planner.py` entra neste pacote
- filepilot/services/scanner.py - servico - exporta `scan_folder(folder: Path) -> list[ScannedFile]`
- tests/services/__init__.py - pacote de testes - a pasta `tests/services` ja existe; novos testes entram nela
- tests/services/test_scanner.py - testes - listagem, ordenacao, extensao, erros de pasta, link simbolico e `.lnk`
- tests/services/test_scanner_protected.py - testes - pastas protegidas e de rede, com `monkeypatch` de `os.environ` e de `scanner._drive_type`
- .abt/reviews/filepilot-v1-2.md - relatorio - veredito APROVADO da Rita

Contratos:
- `scan_folder` (filepilot/services/scanner.py): recebe `Path`, devolve `list[ScannedFile]` ja ordenada por `name` sem diferenciar maiusculas, com `extension` em minusculas, sem ponto (`""` se nao houver; `a.tar.gz` vira `gz`). Levanta `FilePilotError` com `PASTA_INVALIDA`, `PASTA_PROTEGIDA`, `PASTA_ILEGIVEL` ou `PASTA_VAZIA`. So le o disco; `build_plan` recebe essa lista pronta e nao chama `scan_folder`.
- Mensagens de erro: ficam no dicionario `_MESSAGES` de scanner.py (privado, texto igual ao da tabela da SPEC secao 6); o planner nao as reutiliza.
- Armadilha: o relatorio da Rita lista 3 achados abertos que nao bloqueiam e nao pertencem ao planner: laco de link simbolico na pasta escolhida faz `resolve()` levantar `RuntimeError` (scanner.py:52), variavel de ambiente vazia vira a pasta atual (scanner.py:56) e empate de nomes que diferem so por maiuscula tem ordem nao deterministica (scanner.py:101).

Nomes decididos:
- Os helpers privados de scanner.py sao `_read_stat`, `_drive_type`, `_is_protected`, `_extension` e `_scan_entry`; os testes trocam `_read_stat` e `_drive_type` por `monkeypatch`.
- Os testes de servico ficam em `tests/services/test_<modulo>.py` e, quando um modulo tem varios assuntos, em `test_<modulo>_<assunto>.py` (como `test_scanner_protected.py`).

Padroes estabelecidos:
- Simular Windows no Linux e por `monkeypatch` (`os.environ`, atributos de `stat` e `ctypes.windll` com `raising=False`); teste que so vale no Windows usa `skipif`.
- O servico levanta `FilePilotError(code, message)` pelo helper `_error(code)`, com `message` vindo do dicionario de mensagens do proprio modulo.
- Comparacao de nome sem diferenciar maiusculas usa `str.casefold()`.

## Features

### filepilot-v1-4-f1 Categorizacao e precedencia de regra
Linhas da SPEC: .abt/SPEC.md L276-291
Arquivos:
- filepilot/services/planner.py (novo)
- tests/services/test_planner.py (novo)
Criterios de aceite:
- Com `fatura.pdf`, `foto.JPG` e `setup.exe`, `build_plan` devolve 2 operacoes (`Documentos` e `Imagens`) e 1 arquivo em `skipped`.
- A regra de menor `position` cujo conjunto de extensoes contem a do arquivo vence a regra posterior e a categoria padrao.
- Operacao de regra tem `rule_name` da vencedora e `category` `None`; operacao de categoria padrao tem `category` preenchida e `rule_name` `None`.
- `seq` comeca em 1 e segue a ordem dos arquivos recebidos.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_planner.py -> exit 0
- parser: python -m py_compile filepilot/services/planner.py -> exit 0
- grep deve casar: skipped em filepilot/services/planner.py
Dicas:
- As categorias e extensoes vem de filepilot/domain/categories.py (SPEC 5.5, L216-231); a regra vence a categoria quando as duas casam.
- `PlannedOperation` usa `source_path` e `destination_path`, os mesmos nomes de `operations` (SPEC 5.3).

### filepilot-v1-4-f2 Sufixo de nome repetido no destino
Linhas da SPEC: .abt/SPEC.md L276-291
Arquivos:
- filepilot/services/planner.py (novo)
- tests/services/test_planner_conflicts.py (novo)
Criterios de aceite:
- Destino com `Documentos/fatura.pdf` existente gera `fatura (1).pdf`; com `(1)` tambem existente gera `fatura (2).pdf`.
- `arquivo.tar.gz` com destino ocupado vira `arquivo.tar (1).gz` e arquivo sem extensao vira `README (1)`.
- A comparacao de nomes ignora maiusculas e minusculas, como no Windows.
- Nenhum arquivo existente no destino e alterado; nenhuma pasta e criada.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_planner_conflicts.py -> exit 0
- parser: python -m py_compile filepilot/services/planner.py -> exit 0
- grep deve casar: .suffix em filepilot/services/planner.py
Dicas:
- O nome final vira `<base> (n)<ext>` com `ext` igual a `Path.suffix`; `n` cresce a partir de 1 ate um nome livre.
- A mesma funcao de sufixo sera reutilizada pelo `organize` (item filepilot-v1-5) quando um arquivo surgir no destino durante a execucao.

### filepilot-v1-4-f3 Guarda de pasta e plano sem efeitos
Linhas da SPEC: .abt/SPEC.md L276-291
Arquivos:
- filepilot/services/planner.py (novo)
- tests/services/test_planner_guard.py (novo)
Criterios de aceite:
- Destino cujo `resolve()` fica fora da pasta escolhida levanta `DESTINO_FORA_DA_PASTA` e nenhum plano e devolvido.
- A arvore da pasta e identica antes e depois de `build_plan` (nenhuma pasta criada, nenhum arquivo movido) e o banco nao e tocado.
- `Plan.is_empty` e verdadeiro quando nenhum arquivo tem categoria ou regra.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_planner_guard.py -> exit 0
- grep deve casar: is_relative_to em filepilot/services/planner.py
- grep nao deve casar: mkdir em filepilot/services/planner.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Guarda: `destination_path.resolve().is_relative_to(folder.resolve())` para toda operacao (SPEC 6.2, penultimo item).
- Simulacao e organizacao usam esta mesma funcao (decisao de design em 15.2, L659-669).

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
