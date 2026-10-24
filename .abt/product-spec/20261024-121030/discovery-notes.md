# Discovery Notes: Opcao --help na linha de comando

**Data:** 2026-10-24
**Condutora:** Dani Descoberta

Modo: delta focado

## Contexto e Problema

- **Problema central:** `python -m filepilot --help` (ou `-h`) abre a janela do aplicativo; quem usa a linha de comando não tem como ver o uso (as opções `--help` e `--version`).
- **Situacao atual (sem o produto):** `main()` em `filepilot/__main__.py` só desvia com o argumento único `--version` (§54, comparação exata de `sys.argv[1:]`); qualquer outro argumento, inclusive `--help` e `-h`, segue para a `QApplication` e abre a janela.
- **Por que agora:** a §54 trouxe a primeira opção de linha de comando (`--version`); falta o texto de uso que a apresente.

## Personas

### Ana (persona 1 da SPEC)

- **Papel no produto:** usa o FilePilot e confere pela linha de comando como usá-lo (§54).
- **Objetivo principal:** ver as opções da linha de comando sem abrir a janela.
- **Frustracao atual:** `--help` abre a janela em vez de mostrar o uso.

### Carlos (persona 1 da SPEC)

- **Papel no produto:** mesmo uso da Ana pela linha de comando (§54).
- **Objetivo principal:** ver as opções da linha de comando sem abrir a janela.
- **Frustracao atual:** `--help` abre a janela em vez de mostrar o uso.

## Funcionalidades Core (v1)

1. Ajuda por `--help`: o usuário roda `python -m filepilot --help`, como argumento único, e o aplicativo imprime o texto de uso na saída padrão e sai com código 0, sem abrir a janela.
2. Ajuda por `-h`: o usuário roda `python -m filepilot -h`, como argumento único, com o mesmo efeito de `--help`.
3. Texto de uso: o aplicativo imprime, em português e terminando com nova linha, a linha `uso: python -m filepilot [--help | -h | --version]` seguida de uma linha por opção com a descrição.
4. Demais argumentos: qualquer outra combinação de argumentos (inclusive `--help` ou `-h` junto de outros) segue abrindo a janela como hoje; sem parser de argumentos (decisão da §54).
5. Sem saída padrão (`pythonw`): `--help` e `-h` seguem a mesma regra do `--version` da §54: `main()` devolve 0 sem exceção.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Linguagem e interface | Python e PySide6 (stack inalterada) | A do manifesto e de `.abt/RULES.md`; a mudança é só no ponto de entrada |

### Integracoes Externas

Nenhuma: a mudança é só no ponto de entrada `filepilot/__main__.py`.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- `--help` e `-h`, cada um como argumento único (comparação exata, igual ao `--version`), imprimem o uso e saem com 0 sem abrir a janela.
- Texto de uso em português, terminando com nova linha, citando `--help`, `-h` e `--version`.
- Sem saída padrão (`pythonw`): devolve 0 sem exceção, como o `--version`.

### Fora do Escopo (v1)

- `-V` e outros argumentos de linha de comando.
- Mudar o comportamento do `--version` da §54.
- Mostrar o uso na janela do aplicativo.
- Saída de uso no executável do PyInstaller (sem console, §44).

## Metricas de Sucesso

- Ajuda pela linha de comando: `python -m filepilot --help` e `python -m filepilot -h` imprimem o uso e saem com 0, sem abrir a janela (baseline atual: abrem a janela).

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
