# filepilot-v1-9 - Aba Organizar: pasta, lista e simulacao
Epico: filepilot-v1 | Ordem: 9 | Pontos: 5 | Depende de: filepilot-v1-2,filepilot-v1-3,filepilot-v1-4,filepilot-v1-8

## Objetivo
Na aba Organizar a pessoa escolhe a pasta, ve cada arquivo com categoria e destino previstos e roda a simulacao com as regras atuais sem alterar nada no disco.

## Contexto herdado
-

## Features

### filepilot-v1-9-f1 Escolher pasta e listar os arquivos
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_tab.py (novo)
- filepilot/ui/main_window.py (novo)
- tests/ui/test_organize_tab_folder.py (novo)
Criterios de aceite:
- Escolher uma pasta com 5 arquivos (dublê de `QFileDialog.getExistingDirectory`) mostra "5 arquivos na pasta", coloca `mode` em `listado` e a tabela mostra 5 linhas.
- Sem pasta, o resumo mostra "Escolha uma pasta para começar." e Simular e Organizar ficam desabilitados.
- `PASTA_VAZIA`, `PASTA_INVALIDA`, `PASTA_ILEGIVEL` e `PASTA_PROTEGIDA` colocam `mode` em `erro`, mostram a mensagem do erro e deixam Simular e Organizar desabilitados.
- Cancelar o seletor mantem tudo como estava.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_tab_folder.py -> exit 0
- parser: python -m py_compile filepilot/ui/organize_tab.py -> exit 0
- grep deve casar: getExistingDirectory em filepilot/ui/organize_tab.py
- dependencias: PySide6 em pyproject.toml
Dicas:
- A aba usa `scan_folder`, `list_rules` e `build_plan` (itens filepilot-v1-2, filepilot-v1-3 e filepilot-v1-4); a interface nunca usa `sqlite3`, `os` ou `shutil` direto (SPEC 3.2, L87-94).
- Troque o marcador "Organizar" criado por `build_tabs` (item filepilot-v1-8) pelo `OrganizeTab` real.
- Os estados `mode` sao `vazio`, `carregando`, `listado`, `simulado`, `organizando` e `erro`; o rotulo "Lendo a pasta..." aparece em `carregando`.

### filepilot-v1-9-f2 Tabela de arquivos FileTableView
Linhas da SPEC: .abt/SPEC.md L459-478
Arquivos:
- filepilot/ui/file_table.py (novo)
- tests/ui/test_file_table.py (novo)
Criterios de aceite:
- Colunas, nesta ordem: Arquivo, Extensão, Categoria, Destino e Regra, com `set_rows(files, plan)`.
- A coluna Categoria mostra o nome da subpasta ("Documentos", "Imagens", "Videos" ou "Compactados"), "Regra personalizada" quando uma regra cobre o arquivo, ou "sem categoria"; o nome da regra aparece so na coluna Regra.
- A coluna Destino mostra o destino relativo a pasta escolhida e fica vazia em `listado` e para "sem categoria"; linha "sem categoria" aparece em cinza.
- Sem linhas mostra "Nenhum arquivo para mostrar."; nao ha ordenacao por clique no cabecalho.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_file_table.py -> exit 0
- parser: python -m py_compile filepilot/ui/file_table.py -> exit 0
- grep deve casar: Regra personalizada em filepilot/ui/file_table.py
- grep nao deve casar: setSortingEnabled(True) em filepilot/ui
Dicas:
- Decisao aprovada no ponto de checagem da SPEC (7.3, linha da coluna Categoria): opcao A do VAG-005.
- Use `QAbstractTableModel` (`FileTableModel`); linha "sem categoria" usa `QPalette.Disabled`.
- Colunas Arquivo e Destino com rolagem horizontal em tela estreita.

### filepilot-v1-9-f3 Simular com regras atuais, Atualizar e plano vazio
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_tab.py (novo)
- tests/ui/test_organize_tab_simulate.py (novo)
Criterios de aceite:
- Simular relê a pasta e recalcula o plano com as regras atuais: depois de criar uma regra com `list_rules`, a simulacao mostra "Regra personalizada" e o nome da regra na coluna Regra.
- O resumo mostra "Simulação: N operações. Nenhum arquivo foi alterado." e a arvore da pasta e identica antes e depois; `mode` vira `simulado`.
- Com plano vazio o resumo mostra "Não há operações para executar." e Organizar fica desabilitado.
- O botao Atualizar relê a pasta, recalcula o plano, volta `mode` para `listado` e descarta a simulacao exibida.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_tab_simulate.py -> exit 0
- grep deve casar: Nenhum arquivo foi alterado em filepilot/ui/organize_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Simular nao grava no historico nem cria pastas: exiba o plano devolvido por `build_plan` (item filepilot-v1-4) e nunca chame `organize`.
- Atualizar fica habilitado com pasta escolhida e fora de `organizando`.

## Gates do item
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
