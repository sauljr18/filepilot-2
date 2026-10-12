# filepilot-v1-13 - Executavel Windows com PyInstaller e CI
Epico: filepilot-v1 | Ordem: 13 | Pontos: 3 | Depende de: filepilot-v1-10,filepilot-v1-11,filepilot-v1-12

## Objetivo
O workflow gera, no windows-latest, a pasta FilePilot com o executavel em modo onedir e publica o zip como artefato do workflow.

## Contexto herdado
-

## Features

### filepilot-v1-13-f1 Empacotamento com PyInstaller em modo onedir
Linhas da SPEC: .abt/SPEC.md L95-119
Arquivos:
- packaging/filepilot.spec (novo)
- packaging/entry.py (novo)
Criterios de aceite:
- `pyinstaller packaging/filepilot.spec --noconfirm` termina com exit 0 no windows-latest e gera `dist/FilePilot/FilePilot.exe` em modo `--onedir`.
- O ponto de entrada executa o mesmo `main()` de `python -m filepilot` e nao abre console (modo janela).
- A pasta `dist/FilePilot` inclui as bibliotecas do PySide6 como arquivos separados (decisao da stack para a licenca LGPL).
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- parser: python -m py_compile packaging/entry.py -> exit 0
- grep deve casar: FilePilot em packaging/filepilot.spec
- grep nao deve casar: onefile em packaging/filepilot.spec
- dependencias: pyinstaller em pyproject.toml
Dicas:
- Stack: PyInstaller 6.22.3, modo `--onedir`, build no runner Windows (SPEC 4, L95-119, e Decisoes de Design da secao 4).
- Aviso do SmartScreen por falta de assinatura e aceito na v1 (risco D-003 do PRD).
- O aplicativo e desktop e nao tem servidor nem rota de saude, entao nao ha `smoke:` com `curl` neste projeto.

### filepilot-v1-13-f2 Job de build e artefato zip no windows-latest
Linhas da SPEC: .abt/SPEC.md L635-645
Arquivos:
- .github/workflows/build.yml (novo)
Criterios de aceite:
- O job `build` roda no `windows-latest` com Python 3.12, instala `pip install -e .[dev]` e roda `pytest` antes do `pyinstaller`.
- O job inicia `dist/FilePilot/FilePilot.exe` e confirma que o processo continua rodando depois de 5 segundos, sem codigo de saida, e entao o encerra.
- O job publica `FilePilot-windows.zip` com a pasta `dist/FilePilot` como artefato do workflow.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- grep deve casar: windows-latest em .github/workflows/build.yml
- grep deve casar: FilePilot-windows.zip em .github/workflows/build.yml
- grep deve casar: upload-artifact em .github/workflows/build.yml
Dicas:
- Ordem de entrega em 14 (L635-645): empacotamento e CI sao o ultimo passo, depois de tudo funcionar.
- Confirme a versao das acoes do GitHub (checkout, setup-python, upload-artifact) antes de fixa-las.

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
