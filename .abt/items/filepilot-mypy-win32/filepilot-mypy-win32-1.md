# filepilot-mypy-win32-1 - Comando unico de mypy nos itens filepilot-v1-2 a 13
Epico: filepilot-mypy-win32 | Ordem: 1 | Pontos: 3 | Depende de: -

## Objetivo
Trocar, nos detalhes de item filepilot-v1-2 a filepilot-v1-13 (.abt/items/filepilot-v1/), o comando mypy . --no-error-summary pelo comando unico python -m mypy --platform win32 filepilot (SPEC 19.2), de modo que nenhum desses itens seja validado pela forma antiga.

## Contexto herdado
-

## Features

### filepilot-mypy-win32-1-f1 Comando unico nas linhas de Verificacao e nos Gates dos itens filepilot-v1-2 a 13
Linhas da SPEC: .abt/SPEC.md L843-851
Arquivos:
- .abt/items/filepilot-v1/filepilot-v1-2.md L47-78
- .abt/items/filepilot-v1/filepilot-v1-3.md L23-70
- .abt/items/filepilot-v1/filepilot-v1-13.md L22-50
Criterios de aceite:
- Em cada arquivo de filepilot-v1-2.md a filepilot-v1-13.md, toda linha "- typecheck: mypy . --no-error-summary -> exit 0" vira "- typecheck: python -m mypy --platform win32 filepilot -> exit 0" (a soma de linhas com a forma nova nesses 12 arquivos e 46).
- grep -rn "mypy . --no-error-summary" .abt/items/filepilot-v1 --exclude=filepilot-v1-1.md nao encontra nenhuma linha.
- filepilot-v1-1.md nao e alterado (git diff --name-only nao o lista).
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- grep deve casar: typecheck: python -m mypy --platform win32 filepilot -> exit 0 em .abt/items/filepilot-v1/filepilot-v1-2.md
- grep deve casar: typecheck: python -m mypy --platform win32 filepilot -> exit 0 em .abt/items/filepilot-v1/filepilot-v1-13.md
- grep nao deve casar: mypy . --no-error-summary em .abt/items/filepilot-v1/filepilot-v1-3.md
- grep nao deve casar: mypy . --no-error-summary em .abt/items/filepilot-v1/filepilot-v1-12.md
Dicas:
- Os 46 gates estao em: filepilot-v1-2 (3 linhas), filepilot-v1-3 a filepilot-v1-12 (4 linhas cada) e filepilot-v1-13 (3 linhas). Troque so o comando e mantenha o "-> exit 0".
- filepilot-v1-1.md ja foi entregue (commit 940e833) e fica como registro historico: nao o edite (SPEC 19.2, excecao unica, e 19.4).
- O ultimo grep acima e o de exclusao completa: grep -rn "mypy . --no-error-summary" .abt/items/filepilot-v1 --exclude=filepilot-v1-1.md deve sair vazio (status 1).
- Nao altere nenhuma outra linha desses arquivos (Depende de, features, Linhas da SPEC): so o comando de mypy.

### filepilot-mypy-win32-1-f2 Comando unico no texto descritivo de filepilot-v1-2
Linhas da SPEC: .abt/SPEC.md L843-851
Arquivos:
- .abt/items/filepilot-v1/filepilot-v1-2.md L18-30
Criterios de aceite:
- A linha 18 de filepilot-v1-2.md descreve o workflow como rodando "pytest" e "python -m mypy --platform win32 filepilot" no windows-latest.
- A linha 30 de filepilot-v1-2.md diz que todo codigo novo passa em "python -m mypy --platform win32 filepilot" (configuracao padrao, sem arquivo de configuracao proprio).
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- grep deve casar: roda `pytest` e `python -m mypy --platform win32 filepilot` no windows-latest em .abt/items/filepilot-v1/filepilot-v1-2.md
- grep deve casar: passa em `python -m mypy --platform win32 filepilot` (configuracao padrao em .abt/items/filepilot-v1/filepilot-v1-2.md
- grep nao deve casar: mypy . --no-error-summary em .abt/items/filepilot-v1/filepilot-v1-2.md
Dicas:
- Mantenha o resto das duas linhas como esta: a linha 18 comeca por "- .github/workflows/tests.yml - CI - roda" e a linha 30 por "- Todo codigo novo passa em".
- A linha 11 do mesmo arquivo cita mypy==2.4.0 no manifesto: nao a altere.

## Gates do item
- python -m mypy --platform win32 filepilot -> exit 0
- pytest -> exit 0
- grep -rn "mypy . --no-error-summary" .abt/items/filepilot-v1 --exclude=filepilot-v1-1.md -> saida vazia
- awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-mypy-win32/*.md -> saida vazia
