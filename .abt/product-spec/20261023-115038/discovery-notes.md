# Discovery Notes: Opcao --version na linha de comando

**Data:** 2026-10-23
**Condutora:** Dani Descoberta

Modo: so SPEC + itens

## Contexto e Problema

- **Problema central:** `python -m filepilot` sempre abre a janela; não há como consultar a versão instalada pela linha de comando.
- **Situacao atual (sem o produto):** `filepilot/__main__.py` cria a `QApplication` e abre a janela principal em toda execução, sem ler argumentos; a versão (`__version__` em `filepilot/__init__.py`, hoje `0.1.0`) só é visível lendo o código.
- **Por que agora:** pedido direto da pessoa, registrado como escopo (modo so SPEC + itens, sem entrevista).

## Personas

### Ana (Usuaria domestica)

- **Papel no produto:** usuária principal do FilePilot (persona da SPEC, seção 1).
- **Objetivo principal:** conferir a versão do FilePilot instalada.
- **Frustracao atual:** para saber a versão, precisa abrir o código; o comando sempre abre a janela.

### Carlos (Usuario que cria regras)

- **Papel no produto:** usuário secundário (persona da SPEC, seção 1); junto com quem mantém o projeto, confere a versão no build.
- **Objetivo principal:** confirmar pela linha de comando qual versão está rodando.
- **Frustracao atual:** não há saída de versão sem abrir a interface.

## Funcionalidades Core (v1)

1. Exibir a versão: pessoa roda `python -m filepilot --version` e vê o valor de `__version__` de `filepilot/__init__.py` na saída padrão.
2. Sair sem interface: o comando `python -m filepilot --version` termina com código de saída 0 e não abre a interface gráfica.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Linguagem | Python 3.12 | stack inalterada: a da SPEC, seção 4, e do `pyproject.toml` |
| Interface grafica | PySide6 6.12.0 | stack inalterada: a da SPEC, seção 4; não é aberta no `--version` |

### Integracoes Externas

Nenhuma: a mudança não envolve serviço externo.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- `python -m filepilot --version` imprime o `__version__` de `filepilot/__init__.py` na saída padrão.
- Esse comando sai com código 0, sem abrir a interface gráfica.

### Fora do Escopo (v1)

- Outros argumentos de linha de comando (como `-V` e `--help`).
- Mudar o valor ou a fonte da versão.
- A versão não aparece na janela do aplicativo.
- Sem argumento, o aplicativo abre como hoje (comportamento atual inalterado).

## Metricas de Sucesso

- Versao na linha de comando: `python -m filepilot --version` imprime o `__version__` e sai com código 0, sem janela (baseline atual: o comando abre a janela).

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
