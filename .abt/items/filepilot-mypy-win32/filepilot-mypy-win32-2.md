# filepilot-mypy-win32-2 - Passo de mypy do workflow com comando unico
Epico: filepilot-mypy-win32 | Ordem: 2 | Pontos: 1 | Depende de: -

## Objetivo
Fazer o passo Checagem de tipos de .github/workflows/tests.yml rodar o comando unico python -m mypy --platform win32 filepilot (SPEC 19.2 e 19.3), no lugar de mypy . --no-error-summary.

## Contexto herdado
-

## Features

### filepilot-mypy-win32-2-f1 Passo Checagem de tipos com o comando unico
Linhas da SPEC: .abt/SPEC.md L835-842
Arquivos:
- .github/workflows/tests.yml L17-22
Criterios de aceite:
- grep -n "python -m mypy --platform win32 filepilot" .github/workflows/tests.yml encontra exatamente uma linha, dentro do passo Checagem de tipos.
- grep -n "mypy . --no-error-summary" .github/workflows/tests.yml nao encontra nenhuma linha.
- O passo Checagem de tipos continua depois do passo Testes, e o job continua em windows-latest com Python 3.12.
- Nenhum job, matriz de sistemas operacionais ou etapa de Linux foi acrescentado ao workflow.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- grep deve casar: python -m mypy --platform win32 filepilot em .github/workflows/tests.yml
- grep nao deve casar: mypy . --no-error-summary em .github/workflows/tests.yml
- grep deve casar: windows-latest em .github/workflows/tests.yml
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em .github/workflows/tests.yml
Dicas:
- Hoje o passo e, nas linhas 21 e 22: "- name: Checagem de tipos" e "run: mypy . --no-error-summary" (.github/workflows/tests.yml:21 e :22). Troque so o valor de run, mantendo a indentacao e o nome do passo.
- O pip install -e .[dev] da linha 18 ja instala mypy==2.4.0 (pyproject.toml:19), entao python -m mypy funciona no runner sem passo novo.
- A opcao --platform win32 faz o mypy analisar como Windows tambem no Linux (SPEC 17.2): o comando e o mesmo nas duas plataformas.
- Nao crie arquivo de configuracao do mypy e nao toque no workflow de build de filepilot-v1-13 (.github/workflows/build.yml e outro arquivo).

## Gates do item
- python -m mypy --platform win32 filepilot -> exit 0
- pytest -> exit 0
- awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-mypy-win32/*.md -> saida vazia
