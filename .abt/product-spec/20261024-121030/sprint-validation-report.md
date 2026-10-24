# Relatorio de Prontidao para o Fatiamento: Opcao --help na linha de comando

**Data:** 2026-10-24
**Modo:** delta focado

## 1. Cobertura de Requisitos

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| `--help`, argumento unico, imprime o uso e sai com 0 sem abrir a janela | 56.3 (desvio em `main()`); 56.4 testes 1 e 2 | coberto |
| `-h`, argumento unico, faz o mesmo que `--help` | 56.3; 56.4 testes 1 e 2 (parametrizados) | coberto |
| Texto de uso em portugues, terminando com nova linha, uma linha por opcao | 56.3 (`_USAGE`, `print`); 56.4 (texto literal) | coberto |
| Demais combinacoes de argumentos abrem a janela; sem parser | 56.3 (comparacao exata); 56.4 teste 3 | coberto |
| Sem saida padrao (`pythonw`): devolve 0 sem excecao | 56.3; 56.4 teste 4 | coberto |
| Fora de escopo (`-V`, `--version` de 54.2, janela, PyInstaller) | 56.1; 56.2 (errata `{acrescenta: 54.1}`) | coberto |
| Metrica: `--help` e `-h` imprimem o uso e saem com 0, sem janela | 56.4 teste 1 | coberto |

Decisao registrada (nao e lacuna): `[DECISAO: aprovada no enriquecimento; sugestao 1]` em 56.3 (saida padrao que nao codifica `ã` e `õ` sai com 1, sem teste).

**Lacunas:** 0

## 2. Mapa de Dependencias

| Parte | Depende de |
|---|---|
| 56.3 desvio de `--help` e `-h` em `filepilot/__main__.py` | `filepilot-version-1` (pronto): o desvio de `--version` de 54.2, logo antes do qual o novo desvio entra |
| 56.4 testes em `tests/test_help_cli.py` | 56.3 (o desvio que os testes exercitam) |

**Dependencias criticas:** nenhuma; a unica dependencia externa, `filepilot-version-1`, ja esta `pronto` (`grep -l 'test_version_cli' .abt/items/*/*.md`: so `.abt/items/filepilot-version/filepilot-version-1.md`).

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| 56.3 + 56.4 (desvio, constante `_USAGE` e testes, um objetivo verificavel) | Simples | 2 |

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| Texto de uso com `ã` e `õ` falha com saida padrao sem essa codificacao (decisao aprovada, sem teste) | Baixo | Nenhuma: limite aceito em 56.3; o CI roda em `windows-latest` sem `PYTHONIOENCODING` |
| Espacos do alinhamento de `_USAGE` digitados errado quebram os testes 1 e 2 (texto literal) | Baixo | O detalhe do item cita o bloco `text` de 56.3 como fonte exata |

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro cabe em 1 item de 2 pontos (desvio, constante e testes), dependendo so de `filepilot-version-1`, ja pronto.

## 6. Dados para o fatiamento

- Epicos ja usados (`abt epic list --ids --json`): `filepilot-fix`, `filepilot-fix2`, `filepilot-fix3`, `filepilot-mypy`, `filepilot-mypy-win32`, `filepilot-v1`, `filepilot-version`.
- Itens ja usados (`abt queue list --json`, todos `pronto`): `filepilot-fix-1` a `-4`, `filepilot-fix2-1` a `-4`, `filepilot-fix3-1` a `-7`, `filepilot-mypy-1`, `filepilot-mypy-win32-1` e `-2`, `filepilot-v1-1` a `-13`, `filepilot-version-1`.
- Dependencia com item existente: `filepilot-version-1` (desvio de `--version`, `tests/test_version_cli.py`).

Pronto para fatiamento: SIM
