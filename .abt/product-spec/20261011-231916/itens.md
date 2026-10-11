# Itens - Checagem de tipos com mypy

Epico: filepilot-mypy
Titulo do epico: Checagem de tipos com mypy

**Data:** 2026-10-11
**Modo:** so SPEC + itens

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-mypy-1 | Checagem de tipos com mypy no pyproject | 2 | filepilot-v1-1 | Declarar mypy==2.4.0 entre as dependencias de desenvolvimento do pyproject.toml e deixar o comando python -m mypy --platform win32 filepilot saindo com codigo 0 sobre o codigo existente |

## 2. Criterios de aceite

- filepilot-mypy-1:
    - O pyproject.toml traz a linha mypy==2.4.0 entre as dependencias de desenvolvimento, ao lado de pytest==9.1.1, pytest-qt==4.5.0 e pyinstaller==6.22.3 (conferido com grep mypy==2.4.0 pyproject.toml, uma linha encontrada).
    - Depois de instalar as dependencias de desenvolvimento, python -m mypy --version imprime uma linha que comeca por mypy 2.4.0.
    - python -m mypy --platform win32 filepilot, na raiz do repositorio, sai com codigo 0 e imprime uma linha que comeca por Success: no issues found.
    - Nenhum arquivo de configuracao do mypy e nenhuma etapa de mypy no fluxo do GitHub Actions foram criados (git status lista so o pyproject.toml como arquivo alterado por este item).

## 3. Mapa para a SPEC

- filepilot-mypy-1: 17.2 Ferramentas de desenvolvimento: mypy; 4 Stack e dependencias (a linha nova de 17.2 complementa a tabela e o ultimo paragrafo); 17.3 Plataforma alvo (motivo da opcao --platform win32).

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| O pyproject.toml so existe depois de filepilot-v1-1, que esta na fila: sem a dependencia, o item de mypy poderia ser assumido antes do manifesto existir | Medio | filepilot-mypy-1 declara Depende de: filepilot-v1-1 |
| O detalhe e os gates dos 13 itens existentes nao citam mypy, entao a checagem nao entra neles; o item novo verifica so o codigo que existir quando for implementado | Baixo | Nao editar os 13 itens (fora de escopo, 17.1); o gate do item novo e o comando de 17.2 sobre o codigo do momento |
| Codigo dos itens seguintes (filepilot-v1-2 em diante) pode ser mesclado sem checagem de tipos, ate o item de mypy ser implementado | Baixo | Aceito: 17.2 define a checagem como comando manual de desenvolvimento, sem etapa no GitHub Actions |
| A versao mypy==2.4.0 e a mais recente do PyPI em 2026-10-11 ([DECISAO] do Gabriel); uma versao nova pode mudar o resultado da checagem | Baixo | A versao fica fixada no pyproject.toml; trocar e decisao de outra especificacao |

Pendencias da subsecao Pendencias para decisao da secao 17: nenhuma aberta.

## 5. Cobertura

| Item do escopo | Item que cobre |
|---|---|
| mypy faz parte das ferramentas de desenvolvimento, junto com pytest | filepilot-mypy-1 |
| Plataforma alvo: Windows 10 e 11 em 64 bits, como decisao | Sem item: decisao documental coberta pela SPEC 17.3 (nao exige codigo; 17.3 nao cria teste e nao muda requires-python). A opcao --platform win32 do comando de filepilot-mypy-1 aplica essa decisao na checagem. |
