# Relatorio do Detalhe dos Itens: filepilot-mypy-win32

**Data:** 2026-10-11
**Modo:** so SPEC + itens
**Stack:** Python (comandos de SPEC 19.2, que prevalece sobre a tabela da stack; manifesto pyproject.toml)

## 1. Secao da SPEC

Secao nova: 19. Comando unico de checagem de tipos com mypy [DELTA 2026-10-11], linhas 805 a 867 de `.abt/SPEC.md` (total de 867 linhas). Subsecoes de conteudo mapeadas: 19.1 L807-814, 19.2 L815-834, 19.3 L835-842, 19.4 L843-851. `19.5 Pendencias para decisao` (L852) e `19.6 Traceability Matrix` (L856) nunca sao alvo de `Linhas da SPEC`.

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-mypy-win32-1 | Comando unico de mypy nos itens filepilot-v1-2 a 13 | 3 | - | 2 |
| 2 | filepilot-mypy-win32-2 | Passo de mypy do workflow com comando unico | 1 | - | 1 |

Total: 2 itens, 4 pontos, 3 features.

## 3. Linhas da SPEC por feature

| Feature | Linhas da SPEC | Subsecao |
|---|---|---|
| filepilot-mypy-win32-1-f1 | L843-851 | 19.4 Itens existentes e o item de mypy |
| filepilot-mypy-win32-1-f2 | L843-851 | 19.4 Itens existentes e o item de mypy |
| filepilot-mypy-win32-2-f1 | L835-842 | 19.3 Fluxo do GitHub Actions |

## 4. Checklist mecanico

1. Um detalhe por item, no caminho `.abt/items/filepilot-mypy-win32/<item_id>.md`, com linha 1, cabecalho e as quatro secoes: ok.
2. `Ordem`, `Pontos` e `Depende de` iguais aos do `itens.md` (1, 3, `-` e 2, 1, `-`); pontos de 1 a 8: ok.
3. Toda feature com `Linhas da SPEC`, `Arquivos:`, de 2 a 5 criterios, `Verificacao:` com o typecheck e `Dicas:`: ok.
4. Todo intervalo com 1 <= a <= b <= 867 e no maximo 60 linhas (9, 9 e 8 linhas), dentro de subsecao de conteudo da secao 19, nunca na matriz, na pendencia nem num `## §N`: ok.
5. Ids no formato `^[a-z0-9][a-z0-9-]{1,39}$` e livres (`abt epic list --ids` e `abt queue list --ids` reconferidos: epicos `filepilot-mypy` e `filepilot-v1`; 14 itens, nenhum com o prefixo `filepilot-mypy-win32`); sem dependencias, logo sem ciclo: ok.
6. Nenhum marcador do modelo sobrando (grep dos marcadores com saida vazia): ok.
7. Nenhum `§EPIC-` fora de bloco cercado (awk sobre `.abt/SPEC.md` e `.abt/items/filepilot-mypy-win32/*.md`, saida vazia): ok.

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-mypy-win32/filepilot-mypy-win32-1.md | criado | gravado nesta execucao |
| .abt/items/filepilot-mypy-win32/filepilot-mypy-win32-2.md | criado | gravado nesta execucao |

`.abt/items/` ja tem as pastas `filepilot-mypy` (1 detalhe, `filepilot-mypy-1.md`) e `filepilot-v1` (13 detalhes); a convencao de nomes e `<epic_id>-<n>.md`, seguida aqui. Estrutura `.abt/` conferida por `abt scaffold --check`: `RULES.md`, `WORKFLOW.md` e `SPEC.md` mantidos.

## 6. Pendencias e ajustes

- Fonte do comando de typecheck: a tabela da stack Python do roteiro usa `mypy . --no-error-summary`; os detalhes usam o comando unico de 19.2 (`python -m mypy --platform win32 filepilot`), porque a decisao da SPEC prevalece. `.abt/WORKFLOW.md` nao tem secao de comandos: recomenda-se a pessoa acrescentar ali o comando unico, para os proximos detalhes de item nao voltarem a forma antiga (Hugo nao escreve nesse arquivo).
- Smoke omitido nos dois itens: nao ha servidor nem rota de saude (os itens editam arquivos de texto e um workflow); nenhuma porta foi inventada.
- Risco aberto, fora destes itens: `filepilot-mypy-1` segue `na_fila` e disponivel; encerra-lo e acao da pessoa na fila (SPEC 19.4).
- O mypy nao esta instalado neste ambiente: os gates `python -m mypy --platform win32 filepilot -> exit 0` nao foram executados aqui.
- Ajustes do `itens.md`: nenhum.

Retorno: harness
