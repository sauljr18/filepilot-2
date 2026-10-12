# Discovery Notes: Correcao de quatro defeitos do FilePilot

**Data:** 2026-10-12
**Condutora:** Dani Descoberta

Modo: so SPEC + itens

## Contexto e Problema

- **Problema central:** quatro defeitos ja presentes na main do FilePilot: (1) ler uma pasta com laco de atalho (symlink apontando para cima) quebra com erro interno em vez de informar que a pasta e invalida; (2) com a variavel SystemRoot vazia, a pasta atual passa a ser tratada como protegida; (3) a ordem da lista de arquivos muda de uma execucao para outra quando dois nomes so diferem por maiuscula e minuscula; (4) se o banco fica indisponivel no meio de uma organizacao, ela fica presa como em andamento, sem desfazer o que foi aberto no banco.
- **Situacao atual (sem o produto):** os defeitos estao na main e nao tem teste que os cubra; a pessoa ve erro interno, pasta bloqueada sem motivo, lista em ordem instavel ou organizacao presa.
- **Por que agora:** a pessoa quer corrigir os defeitos, um item de correcao com teste para cada, antes de seguir com a interface.

## Personas

### Ana (Usuaria domestica)

- **Papel no produto:** usuaria domestica que organiza a pasta Downloads (persona ja registrada na SPEC, secao 1).
- **Objetivo principal:** manter a pasta em ordem com poucos cliques e sem medo de perder arquivo.
- **Frustracao atual:** erro interno ao escolher pasta com atalho em laco, organizacao presa como em andamento e lista que muda de ordem sem motivo.

### Carlos (Criador de regras)

- **Papel no produto:** pessoa que cria regras personalizadas para o proprio jeito de guardar arquivos (persona ja registrada na SPEC, secao 1).
- **Objetivo principal:** ter regras aplicadas de forma previsivel sobre os arquivos da pasta.
- **Frustracao atual:** a ordem da lista de arquivos varia entre execucoes quando nomes diferem so por maiuscula e minuscula, o que torna o resultado imprevisivel.

## Funcionalidades Core (v1)

1. Pasta invalida por laco de atalho: o sistema informa que a pasta e invalida, em vez de falhar com erro interno, quando a leitura encontra um symlink apontando para cima.
2. Pasta atual sem falso bloqueio: o sistema trata a pasta atual como protegida apenas quando isso e verdade, mesmo com a variavel SystemRoot vazia.
3. Ordem estavel da lista: o sistema entrega a lista de arquivos sempre na mesma ordem em qualquer execucao, inclusive quando dois nomes so diferem por maiuscula e minuscula.
4. Organizacao encerrada na falha do banco: o sistema desfaz o que foi aberto no banco e encerra a organizacao, sem deixa-la como em andamento, quando o banco fica indisponivel no meio dela.
5. Teste por defeito: cada correcao e entregue em um item proprio, com ao menos um teste automatizado que falha antes e passa depois da correcao.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Stack inalterada | A do manifesto `pyproject.toml` e da secao 4 da SPEC | Correcao de defeitos, sem mudanca de stack |
| Testes | pytest (secao 4 da SPEC) | E o framework de testes ja usado no projeto |

### Integracoes Externas

- Nenhuma integracao externa nova: as correcoes ficam em `filepilot.services` e `filepilot.db`, como na SPEC.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- Correcao dos quatro defeitos descritos em Contexto e Problema, um item de correcao para cada.
- Ao menos um teste automatizado por defeito.
- Suite pytest e mypy sem regressao ao fim.

### Fora do Escopo (v1)

- A interface: fica para depois, conforme o pedido da pessoa.
- Novas funcionalidades.
- Mudanca de stack.
- Correcao de defeitos que nao estao na lista de quatro.

## Metricas de Sucesso

- Itens de correcao entregues: 4 itens, um por defeito, ate o fim desta especificacao (baseline atual: 0 itens e 0 testes para estes defeitos).
- Testes por defeito: ao menos 1 teste automatizado por item, que falha antes e passa depois da correcao (baseline atual: 0).
- Regressao: 0 testes pytest e 0 erros de mypy novos ao fim de cada item (baseline atual: suite e mypy da main).

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
