# filepilot-fix2-2 - Aba Organizar sai de carregando quando a leitura da pasta falha com erro do sistema
Epico: filepilot-fix2 | Ordem: 2 | Pontos: 2 | Depende de: filepilot-v1-9

## Objetivo

Um OSError na leitura da pasta leva a aba Organizar ao estado de erro com a mensagem de PASTA_ILEGIVEL, e os botoes Escolher pasta e Atualizar voltam a funcionar, em vez de a aba ficar presa em carregando com todos os botoes desabilitados.

## Contexto herdado

-

## Features

### filepilot-fix2-2-f1 Estado de erro da aba para OSError na leitura da pasta
Linhas da SPEC: .abt/SPEC.md L1126-1146
Arquivos:
- filepilot/ui/organize_tab.py L24-41
- filepilot/ui/organize_tab.py L84-141
- tests/ui/test_organize_tab_read_error.py (novo)
- tests/ui/test_organize_tab_folder.py L1-43
- tests/services/test_scanner_loop.py L10-30
Criterios de aceite:
- Com organize_tab_module.scan_folder trocado por monkeypatch para levantar PermissionError("acesso negado"), depois de tab.choose_folder() o tab.mode e erro e tab.summary.text() e exatamente "Não foi possível ler a pasta escolhida.", sem o texto acesso negado.
- Nesse estado tab.table.model.rowCount() e 0, tab.files e [] e tab.plan e None; Simular e Organizar ficam desabilitados e Escolher pasta e Atualizar ficam habilitados.
- Com a pasta ja listada e scan_folder passando a levantar OSError, tab.simulate() leva a tab.mode igual a erro com o mesmo estado; com scan_folder de volta ao servico real, tab.refresh() leva a tab.mode igual a listado com os arquivos da pasta.
- Com Path.resolve trocado por monkeypatch para levantar PermissionError so para a pasta escolhida (sem trocar scan_folder), tab.choose_folder() leva a tab.mode igual a erro.
- A constante _UNREADABLE de organize_tab e igual a scanner._MESSAGES["PASTA_ILEGIVEL"].
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/ui/test_organize_tab_read_error.py tests/ui/test_organize_tab_folder.py tests/ui/test_organize_tab_simulate.py -> exit 0
- parser: python -m py_compile filepilot/ui/organize_tab.py -> exit 0
- grep deve casar: except OSError em filepilot/ui/organize_tab.py
- grep deve casar: ler a pasta escolhida em filepilot/ui/organize_tab.py
- grep deve casar: ler a pasta escolhida em filepilot/services/scanner.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/ui/organize_tab.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/ui/organize_tab.py
Dicas:
- Hoje _read_folder (organize_tab.py L128-141) poe mode carregando (L131) e captura so FilePilotError (L136). Em carregando (_BUSY, L40) _update_buttons (L90-96) desabilita Escolher pasta, Atualizar, Simular e Organizar, e nada reabilita: o OSError escapa do slot.
- Acrescente except OSError depois do except FilePilotError, chamando self._show_error(FilePilotError("PASTA_ILEGIVEL", _UNREADABLE)) e devolvendo None. _show_error (L103-108) ja zera files e plan, limpa a tabela, mostra a mensagem e poe mode erro; em erro, Atualizar fica habilitado porque folder nao e None (L94).
- Defina _UNREADABLE = "Não foi possível ler a pasta escolhida." junto das outras constantes de texto (L31-35). O texto e o de PASTA_ILEGIVEL em scanner._MESSAGES (scanner.py L15); a SPEC repete o texto porque a camada ui nao importa o dicionario privado do scanner, e o teste compara os dois.
- Nunca exiba o texto bruto da excecao: ele fica so na cadeia de excecoes.
- Os tres chamadores de _read_folder (choose_folder via refresh, refresh e simulate, L145-167) ficam cobertos pela correcao no ponto unico; nao os altere.
- Padrao de teste: tests/ui/test_organize_tab_folder.py L1-43 (fixture conn, _tab, _pick, _folder_with); copie esses helpers. O monkeypatch de Path.resolve segue _fail_resolve_for em tests/services/test_scanner_loop.py L15-21: chame o resolve original para qualquer outro caminho, porque tmp_path tambem o usa.
- O PermissionError de Path.resolve passa por scanner._resolve_folder (scanner.py L52-61), que so converte laco e deixa subir os demais OSError (SPEC 27.2).
- Fora de escopo (SPEC 37.3): so OSError; outra excecao inesperada segue o tratamento de 6. Nao mude scanner.py nem a tabela de erros de 6.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix2/*.md
```
