# filepilot-v1-6 - Verificacoes de destino e textos de falha
Epico: filepilot-v1 | Ordem: 6 | Pontos: 3 | Depende de: filepilot-v1-5

## Objetivo
A organizacao recusa caminho de destino acima de 259 caracteres e subpasta de destino que e atalho, e grava os textos amigaveis de falha por arquivo, sem nenhuma chamada proibida nos servicos.

## Contexto herdado
-

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
