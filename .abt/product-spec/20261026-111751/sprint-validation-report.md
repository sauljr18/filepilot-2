# Relatorio de Prontidao para o Fatiamento: zz-74e-descartavel - arquivo de prova do smoke 74e

**Data:** 2026-10-26
**Modo:** so SPEC + itens

## 1. Cobertura de Requisitos

| Requisito | Elemento da SPEC | Status |
|-----------|------------------|--------|
| Item `zz-74e-descartavel` cria `rascunho/74e-prova.md` com a linha `prova do smoke 74e` | 60.2 (caminho, conteudo de 19 bytes, verificacao pelo arquivo versionado) | coberto |
| Fora de escopo: codigo de qualquer tipo | 60.1 | coberto |
| Fora de escopo: testes | 60.1 | coberto |
| Fora de escopo: mudanca em qualquer outro arquivo | 60.1; 60.2 (verificacao pelo diff) | parcial |
| Metrica: solicitacao de mesclagem do item aberta com so rascunho/74e-prova.md no diff | 60.2 (verificacao pelo diff) | parcial |
| Metrica: conteudo do arquivo e exatamente uma linha | 60.2 (`git show HEAD:` com `cmp`) | coberto |

**Lacunas:** 0 ausentes; 2 parciais, ambas pela mesma causa: o ERR-001 do relatorio do Rafael (Round 1), aprovado pela pessoa como pendencia registrada. Todo PR de item deste projeto leva tambem `.abt/reviews/<item_id>.md`, entao "so rascunho/74e-prova.md no diff" nao se cumpre como esta escrito. Correcao recomendada: no detalhe do item, tratar o `.abt/reviews/zz-74e-descartavel.md` do fluxo do abt como a unica outra mudanca aceita (Opcao A do ERR-001), sem mudar a SPEC aprovada.

## 2. Mapa de Dependencias

| Parte | Depende de |
|-------|------------|
| 60.2 arquivo `rascunho/74e-prova.md` | nenhuma (nenhum codigo, dado nem item existente) |

**Dependencias criticas:** nenhuma. Nenhum dos 34 itens existentes (todos `pronto`) toca `rascunho/`.

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|-------|--------------|--------|
| 60.2 arquivo `rascunho/74e-prova.md` | Simples | 1 |

## 4. Riscos

| Risco | Severidade | Acao |
|-------|------------|------|
| ERR-001 pendente: o criterio "so rascunho/74e-prova.md no diff" (60.2) falha porque o PR do item leva tambem `.abt/reviews/zz-74e-descartavel.md` | Medio | No detalhe do item, aceitar so esse relatorio do abt como mudanca extra (Opcao A do ERR-001) e registrar isso como decisao da pessoa pendente |
| Copia de trabalho com CRLF no Windows (`core.autocrlf=true`, sem `.gitattributes`) | Baixo | Ja tratado em 60.2: a verificacao usa o arquivo versionado |

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro e uma parte Simples de 1 ponto, sem dependencias; 1 item estimado.

## 6. Dados para o fatiamento

- Epicos ja usados no projeto (`abt epic list --ids --json`): filepilot-fix, filepilot-fix2, filepilot-fix3, filepilot-help, filepilot-mypy, filepilot-mypy-win32, filepilot-opcao-v, filepilot-v1, filepilot-version.
- Itens ja usados (`abt queue list --json`, 34, todos `pronto`): filepilot-fix-1 a -4, filepilot-fix2-1 a -4, filepilot-fix3-1 a -7, filepilot-help-1, filepilot-mypy-1, filepilot-mypy-win32-1 e -2, filepilot-opcao-v-1, filepilot-v1-1 a -13, filepilot-version-1.
- O id pedido pela pessoa, `zz-74e-descartavel`, nao colide com nenhum epico nem item existente.
- Dependencias com itens existentes: nenhuma.

Pronto para fatiamento: SIM
