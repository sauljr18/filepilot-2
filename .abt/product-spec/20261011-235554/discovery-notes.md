# Discovery Notes: Checagem de tipos unica com mypy --platform win32

**Data:** 2026-10-11
**Condutora:** Dani Descoberta

Modo: so SPEC + itens

## Contexto e Problema

- **Problema central:** a checagem de tipos precisa rodar igual no Linux e no Windows, com um unico comando de mypy em todos os itens, sempre com `--platform win32`, inclusive no fluxo do GitHub Actions.
- **Situacao atual (sem o produto):** o workflow `.github/workflows/tests.yml` roda `mypy . --no-error-summary`, sem `--platform win32`; a SPEC 17.2 define o comando `python -m mypy --platform win32 filepilot` mas diz que o mypy NAO entra no GitHub Actions; o pedido registrado em itens existentes mistura os dois comandos.
- **Por que agora:** o item `filepilot-mypy-1` (mudanca anterior) ja foi atendido pelo que foi entregue (`mypy==2.4.0` na linha 19 do `pyproject.toml`, entregue em `filepilot-v1-1`), restando padronizar o comando e o workflow.

## Personas

### Saul (Pessoa que desenvolve o FilePilot)

- **Papel no produto:** desenvolve e mantem o FilePilot, em Linux e em Windows.
- **Objetivo principal:** ter a mesma checagem de tipos, com o mesmo comando e o mesmo resultado, em qualquer das duas plataformas e no GitHub Actions.
- **Frustracao atual:** o comando do workflow difere do comando da SPEC; sem `--platform win32`, o mypy aponta como erro, fora do Windows, o que e valido no Windows (`ctypes.windll`, `st_file_attributes`).

## Funcionalidades Core (v1)

1. Comando unico de mypy: a pessoa que desenvolve roda `python -m mypy --platform win32 filepilot` e obtem o mesmo resultado no Linux e no Windows.
2. Comando unico nos itens: os itens existentes e os novos usam esse mesmo comando nos campos `Verificacao:` e `Gates do item`.
3. Checagem no GitHub Actions: o passo de checagem de tipos do workflow roda esse mesmo comando.
4. SPEC alinhada: a SPEC 17.2 passa a refletir que o mypy roda no fluxo do GitHub Actions, substituindo o escopo negativo sobre o Actions.
5. Item `filepilot-mypy-1` registrado como ja atendido: encerrado sem implementar, e esta especificacao nao cria item para ele.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Checagem de tipos | mypy 2.4.0 | ja fixado no `pyproject.toml`; stack inalterada |
| CI | GitHub Actions, runner windows-latest | ja usado pelo workflow existente |
| Linguagem | Python 3.12 | a do manifesto e de `.abt/RULES.md`; inalterada |

### Integracoes Externas

- GitHub Actions: executa o workflow `tests.yml` com a checagem de tipos.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- Comando unico `python -m mypy --platform win32 filepilot` em todos os itens (Verificacao e Gates).
- O mesmo comando no passo de checagem de tipos do GitHub Actions.
- Ajuste da SPEC 17.2 (secao nova que substitui o escopo negativo sobre o Actions).
- Itens novos para a mudanca no workflow e nos itens existentes, sem tocar o codigo do produto.
- Registro do `filepilot-mypy-1` como atendido e encerrado sem implementar.

### Fora do Escopo (v1)

- Anotar tipos no codigo existente.
- Criar arquivo de configuracao do mypy.
- Mudar a plataforma alvo (Windows 10 e 11, 64 bits).
- Reabrir PRD ou stack.

## Metricas de Sucesso

- Saida do comando unico: codigo 0 e linha `Success: no issues found` em 100% das execucoes, no Linux e no runner windows-latest, ao final da execucao dos itens desta especificacao (baseline atual: o workflow roda `mypy .` sem `--platform win32`).
- Comandos de mypy distintos nos itens e no workflow: 1 comando unico, ao final da execucao dos itens desta especificacao (baseline atual: 2 formas, `mypy .` e `python -m mypy --platform win32 filepilot`).

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
