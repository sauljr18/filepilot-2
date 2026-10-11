# filepilot-mypy-1 - Checagem de tipos com mypy no pyproject
Epico: filepilot-mypy | Ordem: 1 | Pontos: 2 | Depende de: filepilot-v1-1

## Objetivo
Fixar mypy==2.4.0 entre as dependencias de desenvolvimento do pyproject.toml e deixar o comando python -m mypy --platform win32 filepilot saindo com codigo 0 sobre o codigo existente.

## Contexto herdado
-

## Features

### filepilot-mypy-1-f1 mypy 2.4.0 fixado e comando de checagem para Windows
Linhas da SPEC: .abt/SPEC.md L758-773
Arquivos:
- .abt/SPEC.md L758-773
- pyproject.toml (novo)
Criterios de aceite:
- O pyproject.toml traz a linha mypy==2.4.0 entre as dependencias de desenvolvimento, ao lado de pytest==9.1.1, pytest-qt==4.5.0 e pyinstaller==6.22.3 (grep mypy==2.4.0 pyproject.toml encontra uma linha).
- Depois de instalar as dependencias de desenvolvimento, python -m mypy --version imprime uma linha que comeca por mypy 2.4.0.
- python -m mypy --platform win32 filepilot, na raiz do repositorio, sai com codigo 0 e imprime uma linha que comeca por Success: no issues found.
- Nenhum arquivo de configuracao do mypy foi criado e o pyproject.toml e o unico arquivo alterado por este item (git status).
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- grep deve casar: mypy==2.4.0 em pyproject.toml
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em pyproject.toml
- dependencias: mypy em pyproject.toml
Dicas:
- O pyproject.toml ja existe quando este item e assumido: filepilot-v1-1 o cria (filepilot-v1-1-f1, em .abt/items/filepilot-v1/filepilot-v1-1.md). Este item so altera a linha do mypy; o "(novo)" de Arquivos so indica que o arquivo nao existe hoje, antes de filepilot-v1-1.
- filepilot-v1-1 ja declara mypy sem versao nas dependencias de desenvolvimento (filepilot-v1-1.md, linhas 31 e 33) e roda mypy . --no-error-summary no typecheck e no workflow do GitHub Actions (linhas 24 e 90). Este item NAO edita o detalhe de filepilot-v1-1 nem o workflow: so troca a linha sem versao por mypy==2.4.0 e adota o comando de 17.2 para a checagem.
- A opcao --platform win32 faz o mypy analisar o codigo como Windows: sem ela, ctypes.windll (6.1) e st_file_attributes (6.1 e 6.7) sao apontados como erro fora do Windows (SPEC 17.2 e 17.3).
- Confirme que mypy 2.4.0 existe no PyPI antes de gravar a versao (pip index versions mypy).
- Nao crie arquivo de configuracao do mypy nem etapa de mypy no GitHub Actions (escopo negativo de 17.2); nao anote tipos no codigo existente (17.1).

## Gates do item
- python -m mypy --platform win32 filepilot -> exit 0
- pytest -> exit 0
- awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-mypy/*.md -> saida vazia
