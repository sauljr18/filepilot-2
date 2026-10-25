# Discovery Notes: Opcao -V na linha de comando

**Data:** 2026-10-25
**Condutora:** Dani Descoberta

Modo: delta focado

## Contexto e Problema

- **Problema central:** so o argumento unico `--version` mostra a versao do FilePilot pela linha de comando; `python -m filepilot -V` abre a janela do aplicativo em vez de imprimir a versao.
- **Situacao atual (sem o produto):** `main()` (`filepilot/__main__.py:69` a `:71`) desvia so com `sys.argv[1:] == ["--version"]` (54.2) e com `--help` ou `-h` (56.3); `-V` segue para a `QApplication`. A secao 54.1 e a 56.1 deixaram `-V` fora de escopo.
- **Por que agora:** a pessoa pediu que `-V` faca o mesmo que `--version`: imprimir a versao e sair, sem abrir a janela.

## Personas

### Ana e Carlos (personas da secao 1)

- **Papel no produto:** usam o FilePilot pela linha de comando (54.1, 56.1).
- **Objetivo principal:** conferir a versao instalada com `-V`, a forma curta, como com `--version`.
- **Frustracao atual:** `-V` abre a janela do aplicativo em vez de mostrar a versao.

## Funcionalidades Core (v1)

1. Versao com -V: a pessoa roda `python -m filepilot -V`, como argumento unico, e ve a versao (o `__version__`, hoje `0.1.0`) na saida padrao; o processo sai com codigo 0, sem abrir a janela, igual ao `--version` de 54.2.
2. Ajuda cita -V: o texto do `--help` (`_USAGE`, `filepilot/__main__.py:25`) passa a citar `-V` junto do `--version`; o teste do `--help` (`tests/test_help_cli.py`) acompanha o texto novo.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Toda | inalterada: a do `pyproject.toml` e de `.abt/RULES.md` | delta focado: a stack ja esta decidida e a mudanca so toca o ponto de entrada |

### Integracoes Externas

Nenhuma integracao externa: a mudanca so toca o ponto de entrada `filepilot/__main__.py`.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- `python -m filepilot -V`, como argumento unico, imprime a versao e sai com 0, sem abrir a janela, com a mesma saida do `--version`.
- O texto do `--help` e `-h` passa a citar `-V` junto do `--version`, e o teste do `--help` acompanha.

### Fora do Escopo (v1)

- `-V` com outros argumentos (ex.: `-V x`) segue o caminho de hoje, como o `--version` com argumentos extras (54.2).
- Parser de argumentos (mesmo motivo de 54.2).
- Versao no executavel do PyInstaller (sem console, 54.1) e na janela do aplicativo.
- Mudar o valor ou a fonte da versao, ou o comportamento do `--version`, do `--help` e do `-h`.

## Metricas de Sucesso

Saida do -V: `python -m filepilot -V` imprime a mesma saida do `--version`, sai com 0 e nao abre janela (qualitativa, verificavel por teste).

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
