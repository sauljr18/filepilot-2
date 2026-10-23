# Validacao do item filepilot-version-1 - Opcao --version imprime a versao e sai sem abrir a janela

**Item:** filepilot-version-1 | **Epico:** filepilot-version | **Data:** 2026-10-23
Execucao: 20261023-135213
Veredito: APROVADO
**Tipo do item:** backend (ponto de entrada; o diff nao toca tela)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot tests`: exit 0, `Success: no issues found in 83 source files`; baseline exit 0, zero erros novos (unica linha diferente e a contagem 82 -> 83) |
| 2 Criterios de aceite | PASS | 4/4 atendidos, 0 NAO VERIFICAVEL |
| 3 Qualidade de codigo | PASS | zero problemas: grep TODO/placeholder/not implemented/FIXME vazio nos 2 arquivos; o `print` de `filepilot/__main__.py:65` e a saida exigida por 54.2, nao depuracao |
| 4 Autorizacao e seguranca | PASS | todos verificados: sem endpoint, sem dado sensivel; o desvio nao toca pasta de dados, trava nem banco |
| 5 Testes | PASS | suite inteira 529 passed, 2 skipped (so Windows, `tests/services/test_destination_checks.py:153` e `tests/services/test_scanner_protected.py:185`, pre-existentes); 2 mutacoes refeitas e pegas pela suite |
| 6 Consistencia entre documentos | PASS | consistente com 54.1 e 54.2 (lidas por `abt spec show`, sha conferido) |
| 7b Varredura adversarial | PASS | nenhum: sem entidade nova; comparacao exata de `sys.argv[1:]` sem parser (54.2), nada a reusar |
| 7c Degradacao e borda | PASS | nenhuma das 5 perguntas responde sim (ver nota abaixo) |
| 7d Matriz (backend) | PASS | BE-1: grep `argparse` em `filepilot/__main__.py` = 0; BE-2 e BE-3: n/a (sem service nem policy) |
| 7e Funcao irma e comando citado | PASS | nenhuma: `main()` nao grava estado compartilhado no desvio; nenhuma mensagem nova manda rodar comando |

Nota do 7c: com a saida padrao ligada a um pipe ja fechado, o `print` segue o comportamento padrao do Python (o interpretador avisa na saida de erro ao fechar); a SPEC nao preve esse caso e ele e igual ao de qualquer CLI Python. Registrado so como observacao.

Mutacoes refeitas (escopo: suite inteira, venv de verificacao proprio):

| Mutacao | Diff | Resultado |
|---------|------|-----------|
| M1 | `-    if sys.argv[1:] == ["--version"]:` / `+    if "--version" in sys.argv[1:]:` | 1 failed: `test_outros_argumentos_seguem_o_caminho_de_hoje[extra]` |
| M2 | `-        print(__version__)` / `+        pass` | 2 failed: `test_version_em_subprocesso_imprime_a_versao`, `test_version_em_processo_nao_abre_a_interface` |

Depois das mutacoes: `git diff --stat` igual ao do Passo 0 (`filepilot/__main__.py | 4 ++++`) e suite 529 passed, 2 skipped.

Smoke da `Verificacao:` (sem `DISPLAY`, timeout 30 s): `python -m filepilot --version` -> stdout `0.1.0`, stderr 0 bytes, exit 0.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-version-1-f1 | `python -m filepilot --version` termina com codigo 0, saida padrao exatamente `filepilot.__version__ + "\n"` e saida de erro vazia (teste 1 de 54.2) | PASS | `filepilot/__main__.py:64-66`; `tests/test_version_cli.py:39-49`; smoke exit 0, `0.1.0`, stderr vazio |
| filepilot-version-1-f1 | Com `sys.argv` `["filepilot", "--version"]` e `QApplication`, `default_data_dir` e `open_main_window` levantando `AssertionError`, `main()` devolve 0 e imprime so a versao; com `sys.stdout` `None`, devolve 0 sem excecao (testes 2 e 5) | PASS | `tests/test_version_cli.py:33-36`, `:52-59`, `:82-89` |
| filepilot-version-1-f1 | Com `["filepilot"]` e `["filepilot", "--version", "x"]`, `main()` cria a `QApplication` falsa uma vez, chama `open_main_window` falso uma vez e nao imprime nada (teste 3) | PASS | `tests/test_version_cli.py:62-79`; mutacao M1 pega pelo caso `extra` |
| filepilot-version-1-f1 | `python -m mypy --platform win32 filepilot tests` exit 0 com `Success: no issues found`, e `pytest` exit 0 | PASS | Gate 1 e Gate 5 acima |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
