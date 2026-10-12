# Itens - Comando unico de mypy com --platform win32
Epico: filepilot-mypy-win32
Titulo do epico: Comando unico de mypy com --platform win32
**Data:** 2026-10-11
**Modo:** so SPEC + itens

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-mypy-win32-1 | Comando unico de mypy nos itens filepilot-v1-2 a 13 | 3 | - | Os detalhes de item filepilot-v1-2 a filepilot-v1-13 usam o comando unico de 19.2 no lugar de mypy . --no-error-summary |
| 2 | filepilot-mypy-win32-2 | Passo de mypy do workflow com comando unico | 1 | - | O passo Checagem de tipos de .github/workflows/tests.yml roda o comando unico de 19.2 |

## 2. Criterios de aceite

- filepilot-mypy-win32-1:
    - grep -rn "mypy . --no-error-summary" .abt/items/filepilot-v1 --exclude=filepilot-v1-1.md nao encontra nenhuma linha.
    - grep -rc "typecheck: python -m mypy --platform win32 filepilot -> exit 0" nos arquivos filepilot-v1-2.md a filepilot-v1-13.md soma 46.
    - Nas linhas 18 e 30 de filepilot-v1-2.md o comando descrito e python -m mypy --platform win32 filepilot.
    - git diff --name-only lista somente arquivos de .abt/items/filepilot-v1 entre filepilot-v1-2.md e filepilot-v1-13.md.
- filepilot-mypy-win32-2:
    - grep -n "python -m mypy --platform win32 filepilot" .github/workflows/tests.yml encontra uma linha.
    - grep -n "mypy . --no-error-summary" .github/workflows/tests.yml nao encontra nenhuma linha.
    - O passo Checagem de tipos continua depois do passo Testes e o job continua em windows-latest com Python 3.12.

## 3. Mapa para a SPEC

- filepilot-mypy-win32-1: 19.2 Comando unico; 19.4 Itens existentes e o item de mypy.
- filepilot-mypy-win32-2: 19.2 Comando unico; 19.3 Fluxo do GitHub Actions.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| filepilot-v1-2, filepilot-v1-3 ou filepilot-v1-8 serem assumidos antes de filepilot-mypy-win32-1 e validados pela forma antiga do comando | Medio | Assumir filepilot-mypy-win32-1 antes de qualquer filepilot-v1-N; ele vem primeiro na ordem |
| filepilot-mypy-1 continua na_fila e disponivel ate a pessoa encerra-lo; alguem pode reimplementar o que pyproject.toml:19 ja tem | Medio | Encerrar filepilot-mypy-1 na fila (acao da pessoa, fora destes itens) |
| O mypy nao foi executado sobre filepilot/ no ambiente desta especificacao | Baixo | O workflow windows-latest roda o comando unico no CI do item filepilot-mypy-win32-2 |
| A pasta tests/ deixa de ter checagem de tipos (decisao aprovada em 19.2) | Baixo | Nenhuma; decisao registrada |

## 5. Cobertura

| Item do escopo | Item que cobre |
|---|---|
| Comando unico em todos os itens (Verificacao e Gates) | filepilot-mypy-win32-1 |
| O mesmo comando no passo de checagem de tipos do GitHub Actions | filepilot-mypy-win32-2 |
| SPEC 17.2 reflete que o mypy roda no GitHub Actions | ja entregue na secao 19 da SPEC desta execucao |
| Itens novos para o workflow e para os itens existentes | filepilot-mypy-win32-1 e filepilot-mypy-win32-2 |
| filepilot-mypy-1 registrado como atendido e encerrado sem implementar | sem item novo: registrado em 19.4; encerramento feito pela pessoa na fila |
| Saida Success: no issues found e codigo 0 no Linux e no runner windows-latest | filepilot-mypy-win32-1 e filepilot-mypy-win32-2 |
