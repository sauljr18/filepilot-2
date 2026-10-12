# filepilot-v1-8 - Janela principal, abas e instancia unica
Epico: filepilot-v1 | Ordem: 8 | Pontos: 3 | Depende de: filepilot-v1-1

## Objetivo
python -m filepilot abre a MainWindow com as abas Organizar, Histórico e Regras, com instancia unica, falha de banco tratada e bloqueio de fechamento durante a organizacao.

## Contexto herdado
-

## Features

### filepilot-v1-8-f1 MainWindow com tres abas
Linhas da SPEC: .abt/SPEC.md L415-433
Arquivos:
- filepilot/__main__.py (novo)
- filepilot/ui/__init__.py (novo)
- filepilot/ui/main_window.py (novo)
- tests/ui/test_main_window.py (novo)
Criterios de aceite:
- Com pytest-qt em modo offscreen, a `MainWindow` tem o titulo "FilePilot" e um `QTabWidget` com as abas "Organizar", "Histórico" e "Regras", nesta ordem.
- `MainWindow.organizing` comeca `False` e a `MainWindow` guarda `conn` aberta por `open_connection`.
- Ao trocar para a aba Historico ou Regras, a aba recarrega os dados (sinal `currentChanged`).
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_main_window.py -> exit 0
- parser: python -m py_compile filepilot/ui/main_window.py -> exit 0
- grep deve casar: setApplicationName("FilePilot") em filepilot/__main__.py
- dependencias: PySide6 em pyproject.toml
Dicas:
- Esta feature cria as tres abas como `QWidget` simples (marcadores de posicao) em uma funcao `build_tabs(conn)`; os itens filepilot-v1-9, filepilot-v1-11 e filepilot-v1-12 trocam cada marcador pela aba real.
- Confirme que a classe e o metodo do PySide6 6.12.0 existem na versao instalada antes de usa-los.
- O caminho do banco vem de `QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)` mais `filepilot.db` (SPEC 5.1, L126-132).

### filepilot-v1-8-f2 Instancia unica com QLockFile
Linhas da SPEC: .abt/SPEC.md L415-433
Arquivos:
- filepilot/__main__.py (novo)
- tests/ui/test_single_instance.py (novo)
Criterios de aceite:
- Antes de abrir o banco, `main()` toma `QLockFile` em `filepilot.lock` na pasta de dados; com a trava ja tomada mostra "O FilePilot já está aberto." e termina com codigo 0 sem criar a janela e sem abrir o banco.
- A trava e liberada no `closeEvent`; trava velha de um processo que caiu e recuperada na abertura seguinte (`setStaleLockTime`).
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_single_instance.py -> exit 0
- parser: python -m py_compile filepilot/__main__.py -> exit 0
- grep deve casar: QLockFile em filepilot/__main__.py
Dicas:
- No teste, chame a funcao de abertura com uma pasta de dados em `tmp_path` e uma trava ja tomada por outro `QLockFile`; substitua `QMessageBox.information` por um dublê.
- A mensagem exata esta em 7.1 (item Instancia unica).

### filepilot-v1-8-f3 Bloqueio de fechamento e falha de abertura do banco
Linhas da SPEC: .abt/SPEC.md L415-433
Arquivos:
- filepilot/ui/main_window.py (novo)
- filepilot/__main__.py (novo)
- tests/ui/test_close_and_db_error.py (novo)
Criterios de aceite:
- `closeEvent` com `organizing` verdadeiro ignora o fechamento e mostra "Aguarde a organização terminar para fechar."; com `organizing` falso fecha a conexao, libera a trava e aceita.
- Falha em `open_connection` mostra `QMessageBox.critical` com "Não foi possível acessar o histórico do FilePilot." e o programa termina com codigo 1.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_close_and_db_error.py -> exit 0
- grep deve casar: closeEvent em filepilot/ui/main_window.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Mensagens e codigos de saida em 7.1 (L415-433); a tabela de erros de 9 (L569-592) repete o caso de segunda instancia e de excecao inesperada.

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
