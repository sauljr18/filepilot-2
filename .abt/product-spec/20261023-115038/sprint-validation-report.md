# Relatorio de Prontidao para o Fatiamento: Opcao --version na linha de comando

**Data:** 2026-10-23
**Modo:** so SPEC + itens

## 1. Cobertura de Requisitos

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| `python -m filepilot --version` imprime o `__version__` de `filepilot/__init__.py` | 54.2: desvio no início de `main()` com `print(__version__)`; testes 1 e 2 | coberto |
| O comando sai com código 0 e não abre a interface gráfica | 54.2: `return 0` antes da `QApplication`, sem trava, banco nem janela; testes 1, 2 e 5 | coberto |
| Fora de escopo: outros argumentos (`-V`, `--help`) | 54.1; 54.2: comparação exata de `sys.argv[1:]`, sem parser; teste 3 | coberto |
| Fora de escopo: mudar o valor ou a fonte da versão | 54.1 | coberto |
| Fora de escopo: a versão não aparece na janela | 54.1 | coberto |
| Fora de escopo: sem argumento o aplicativo abre como hoje | 54.2: caminho de hoje inalterado; teste 3 | coberto |
| Métrica: imprime a versão e sai com 0, sem janela | 54.2: teste 1 (subprocesso real) | coberto |

Conferido na SPEC (seção 54), não só na Traceability Matrix de 54.4.

**Lacunas:** 0.

## 2. Mapa de Dependencias

| Parte | Depende de |
|---|---|
| Desvio `--version` em `main()` (54.2) | `__version__` existente em `filepilot/__init__.py:3`; `main()` atual em `filepilot/__main__.py:62` a `:69` |
| Testes 1 a 3 e 5 (`tests/test_version_cli.py`) | Desvio `--version` em `main()` |
| Gate de tipos (54.2 teste 4) | Comando único de 19.2 com 45.7 (`python -m mypy --platform win32 filepilot tests`), já na main |

Itens existentes: `grep -l '__main__' .abt/items/*/*.md` devolve `filepilot-v1-8`, `-9`, `-12`, `-13`, `filepilot-fix2-3` e `filepilot-fix3-7`; o mais recente deles, `filepilot-fix3-7`, já está na main (merge do PR #37, commit `6194b55`); nenhuma dependência de item aberto.

**Dependencias criticas:** nenhuma; a mudança é uma parte só, sem infraestrutura nova.

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| Desvio `--version` em `main()` com os testes 1 a 5 de 54.2 | Simples | 1 |

Um subcomportamento (o desvio) e um componente (`filepilot/__main__.py`), mais um arquivo de teste: cabe num item.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| Teste 1 exige `stderr == ""`: um aviso do Python ou do PySide6 no runner Windows (por exemplo `DeprecationWarning` impresso) quebraria o teste sem defeito no código | Baixo | No item, rodar o teste 1 no Linux e no runner `windows-latest`; se aparecer aviso, a correção é do item, não da SPEC |
| Projeto ativo do `abt` mudou para `smartoffer` durante esta execução (reativado `filepilot-2` a pedido da pessoa) | Baixo | As fases seguintes conferem o projeto ativo antes de consultar épicos e itens |

## 5. Prontidao

**MVP pronto:** Sim - o escopo inteiro da mudança é uma parte Simples de 1 ponto, sem dependência aberta; 1 item estimado.

## 6. Dados para o fatiamento

- Épicos já usados no projeto (`abt epic list --ids --json`, com o projeto `filepilot-2` reativado): `filepilot-fix`, `filepilot-fix2`, `filepilot-fix3`, `filepilot-mypy`, `filepilot-mypy-win32`, `filepilot-v1`.
- Itens já usados (`abt queue list --ids --json`, 31): `filepilot-fix-1` a `-4`, `filepilot-fix2-1` a `-4`, `filepilot-fix3-1` a `-7`, `filepilot-mypy-1`, `filepilot-mypy-win32-1` e `-2`, `filepilot-v1-1` a `-13`.
- Dependências com itens existentes: nenhuma aberta.
- A primeira consulta desta fase devolveu épicos e itens do `smartoffer` (projeto ativo trocado fora desta execução); os dados acima são os da consulta repetida depois da reativação.

Pronto para fatiamento: SIM
