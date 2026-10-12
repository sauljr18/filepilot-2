# filepilot-fix2-4 - Planejamento com laco de atalhos vira PASTA_INVALIDA
Epico: filepilot-fix2 | Ordem: 4 | Pontos: 3 | Depende de: filepilot-fix-1,filepilot-v1-4

## Objetivo

O planejamento de uma pasta ou de um destino com laco de atalhos levanta FilePilotError com code PASTA_INVALIDA e a mensagem de 6, em vez de RuntimeError (erro interno), sem bloquear o plano por laco em subpasta de destino que nenhum arquivo usa.

## Contexto herdado

-

## Features

### filepilot-fix2-4-f1 Resolucao publica de laco de atalhos usada pelo planejamento
Linhas da SPEC: .abt/SPEC.md L1169-1194
Arquivos:
- filepilot/services/scanner.py L52-61
- filepilot/services/scanner.py L111-128
- filepilot/services/planner.py L1-50
- filepilot/services/planner.py L64-96
- tests/services/test_planner_loop.py (novo)
- tests/services/test_planner_guard.py L1-48
- tests/services/test_scanner_loop.py L10-30
Criterios de aceite:
- Com Path.resolve trocado por monkeypatch para levantar RuntimeError("Symlink loop") so para folder/Documentos/a.pdf, build_plan(folder, [a.pdf], []) levanta FilePilotError com code PASTA_INVALIDA, message igual a "A pasta escolhida não existe ou não é uma pasta." e sem o texto Symlink loop.
- Com OSError de errno.ELOOP o resultado e PASTA_INVALIDA; com OSError de errno.EACCES na resolucao continua sendo OSError.
- Laco real em folder/Documentos apontando para si mesmo (Path.symlink_to, com pytest.skip se o sistema recusar) da PASTA_INVALIDA e a arvore da pasta fica identica.
- Laco real em folder/Imagens com a.pdf na pasta devolve o plano com a operacao do PDF para Documentos e sem erro; destino fora da pasta continua DESTINO_FORA_DA_PASTA.
- Todos os testes de tests/services/test_scanner_loop.py e tests/services/test_planner_guard.py passam sem alteracao.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_planner_loop.py tests/services/test_planner_guard.py tests/services/test_planner.py tests/services/test_scanner_loop.py -> exit 0
- parser: python -m py_compile filepilot/services/planner.py filepilot/services/scanner.py -> exit 0
- grep deve casar: def resolve_folder em filepilot/services/scanner.py
- grep deve casar: resolve_folder em filepilot/services/planner.py
- grep nao deve casar: _resolve_folder em filepilot/services/scanner.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/services/planner.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/planner.py
Dicas:
- Hoje planner._inside (planner.py L48-49) chama destination.resolve() e folder.resolve() sem tratamento; build_plan o chama em L76 e L85. Medicao da SPEC 37.5 (Python 3.12.3): com Documentos apontando para si mesmo, resolve() do destino e da pasta levanta RuntimeError("Symlink loop ...").
- Renomeie scanner._resolve_folder (scanner.py L52) para resolve_folder (mesmo corpo e comportamento de 27.2: RuntimeError, OSError com errno.ELOOP e OSError com winerror 1921 viram PASTA_INVALIDA com raise ... from exc; outro OSError continua subindo) e troque a chamada em scan_folder (L115). Nenhum teste nem modulo cita o nome antigo (conferido em filepilot e tests).
- Em planner.py importe com from filepilot.services.scanner import resolve_folder e escreva _inside como resolve_folder(destination).is_relative_to(resolve_folder(folder)). Nao ha ciclo: scanner.py nao importa planner.
- A mensagem de PASTA_INVALIDA e o texto fixo de 6, vindo do scanner; nunca o texto da excecao original.
- So o destino de arquivo com categoria ou regra e resolvido: build_plan ja pula os arquivos sem alvo antes de chamar _inside (planner.py L70-73). Nao resolva as subpastas de destino de antemao, senao um laco em Imagens sem imagem na pasta bloquearia o plano.
- Padrao de teste com monkeypatch de Path.resolve: tests/services/test_scanner_loop.py L15-21 (_fail_resolve_for chama o resolve original para outro caminho). Construa o alvo como folder / "Documentos" / "a.pdf". Padrao de plano: tests/services/test_planner_guard.py L10-18 (_file e _rule).
- Fora de escopo (SPEC 37.6): o laco de atalhos dentro do desfazer (undo.py L47 e L93) nao e corrigido aqui.

### filepilot-fix2-4-f2 Teste da aba Organizar com laco no destino do planejamento
Linhas da SPEC: .abt/SPEC.md L1169-1194
Arquivos:
- tests/ui/test_organize_tab_plan_loop.py (novo)
- tests/ui/test_organize_tab_folder.py L1-43
- filepilot/ui/organize_tab.py L128-141
Criterios de aceite:
- Pasta com a.pdf e Path.resolve trocado por monkeypatch para levantar RuntimeError("Symlink loop") so para folder/Documentos/a.pdf: tab.choose_folder() leva a tab.mode igual a erro.
- Nesse estado tab.summary.text() e exatamente "A pasta escolhida não existe ou não é uma pasta.".
- O arquivo e proprio deste item: nao importa nem depende de tests/ui/test_organize_tab_read_error.py.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/ui/test_organize_tab_plan_loop.py tests/ui/test_organize_tab_folder.py -> exit 0
- grep deve casar: não existe ou não é uma pasta em tests/ui/test_organize_tab_plan_loop.py
- grep nao deve casar: test_organize_tab_read_error em tests/ui/test_organize_tab_plan_loop.py
Dicas:
- Copie _tab, _pick, _folder_with e a fixture conn de tests/ui/test_organize_tab_folder.py L1-43, em vez de importa-los, para o item nao depender de outro arquivo de teste.
- A aba ja captura FilePilotError em _read_folder (organize_tab.py L136-138) e mostra a mensagem em modo erro (L103-108): este teste so prova o caminho; nao altere organize_tab.py neste item.
- O monkeypatch de Path.resolve deve chamar o original para qualquer outro caminho (tmp_path usa resolve).

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix2/*.md
```
