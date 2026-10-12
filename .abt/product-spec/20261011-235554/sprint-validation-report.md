# Relatorio de Prontidao para o Fatiamento: Comando unico de checagem de tipos com mypy --platform win32

**Data:** 2026-10-11
**Modo:** so SPEC + itens

## 1. Cobertura de Requisitos

Escopo de `discovery-notes.md` (modo so SPEC + itens: o escopo e a fonte, sem `prd.md`), conferido contra a secao 19 de `.abt/SPEC.md` e contra o codigo real (`.github/workflows/tests.yml:21` e `:22`, `pyproject.toml:19`, `.abt/items/filepilot-v1/`).

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| Comando unico `python -m mypy --platform win32 filepilot` em todos os itens (Verificacao e Gates) | 19.2 (regras) e 19.4 (itens `filepilot-v1-2` a `filepilot-v1-13`, excecao de `filepilot-v1-1`) | coberto |
| O mesmo comando no passo de checagem de tipos do GitHub Actions | 19.3 (`tests.yml`, linhas 21 e 22) | coberto |
| SPEC 17.2 reflete que o mypy roda no GitHub Actions | 19.2 (substitui a frase de 17.2) | coberto |
| Itens novos para o workflow e para os itens existentes, sem tocar o codigo do produto | 19.3, 19.4 e 19.1 (fora de escopo) | coberto |
| `filepilot-mypy-1` registrado como atendido e encerrado sem implementar | 19.4 | coberto |
| Saida `Success: no issues found` e codigo 0 no Linux e no runner windows-latest | 19.2 e 19.3 | coberto |
| Decisao: tests/ fora da checagem de tipos | 19.2 e 19.6 (`[DECISAO: aprovada no enriquecimento; ...]`) | coberto (decisao registrada, nao e lacuna) |

**Lacunas:** 0. Nenhum requisito `parcial`, `ausente` ou `CORTADO`.

## 2. Mapa de Dependencias

| Parte | Depende de |
|---|---|
| A. Passo de checagem de tipos do workflow (19.3) | `filepilot-v1-1` (entregue, status `pronto`, cria o `tests.yml`) |
| B. Comando unico nos detalhes de item `filepilot-v1-2` a `filepilot-v1-13` (19.4) | nada novo; edita arquivos de `.abt/items/filepilot-v1/` |
| Registro de `filepilot-mypy-1` como atendido (19.4) | nada; e acao da pessoa na fila, sem item novo |

Ordem recomendada: B antes de qualquer item `filepilot-v1-N` (N de 2 a 13) ser assumido, porque o gate desses itens passa a ser o comando unico. A pode andar em paralelo com B (arquivos diferentes). Hoje estao disponiveis para assumir `filepilot-v1-2`, `filepilot-v1-3` e `filepilot-v1-8`.

**Dependencias criticas:** B (os 12 detalhes de item que a fila entrega a quem assumir).

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| A. Passo do workflow | Simples | 1 |
| B. Comando unico nos 12 detalhes de item | Simples | 3 |

Nenhuma parte acima de 8 pontos. B e mecanica (troca textual do mesmo comando em 12 arquivos, cerca de 46 linhas de `typecheck:` mais as linhas 18 e 30 de `filepilot-v1-2.md`), mas o numero de arquivos pede um item proprio, com checagem por grep.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| `filepilot-v1-2`, `filepilot-v1-3` ou `filepilot-v1-8` serem assumidos antes de B: o gate antigo (`mypy . --no-error-summary`) ficaria no detalhe e o item seria validado pela forma antiga | Medio | Fatiar B primeiro e orientar a pessoa a assumir B antes de qualquer filepilot-v1-N; B nao depende de nenhum item novo |
| `filepilot-mypy-1` continua `na_fila` e disponivel (`available: true`) ate a pessoa encerra-lo; alguem pode assumi-lo e reimplementar o que `pyproject.toml:19` ja tem | Medio | Esta especificacao nao cria nem fecha item para ele; a pessoa o encerra na fila antes de outras pessoas assumirem itens |
| O mypy nao esta instalado no ambiente desta execucao: o comando unico nunca foi executado sobre `filepilot/` | Baixo | O item A traz como gate o proprio comando unico e o workflow `windows-latest` o roda no CI |
| Sem `tests/` na checagem (decisao aprovada), erros de tipo em `tests/` deixam de aparecer | Baixo | Decisao registrada em 19.2; nenhuma acao |

Nenhum risco `Bloqueante`.

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro cabe em 2 itens de ate 8 pontos (A: 1 ponto; B: 3 pontos), sem dependencia entre eles e sem nenhuma dependencia nova de infraestrutura.

## 6. Dados para o fatiamento

Epicos ja usados no projeto (`abt epic list --ids --json`): `filepilot-mypy`, `filepilot-v1`.

Itens ja usados (`abt queue list --json`, 14 itens):

| item_id | epic_id | status |
|---|---|---|
| filepilot-mypy-1 | filepilot-mypy | na_fila |
| filepilot-v1-1 | filepilot-v1 | pronto |
| filepilot-v1-2 | filepilot-v1 | na_fila |
| filepilot-v1-3 | filepilot-v1 | na_fila |
| filepilot-v1-4 | filepilot-v1 | na_fila |
| filepilot-v1-5 | filepilot-v1 | na_fila |
| filepilot-v1-6 | filepilot-v1 | na_fila |
| filepilot-v1-7 | filepilot-v1 | na_fila |
| filepilot-v1-8 | filepilot-v1 | na_fila |
| filepilot-v1-9 | filepilot-v1 | na_fila |
| filepilot-v1-10 | filepilot-v1 | na_fila |
| filepilot-v1-11 | filepilot-v1 | na_fila |
| filepilot-v1-12 | filepilot-v1 | na_fila |
| filepilot-v1-13 | filepilot-v1 | na_fila |

Dependencias com itens existentes: A depende de `filepilot-v1-1` (entregue). B edita os detalhes de `filepilot-v1-2` a `filepilot-v1-13` e nao altera o `depends_on` de nenhum.

Pronto para fatiamento: SIM
