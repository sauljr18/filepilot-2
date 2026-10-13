# Discovery Notes: Correcao dos defeitos remanescentes na main do FilePilot

**Data:** 2026-10-13
**Condutora:** Dani Descoberta

Modo: so SPEC + itens

## Contexto e Problema

- **Problema central:** a main do FilePilot ainda tem 7 defeitos: (1) na aba Historico, uma organizacao com data invalida (ano 0001) derruba o carregamento da pagina com erro interno; (2) o desfazer quebra com erro interno quando um caminho tem laco de atalho, o mesmo defeito ja corrigido na leitura e no planejamento; (3) a recusa da pasta com laco de atalho no planejamento so esta provada no Linux: no Windows o teste e pulado e o laco real nao e detectado; (4) na aba Organizar, a barra de progresso continua visivel depois de desfazer; (5) ha testes que travam em vez de falhar quando o comportamento esta errado (instancia unica e botao de desfazer); (6) `mypy .` da tres erros nos testes; (7) o repositorio nao tem `.gitignore`.
- **Situacao atual (sem o produto):** os defeitos permanecem na main; a pagina Historico falha com datas invalidas, o desfazer falha com laco de atalho, a recusa de laco no Windows nao e provada, a barra de progresso fica visivel apos desfazer, a suite pode travar e a checagem de tipos nao passa nos testes.
- **Por que agora:** a pessoa quer fechar os defeitos conhecidos da main, com um item de correcao com teste para cada um, sem mudar mais nada.

## Personas

### Ana (Usuaria domestica)

- **Papel no produto:** usuaria domestica que organiza a pasta Downloads, simula, desfaz a ultima organizacao e consulta o historico (SPEC 8.1, 8.2 e 8.4).
- **Objetivo principal:** manter a pasta em ordem com poucos cliques e sem medo de perder arquivo (SPEC 1).
- **Frustracao atual:** o Historico pode falhar com erro interno, o desfazer pode falhar com laco de atalho e a barra de progresso fica visivel depois de desfazer.

### Carlos (Criador de regras)

- **Papel no produto:** cria regras personalizadas para o proprio jeito de guardar arquivos (SPEC 1 e 8.3).
- **Objetivo principal:** organizar os arquivos pelas proprias regras, com a mesma confianca da simulacao e do desfazer.
- **Frustracao atual:** a organizacao com regras depende do mesmo planejamento e do mesmo desfazer, que ainda tem defeitos com laco de atalho.

## Funcionalidades Core (v1)

1. Historico com data invalida: o Historico carrega a pagina mesmo quando uma organizacao tem data invalida (ano 0001), sem erro interno.
2. Desfazer com laco de atalho: o desfazer nao falha com erro interno quando um caminho tem laco de atalho, como ja tratado na leitura e no planejamento.
3. Recusa de laco no Windows: a recusa da pasta com laco de atalho no planejamento e provada tambem no Windows, com o laco real detectado e sem teste pulado.
4. Barra de progresso: a aba Organizar esconde a barra de progresso depois de desfazer.
5. Testes que travam: os testes de instancia unica e do botao de desfazer falham em vez de travar quando o comportamento esta errado.
6. Checagem de tipos: `mypy .` passa sem erros nos testes.
7. Repositorio: o repositorio tem `.gitignore`.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Linguagem | Python 3.12+ | a do manifesto `pyproject.toml`, inalterada |
| Interface | PySide6 | a do manifesto, inalterada |
| Testes | pytest e pytest-qt | os do manifesto, inalterados |
| Tipos | mypy | o do manifesto, inalterado |

### Integracoes Externas

Nenhuma integracao externa pedida; os modos delta nao atualizam a `stack-decision.md`.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- Os 7 defeitos acima, com um item de correcao com teste para cada um.

### Fora do Escopo (v1)

- Qualquer mudanca alem dos 7 defeitos.
- Novas funcionalidades.
- Alterar comportamento fora das correcoes.
- Atualizar a `stack-decision.md`.

## Metricas de Sucesso

- Cobertura por defeito: cada defeito com teste que falha antes da correcao e passa depois (baseline atual: defeito presente na main).
- Checagem de tipos: `mypy .` sem erros nos testes (baseline atual: tres erros).
- Demais metricas: nao definido

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
