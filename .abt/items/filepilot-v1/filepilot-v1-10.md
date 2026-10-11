# filepilot-v1-10 - Aba Organizar: execucao com barra de progresso
Epico: filepilot-v1 | Ordem: 10 | Pontos: 5 | Depende de: filepilot-v1-5,filepilot-v1-6,filepilot-v1-9

## Objetivo
O botao Organizar executa o plano em thread de trabalho com barra de progresso, conferencia da simulacao exibida e resumo de movidos e falhas, sem travar a janela.

## Contexto herdado
-

## Features

### filepilot-v1-10-f1 OrganizeWorker e barra de progresso
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_worker.py (novo)
- filepilot/ui/organize_tab.py (novo)
- tests/ui/test_organize_worker.py (novo)
Criterios de aceite:
- Organizar roda `OrganizeWorker` em `QThread`; a barra tem faixa de 0 a N, texto "%v de %m arquivos" e termina em 100% com o resumo "Concluído: X movidos, Y falhas.".
- O worker emite `progress(done, total, filename)`, `finished(result)` e `failed(code, message)`, ligados ao `progress_callback` do servico.
- Terminado o worker, a pasta e relida, `mode` volta a `listado` e a aba emite `organization_finished` com o id da organizacao.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_worker.py -> exit 0
- parser: python -m py_compile filepilot/ui/organize_worker.py -> exit 0
- grep deve casar: QThread em filepilot/ui/organize_worker.py
- grep deve casar: %v de %m arquivos em filepilot/ui/organize_tab.py
Dicas:
- O servico `organize` nunca importa PySide6; so o worker liga o `progress_callback` a um sinal Qt (SPEC 3.2).
- Teste o worker pelos sinais com `qtbot.waitSignal`, sem janela visivel.
- Confirme na versao PySide6 6.12.0 a assinatura de `Signal` e de `qtbot.waitSignal`.

### filepilot-v1-10-f2 Conferencia da simulacao antes de organizar
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_tab.py (novo)
- tests/ui/test_organize_confirm.py (novo)
Criterios de aceite:
- Organizar relê a pasta e recalcula o plano com as regras atuais; com `mode` igual a `simulado` e plano novo diferente do exibido (compara `source_path`, `destination_path` e `rule_name`), nada e movido, a tabela mostra o plano novo e aparece "A pasta mudou desde a simulação. Confira a nova simulação e clique em Organizar de novo.".
- Com `mode` igual a `listado` (sem simulacao) ou plano igual ao exibido, a organizacao e executada.
- Plano recalculado vazio nao executa, mostra "Não há operações para executar." e desabilita Organizar.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_confirm.py -> exit 0
- grep deve casar: A pasta mudou desde a simulação em filepilot/ui/organize_tab.py
Dicas:
- Fluxo 8.1 (L524-540): sem simular, Organizar relê a pasta, recalcula e executa.
- Compare listas de tuplas `(source_path, destination_path, rule_name)` na mesma ordem.

### filepilot-v1-10-f3 Estados durante a organizacao e erro inesperado
Linhas da SPEC: .abt/SPEC.md L434-458
Arquivos:
- filepilot/ui/organize_tab.py (novo)
- filepilot/ui/main_window.py (novo)
- tests/ui/test_organize_states.py (novo)
Criterios de aceite:
- Durante a organizacao Simular, Organizar, Atualizar e Escolher pasta ficam desabilitados e `MainWindow.organizing` e verdadeiro; ao fim todos voltam e `organizing` e falso.
- `failed(code, message)` mostra `QMessageBox.critical` com a mensagem e `mode` vai para `erro`; excecao inesperada mostra "Ocorreu um erro inesperado. Tente de novo." e a janela continua aberta.
- Fechar a janela durante a organizacao continua bloqueado pelo `closeEvent` do item filepilot-v1-8.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui/test_organize_states.py -> exit 0
- grep deve casar: organizing em filepilot/ui/organize_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- A trava `OPERATION_LOCK` do servico impede a segunda organizacao; a interface so desabilita botoes (SPEC 6.3, ultimo item).
- Os textos de erro vem da tabela de codigos da secao 6 (L232-259).

## Gates do item
- typecheck: mypy . --no-error-summary -> exit 0
- testes: QT_QPA_PLATFORM=offscreen pytest tests/ui -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
