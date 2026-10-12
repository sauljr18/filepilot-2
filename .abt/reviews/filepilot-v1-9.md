# Validacao do item filepilot-v1-9 - Aba Organizar: pasta, lista e simulacao

**Item:** filepilot-v1-9 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-121617
Veredito: APROVADO - Gate UI-1 DEFERIDO (smoke ao vivo pendente)
Transicoes a cobrir no smoke: vazio -> listado, vazio -> erro, listado -> simulado, simulado -> listado (Atualizar), listado -> erro (pasta apagada ou vazia), erro -> listado (Atualizar depois de corrigir a pasta), cancelar o seletor sem alterar o estado
**Tipo do item:** interface

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "no issues found in 21 source files"; zero erros novos contra a baseline (exit 0, 19 arquivos) |
| 2 Criterios de aceite | PASS | 12/12 criterios atendidos |
| 3 Qualidade de codigo | PASS | zero TODO, FIXME, "not implemented", codigo comentado, print ou caractere Unicode proibido; unicas ocorrencias de "placeholder" sao o nome existente `PlaceholderTab` em main_window.py:28,42-44 |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint; a interface so le a pasta e as regras e nao grava no disco nem no banco |
| 5 Testes | PASS | suite completa 350 passed, 2 skipped (`test_destination_checks.py:153` e `test_scanner_protected.py:185`, ambos "so no Windows", ja existentes); `tests/ui` 49 passed, 31 deles novos |
| 6 Consistencia entre documentos | PASS | nomes de botoes, colunas, estados e textos conferem com SPEC L434-478 e com o contexto herdado |
| 7b Varredura adversarial | PASS | unico consumidor de `build_tabs` e `MainWindow.__init__` (main_window.py:60); `OrganizeTab` ocupa o indice 0, fora de `_RELOAD_ON_FOCUS` (1, 2); servicos reusados (`scan_folder`, `build_plan`, `list_rules`, `CATEGORIES`), nenhum utilitario reinventado |
| 7c Degradacao e borda | FAIL | 1 achado que nao decide o veredito (lista de correcoes, #1): `OSError` durante a leitura da pasta trava a aba em `carregando`; 1 comentario/nome desatualizado (#2) |
| 7d Matriz (interface) | DEFERIDO | UI-1 deferido (abaixo); UI-2 PASS (carregando, vazio e erro presentes: organize_tab.py:130-132, file_table.py:159, organize_tab.py:103-108); UI-3 n/a (uma unica role, sem permissao); UI-4 coberto na linha `Transicoes a cobrir no smoke:` |
| 7e Funcao irma e comando citado | PASS | nenhuma funcao grava estado compartilhado; nenhuma mensagem manda rodar comando |

**Gate UI-1: DEFERIDO - smoke ao vivo pelo Ivan no avanco, antes do commit.** Observacao: a skill `smoke-e2e-playwright` e de aplicacao web com Vuetify, e este projeto e um aplicativo desktop PySide6 para Windows; ela nao se aplica como esta. O smoke ao vivo exige abrir o aplicativo (`python -m filepilot`) e percorrer as transicoes acima, de preferencia no Windows. A pessoa decide no ponto de checagem como cobrir isso.

Validacao do 7c: a Rita reproduziu o achado #1 com um `OSError(5, "Input/output error")` no lugar do `scan_folder`: o `excepthook` recebeu o `OSError`, `mode` ficou `carregando`, o resumo ficou "Lendo a pasta..." e `choose`, `refresh` e `simulate` ficaram todos `False`.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-9-f1 | 5 arquivos mostram "5 arquivos na pasta", `mode` `listado`, 5 linhas | PASS | organize_tab.py:110-114; test_organize_tab_folder.py:59 |
| filepilot-v1-9-f1 | Sem pasta: "Escolha uma pasta para comecar." e Simular/Organizar desabilitados | PASS | organize_tab.py:31,98-101,95-96; test_organize_tab_folder.py:45 |
| filepilot-v1-9-f1 | `PASTA_VAZIA`, `PASTA_INVALIDA`, `PASTA_ILEGIVEL`, `PASTA_PROTEGIDA` dao `mode` `erro`, mensagem e botoes desabilitados | PASS | organize_tab.py:103-108,136-138; test_organize_tab_folder.py:110 (parametrizado, 4 codigos) |
| filepilot-v1-9-f1 | Cancelar o seletor mantem tudo como estava | PASS | organize_tab.py:147-149; test_organize_tab_folder.py:165,188 |
| filepilot-v1-9-f2 | Colunas Arquivo, Extensao, Categoria, Destino e Regra, com `set_rows(files, plan)` | PASS | file_table.py:20,85,182; test_file_table.py:41 |
| filepilot-v1-9-f2 | Categoria mostra subpasta, "Regra personalizada" ou "sem categoria"; nome da regra so em Regra | PASS | file_table.py:25-26,44-54; test_file_table.py:52,73 |
| filepilot-v1-9-f2 | Destino relativo a pasta, vazio em `listado` e para "sem categoria"; "sem categoria" em cinza | PASS | file_table.py:62-66,126-129; organize_tab.py:112; test_file_table.py:89,106 |
| filepilot-v1-9-f2 | Sem linhas mostra "Nenhum arquivo para mostrar."; sem ordenacao por clique | PASS | file_table.py:27,159,170,194; test_file_table.py:132,147; `grep setSortingEnabled(True) filepilot/ui` sem resultado |
| filepilot-v1-9-f3 | Simular relê a pasta e recalcula com as regras atuais ("Regra personalizada" e nome da regra) | PASS | organize_tab.py:128-141,161-167; test_organize_tab_simulate.py:92,110,128 |
| filepilot-v1-9-f3 | Resumo "Simulação: N operações. Nenhum arquivo foi alterado.", arvore identica, `mode` `simulado` | PASS | organize_tab.py:116-124; test_organize_tab_simulate.py:58,77 |
| filepilot-v1-9-f3 | Plano vazio: "Não há operações para executar." e Organizar desabilitado | PASS | organize_tab.py:118-119,96; test_organize_tab_simulate.py:144 |
| filepilot-v1-9-f3 | Atualizar relê, recalcula, volta a `listado` e descarta a simulacao | PASS | organize_tab.py:154-159; test_organize_tab_simulate.py:181,203,219 |

Gates do item reexecutados pela Rita: typecheck exit 0; `pytest tests/ui` 49 passed; awk do Passo 6 sem saida; greps "deve casar" de f1, f2 e f3 com resultado (`getExistingDirectory` em organize_tab.py:147, "Regra personalizada" em file_table.py:25, "Nenhum arquivo foi alterado" em organize_tab.py:35); grep Unicode em `filepilot` sem resultado; `PySide6` em pyproject.toml:11.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/ui/organize_tab.py | 133-138 | `_read_folder` captura so `FilePilotError`. `scan_folder` relança `OSError` que nao seja laco de atalho (scanner.py:52-61) e `build_plan` resolve caminhos sem tratar erro de E/S. Qualquer um deles deixa `mode` em `carregando` com Escolher pasta, Atualizar e Simular desabilitados: a aba fica inutilizavel ate fechar o aplicativo. | Tratar `OSError` (e `RuntimeError` de `resolve`) em `_read_folder`, indo para `erro` com mensagem de leitura (por exemplo a de `PASTA_ILEGIVEL`), e acrescentar teste em test_organize_tab_folder.py. | nao |
| 2 | tests/ui/test_main_window.py | 48 | O nome `test_build_tabs_devolve_tres_marcadores_na_ordem` ficou falso: Organizar agora e a aba real. A asserção continua valida. | Renomear para `test_build_tabs_devolve_tres_abas_na_ordem` (desejavel; o arquivo esta fora de `Arquivos:`). | nao |
| 3 | tests/ui/test_organize_tab_simulate.py | 233-234 | O teste forca `tab.mode = "organizando"` e chama `_update_buttons()` (interno); test_file_table.py:137-144 usa `view._stack`. Acopla o teste a nomes privados. | Desejavel: expor um indicador publico ou testar pelo item 10, que introduz o estado `organizando`. | nao |

Observacoes sem correcao: o botao Organizar habilita conforme SPEC 7.2 (organize_tab.py:96), mas ainda nao tem acao; a execucao, a barra de progresso e o Desfazer sao dos itens filepilot-v1-10 e filepilot-v1-11. `organize_tab.py` e `main_window.py` importam `sqlite3` so para anotacao de tipo. `filepilot.egg-info` e `__pycache__` aparecem como nao rastreados e nao devem ser commitados.
