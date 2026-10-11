# Relatorio de Prontidao para o Fatiamento: FilePilot - mypy nas ferramentas de desenvolvimento e plataforma alvo Windows 10 e 11 (64 bits)

**Data:** 2026-10-11
**Modo:** so SPEC + itens

## 1. Cobertura de Requisitos

Escopo de `discovery-notes.md` (Funcionalidades Core), conferido contra a secao 17 de `.abt/SPEC.md` e nao so contra a Traceability Matrix.

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| Registro do mypy: ferramenta de desenvolvimento junto com pytest, na tabela de stack e nas dependencias de desenvolvimento do `pyproject.toml` | 17.2: linha `mypy` 2.4.0 acrescentada a tabela de 4, `mypy==2.4.0` no `pyproject.toml` e comando `python -m mypy --platform win32 filepilot` | coberto |
| Registro da plataforma alvo: Windows 10 e 11 em 64 bits como decisao da especificacao | 17.3 (formaliza a frase de 13) | coberto |

**Lacunas:** 0. Nenhum item `parcial`, `ausente` ou `CORTADO`. A decisao de plataforma (17.3) e documental: nao exige codigo, e nao cria item (escopo negativo de 17.3: nenhum teste de arquitetura, `requires-python` inalterado).

## 2. Mapa de Dependencias

| Parte | Depende de |
|---|---|
| Declarar `mypy==2.4.0` em `pyproject.toml` | `filepilot-v1-1` (Fundacao: projeto, dominio, banco e CI Windows), que cria o `pyproject.toml` (SPEC 14, item 6 do plano de entrega e 4) |
| Comando de checagem `python -m mypy --platform win32 filepilot` verde | `filepilot-v1-1` (cria o pacote `filepilot` e o manifesto) e a instalacao do mypy declarada acima |
| Decisao de plataforma (17.3) | nenhuma (texto da SPEC) |

**Dependencias criticas:** `filepilot-v1-1`. Ele esta `na_fila` e disponivel, e e o unico item que os itens de mypy precisam esperar. Nenhuma parte nova bloqueia item existente.

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| mypy no `pyproject.toml` e comando de checagem verde sobre o pacote existente | Simples | 2 |
| Decisao de plataforma (17.3) | sem item de codigo | 0 |

Total estimado: 2 pontos, 1 item, com 1 objetivo verificavel (o comando de checagem sai com codigo 0).

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| O `pyproject.toml` so existe depois de `filepilot-v1-1`, que ainda esta na fila: o item de mypy sem `Depende de: filepilot-v1-1` poderia ser assumido antes do manifesto existir | Medio | O fatiamento declara `Depende de: filepilot-v1-1` no item de mypy |
| O detalhe e os gates dos 13 itens existentes nao citam mypy, entao a checagem nao entra neles; o item novo verifica so o codigo que existir quando for implementado | Baixo | Nao editar os 13 itens (fora de escopo, 17.1); o gate do item novo e o comando de 17.2 sobre o codigo do momento |
| Codigo dos itens seguintes (`filepilot-v1-2` em diante) pode ser mesclado sem checagem de tipos, ate o item de mypy ser implementado | Baixo | Aceito: 17.2 define a checagem como comando manual de desenvolvimento, sem etapa no GitHub Actions |
| A versao `mypy==2.4.0` e a mais recente do PyPI em 2026-10-11 (`[DECISAO]` do Gabriel); uma versao nova pode mudar o resultado da checagem | Baixo | A versao fica fixada no `pyproject.toml`; trocar e decisao de outra especificacao |

Sem risco `Bloqueante`. Pendencias aprovadas no relatorio do Rafael (`spec-validation-report.md`, Round 2): nenhuma.

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro da mudanca cabe num caminho critico de 1 item de 2 pontos (mypy no manifesto e comando de checagem), depois de `filepilot-v1-1`; a decisao de plataforma nao precisa de item. Numero estimado de itens: 1.

## 6. Dados para o fatiamento

Fonte: `abt epic list --ids --json` e `abt queue list --json`, rodados nesta fase (ambos `ok: true`).

- Epicos ja usados no projeto: `filepilot-v1`.
- Itens ja usados no projeto (todos do epico `filepilot-v1`, todos `na_fila`): `filepilot-v1-1`, `filepilot-v1-2`, `filepilot-v1-3`, `filepilot-v1-4`, `filepilot-v1-5`, `filepilot-v1-6`, `filepilot-v1-7`, `filepilot-v1-8`, `filepilot-v1-9`, `filepilot-v1-10`, `filepilot-v1-11`, `filepilot-v1-12`, `filepilot-v1-13`.
- Disponivel hoje (sem bloqueio): `filepilot-v1-1`. Os demais dependem dele, direta ou indiretamente.
- Dependencias com itens existentes: o item de mypy depende de `filepilot-v1-1` (Fundacao: projeto, dominio, banco e CI Windows). `filepilot-v1-13` (Executavel Windows com PyInstaller e CI) nao depende do item de mypy.
- Ids novos (epico e item) sao escolhidos pelo fatiamento, sem colidir com os acima.

Pronto para fatiamento: SIM
