# Discovery Notes: zz-74e-descartavel - arquivo de prova do smoke 74e

**Data:** 2026-10-26
**Condutora:** Dani Descoberta

Modo: so SPEC + itens

## Contexto e Problema

- **Problema central:** o smoke 74e precisa de uma especificacao minima e descartavel que percorra o fluxo do abt ate abrir a solicitacao de mesclagem do item, sem mescla-la.
- **Situacao atual (sem o produto):** nao ha item de prova no projeto; o repositorio nao tem a pasta `rascunho/`.
- **Por que agora:** o smoke 74e roda agora e pede um item que nao toque codigo nem testes.

## Personas

### Saul (Admin do abt)

- **Papel no produto:** roda o smoke 74e e conduz a especificacao e o item pelo abt.
- **Objetivo principal:** ver o item chegar a solicitacao de mesclagem aberta, com so o arquivo de prova no diff.
- **Frustracao atual:** um item com codigo ou teste tornaria a prova mais lenta e arriscada do que precisa.

## Funcionalidades Core (v1)

1. Arquivo de prova: o item `zz-74e-descartavel` cria o arquivo `rascunho/74e-prova.md` com uma unica linha, `prova do smoke 74e`.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|--------|------------|--------|
| Todas | inalterada (a do `pyproject.toml` e de `.abt/RULES.md`) | a mudanca e um arquivo Markdown e nao toca codigo |

### Integracoes Externas

Nenhuma integracao externa nova: a mudanca nao chama servico nem API.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- Um unico item, `zz-74e-descartavel`, que cria `rascunho/74e-prova.md` com a linha `prova do smoke 74e`.

### Fora do Escopo (v1)

- Codigo de qualquer tipo.
- Testes.
- Mudanca em qualquer outro arquivo do repositorio.

## Metricas de Sucesso

- Solicitacao de mesclagem do item aberta com so rascunho/74e-prova.md no diff
- Conteudo do arquivo: exatamente uma linha, `prova do smoke 74e`.

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
