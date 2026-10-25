# Relatorio de Prontidao para o Fatiamento: Opcao -V na linha de comando

**Data:** 2026-10-25
**Modo:** delta focado

## 1. Cobertura de Requisitos

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| Escopo 1: `python -m filepilot -V`, argumento unico, imprime a versao e sai com 0 sem abrir a janela, com a mesma saida do `--version` | 58.4 (desvio `sys.argv[1:] in (["--version"], ["-V"])` em `main()`); 58.6 itens 1 e 2 (testes em `tests/test_version_cli.py`) | coberto |
| Escopo 2: o texto do `--help` e do `-h` cita `-V`, e o teste do `--help` acompanha | 58.5 (`_USAGE` com quatro linhas, substitui 56.3); 58.6 (`EXPECTED_USAGE` em `tests/test_help_cli.py`) | coberto |
| Fora de escopo: `-V` com outros argumentos, `-v`, `--V` | 58.1; 58.4 (comparacao exata); 58.6 item 2 (casos `-V x` e `-v`) | coberto |
| Fora de escopo: parser de argumentos | 58.1; 58.4 | coberto |
| Fora de escopo: versao no executavel e na janela | 58.1 | coberto |
| Fora de escopo: valor e fonte da versao, saida do `--version`, `--help`/`-h` fora do texto de uso | 58.1; 58.4; 58.5 | coberto |
| Metrica: `-V` com a mesma saida do `--version`, codigo 0, sem janela | 58.6 item 1 (testes de subprocesso e em processo parametrizados) | coberto |

**Lacunas:** 0. Conferido na propria secao 58 e no codigo (`filepilot/__main__.py:25`, `:69` a `:82`; `tests/test_version_cli.py:62` e `:63`; `tests/test_help_cli.py:8` a `:13`), nao so na Traceability Matrix.

## 2. Mapa de Dependencias

| Parte | Depende de |
|---|---|
| P1: desvio `-V` em `main()` (58.4) | `filepilot-version-1` (desvio de `--version`, 54.2, `pronto`) e `filepilot-help-1` (ordem dos desvios, 56.3, `pronto`) |
| P2: `_USAGE` com `-V` (58.5) | `filepilot-help-1` (`_USAGE` atual, `pronto`) |
| P3: testes de `-V` (58.6, `tests/test_version_cli.py`) | P1 antes de P3 |
| P4: `EXPECTED_USAGE` (58.6, `tests/test_help_cli.py`) | P2 antes de P4 |

**Dependencias criticas:** nenhuma parte bloqueia mais de uma outra; P1 e P2 tocam o mesmo arquivo (`filepilot/__main__.py`) e cada uma tem o seu teste. Sem infraestrutura nova (fila, cache, servico externo).

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| P1 + P3: desvio `-V` e testes | Simples | 1 |
| P2 + P4: texto de uso e teste do `--help` | Simples | 1 |
| Escopo inteiro (P1 a P4) | Simples | 2 |

Nenhuma parte acima de 8 pontos; um unico objetivo verificavel ("`-V` funciona como `--version` e aparece na ajuda") cobre as quatro partes, que mudam um arquivo de codigo e dois de teste.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| P1 e P2 em itens separados mexeriam no mesmo `filepilot/__main__.py` e o teste do `--help` ficaria inconsistente entre as duas entregas | Baixo | fatiar o escopo inteiro num item so |
| Os itens entregues `filepilot-version-1` e `filepilot-help-1` citam as ancoras 54.1, 54.2, 56.1 e 56.3, que as erratas da secao 58 mudam; o `abt spec check` deles passaria a falhar com 103 | Baixo | nenhuma: os dois estao `pronto` e integrados (§55, §57); o item novo cita as ancoras da secao 58 |

Nenhum risco `Bloqueante` nem pendencia aprovada no relatorio do Rafael (status `APROVAVEL`, zero itens aguardando decisao).

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro cabe num caminho critico de 1 item de cerca de 2 pontos, sem dependencia aberta (as duas dependencias sao itens `pronto`).

## 6. Dados para o fatiamento

- Epicos existentes (`abt epic list --ids --json`): `filepilot-fix`, `filepilot-fix2`, `filepilot-fix3`, `filepilot-help`, `filepilot-mypy`, `filepilot-mypy-win32`, `filepilot-v1`, `filepilot-version`.
- Itens existentes (`abt queue list --json`, 33, todos `pronto`): `filepilot-fix-1` a `-4`, `filepilot-fix2-1` a `-4`, `filepilot-fix3-1` a `-7`, `filepilot-help-1`, `filepilot-mypy-1`, `filepilot-mypy-win32-1` e `-2`, `filepilot-v1-1` a `-13`, `filepilot-version-1`.
- Dependencias com itens existentes: `filepilot-version-1` e `filepilot-help-1` (ambos `pronto`).
- Itens que citam as ancoras alteradas (`grep -l` em `.abt/items/*/*.md`): `.abt/items/filepilot-help/filepilot-help-1.md` e `.abt/items/filepilot-version/filepilot-version-1.md`.

Pronto para fatiamento: SIM
