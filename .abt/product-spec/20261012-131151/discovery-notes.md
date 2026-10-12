# Discovery Notes: Correcao de quatro defeitos do FilePilot na main

**Data:** 2026-10-12
**Condutora:** Dani Descoberta

Modo: so SPEC + itens

## Contexto e Problema

- **Problema central:** quatro defeitos do FilePilot ja estao na main e precisam ser corrigidos antes de seguir com as proximas telas. (1) Se o banco fica indisponivel no meio de um desfazer, o desfazer nao desfaz o que ja abriu no banco, e um segundo desfazer marca como restaurado um arquivo que continua fora do lugar. (2) Se a leitura da pasta falha com erro do sistema na aba Organizar, a aba fica presa em carregando, com os botoes desabilitados. (3) Quando o programa nao consegue saber se ja existe outra janela aberta (por exemplo, sem permissao na pasta de dados), ele fecha em silencio como se ja estivesse aberto. (4) O planejamento quebra com erro interno numa pasta com laco de atalho, o mesmo defeito que ja foi corrigido na leitura da pasta.
- **Situacao atual (sem a correcao):** Ana e Carlos podem acabar com um arquivo marcado como restaurado que continua fora do lugar, com a aba Organizar travada sem saida, com o programa fechando sem explicacao e com um erro interno ao planejar uma pasta com laco de atalho.
- **Por que agora:** as proximas telas da v1 dependem destas telas e servicos; corrigir antes evita construir em cima dos defeitos.

## Personas

### Ana (Usuaria domestica)

- **Papel no produto:** quer a pasta Downloads em ordem com poucos cliques e sem medo de perder arquivo (persona da secao 1 da SPEC).
- **Objetivo principal:** organizar a pasta e, se precisar, desfazer a ultima organizacao com a certeza de que cada arquivo volta ao lugar.
- **Frustracao atual:** o desfazer pode marcar como restaurado um arquivo que continua fora do lugar, a aba Organizar pode travar em carregando e o programa pode fechar em silencio.

### Carlos (Usuario que cria regras)

- **Papel no produto:** cria regras personalizadas para o proprio jeito de guardar (persona da secao 1 da SPEC).
- **Objetivo principal:** simular e organizar pastas, inclusive pastas com atalhos, com as regras dele.
- **Frustracao atual:** o planejamento quebra com erro interno numa pasta com laco de atalho.

## Funcionalidades Core (v1)

1. Desfazer consistente com banco indisponivel: a pessoa que desfaz a ultima organizacao tem revertido o que ja abriu no banco quando o banco fica indisponivel no meio, e um segundo desfazer nao marca como restaurado um arquivo que continua fora do lugar.
2. Aba Organizar sai de carregando na falha: a pessoa que escolhe uma pasta cuja leitura falha com erro do sistema ve a falha e volta a ter os botoes habilitados, em vez de ficar presa em carregando.
3. Instancia unica sem fechar em silencio: a pessoa que abre o programa sem que ele consiga saber se ja existe outra janela (por exemplo, sem permissao na pasta de dados) recebe um aviso em vez de ver o programa fechar em silencio como se ja estivesse aberto.
4. Planejamento com laco de atalho: a pessoa que simula uma pasta com laco de atalho recebe o mesmo tratamento ja dado na leitura da pasta, em vez de um erro interno.
5. Um item de correcao por defeito, cada um com teste que reproduz o defeito: o time implementa 4 itens independentes, cada um com seu teste.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
| --- | --- | --- |
| Stack | A do projeto (Python 3.12, PySide, SQLite e pytest, conforme `.abt/SPEC.md` secao 4 e `.abt/RULES.md`) | Stack inalterada: a mudanca so corrige defeitos |

### Integracoes Externas

- Nenhuma integracao externa nova: a mudanca fica nas camadas existentes de dominio, servicos, banco e interface.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- Correcao do desfazer com banco indisponivel no meio (defeito 1), com teste.
- Correcao da aba Organizar presa em carregando quando a leitura da pasta falha com erro do sistema (defeito 2), com teste.
- Correcao do fechamento em silencio quando nao e possivel saber se ja existe outra janela aberta (defeito 3), com teste.
- Correcao do erro interno do planejamento em pasta com laco de atalho (defeito 4), com teste.
- Um item de correcao por defeito, 4 itens independentes entre si.

### Fora do Escopo (v1)

- As proximas telas da v1.
- Novas funcionalidades alem das quatro correcoes.
- Refatoracoes que nao sejam necessarias para as correcoes.
- Defeitos que nao sejam os quatro listados.

## Metricas de Sucesso

- Defeitos corrigidos: 4 de 4 corrigidos na main (baseline atual: 0 de 4).
- Testes novos: 4 testes novos, um por defeito, passando e reproduzindo o defeito antes da correcao (baseline atual: 0).
- Regressao: 0 testes existentes quebrados pela mudanca (baseline atual: 0).

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
