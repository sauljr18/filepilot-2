# Validacao do item filepilot-fix2-2 - Aba Organizar sai de carregando quando a leitura da pasta falha com erro do sistema

**Item:** filepilot-fix2-2 | **Epico:** filepilot-fix2 | **Data:** 2026-10-12
Execucao: 20261012-150032
Veredito: APROVADO - Gate UI-1 DEFERIDO (smoke ao vivo pendente)
Transicoes a cobrir no smoke: carregando -> erro (OSError ao escolher a pasta, atualizar ou simular), listado -> erro (simular com OSError), erro -> listado (atualizar com a pasta de volta legivel)
**Tipo do item:** interface

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "no issues found in 23 source files"; zero erro novo contra a baseline (exit 0) |
| 2 Criterios de aceite | PASS | 5/5 criterios atendidos |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented e FIXME nos dois arquivos do diff; sem codigo comentado nem print; sem travessao ou aspas tipograficas Unicode |
| 4 Autorizacao e seguranca | PASS | sem endpoint; o texto bruto da excecao nao chega a interface (`organize_tab.py:142-145`) |
| 5 Testes | PASS | suite completa: 391 passaram, 2 pulados (`test_destination_checks.py:153` e `test_scanner_protected.py:185`, ambos "so existe/vale no Windows"); 6 testes novos cobrem os 6 itens de 37.3; mutacoes refeitas |
| 6 Consistencia entre documentos | PASS | codigo igual a SPEC 37.3 (L1126-1146): `except OSError` depois do `except FilePilotError`, `_UNREADABLE` com o texto de PASTA_ILEGIVEL, estado de erro pelo `_show_error`; escopo so OSError |
| 7b Varredura adversarial | PASS | `_read_folder` so tem os chamadores `refresh` e `simulate` (`organize_tab.py:165,172`; `choose_folder` passa por `refresh`), todos cobertos pelo ponto unico; nenhum utilitario reinventado (o texto repetido e decisao da SPEC, com teste de igualdade) |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim": antes o OSError escapava do slot e deixava a aba presa, agora vai a erro; sem valor zero ou vazio invertido; sem fraqueza antiga tornada material; comentarios de `organize_tab.py:36-37` e `:143` continuam verdadeiros |
| 7d Matriz (interface) | DEFERIDO | UI-1 deferido ao Ivan; UI-2 PASS (a aba cobre vazio, carregando, listado, simulado e erro); UI-3 n/a (aba sem permissao por role); UI-4 listado em "Transicoes a cobrir no smoke" |
| 7e Funcao irma e comando citado | PASS | nenhuma divergencia: `_read_folder` nao grava estado compartilhado fora de `files` e `plan`, como os irmaos `_show_*`; nenhuma mensagem manda rodar comando |

Gate UI-1: DEFERIDO - smoke ao vivo pelo Ivan no avanco, antes do commit. Observacao: a aplicacao e PySide (janela desktop); o smoke e uma conferencia manual da aba, e os testes de interface com `pytest-qt` ja cobrem as transicoes acima.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix2-2-f1 | `scan_folder` com `PermissionError("acesso negado")`: depois de `choose_folder()` o `mode` e erro e o resumo e exatamente "Não foi possível ler a pasta escolhida.", sem "acesso negado" | PASS | `organize_tab.py:142-145`; `tests/ui/test_organize_tab_read_error.py` (`test_oserror_na_leitura_da_pasta_leva_a_aba_ao_estado_de_erro` e `test_a_mensagem_de_erro_nao_traz_o_texto_bruto_da_excecao`) |
| filepilot-fix2-2-f1 | Nesse estado: 0 linhas, `files == []`, `plan is None`; Simular e Organizar desabilitados; Escolher pasta e Atualizar habilitados | PASS | `organize_tab.py:106-111` e `:93-99`; `_assert_read_error_state` no arquivo de teste |
| filepilot-fix2-2-f1 | Pasta ja listada e `scan_folder` com OSError: `simulate()` leva a erro com o mesmo estado; com o servico real, `refresh()` leva a `listado` com os arquivos | PASS | `organize_tab.py:168-174` e `:161-166`; `test_simular_com_oserror_depois_de_listar...` e `test_atualizar_depois_do_erro_recupera_a_aba` |
| filepilot-fix2-2-f1 | `Path.resolve` com `PermissionError` so para a pasta escolhida, sem trocar `scan_folder`: `choose_folder()` leva a erro | PASS | `test_permission_error_do_resolve_sem_trocar_o_servico_leva_a_erro` (a excecao sobe de `scanner._resolve_folder` e e capturada em `organize_tab.py:142`) |
| filepilot-fix2-2-f1 | `_UNREADABLE` igual a `scanner._MESSAGES["PASTA_ILEGIVEL"]` | PASS | `organize_tab.py:38` e `scanner.py:15`; `test_o_texto_da_interface_e_o_de_pasta_ilegivel_do_scanner` |

## Mutacoes refeitas pela Rita (escopo: suite inteira, revertidas por copia de arquivo)

| Mutacao | Diff | Resultado |
|---------|------|-----------|
| A: suprimir a mostra do erro | `organize_tab.py:144` `self._show_error(FilePilotError("PASTA_ILEGIVEL", _UNREADABLE))` -> `pass` | 4 falhas, 387 passaram, 2 pulados |
| B: alterar o texto da constante | `organize_tab.py:38` "Não foi possível ler..." -> "Nao foi possivel ler..." | 4 falhas, 387 passaram, 2 pulados |

Depois das duas: `git status --short` e `git diff --stat` iguais aos de antes (1 arquivo, 7 insercoes), suite verde.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| - | nenhuma | - | nenhum achado | - | - |
