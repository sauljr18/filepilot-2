# filepilot-fix-1 - Laco de atalhos na leitura da pasta vira PASTA_INVALIDA
Epico: filepilot-fix | Ordem: 1 | Pontos: 2 | Depende de: filepilot-v1-2

## Objetivo

scan_folder levanta FilePilotError com code PASTA_INVALIDA, e nao erro interno, quando a resolucao da pasta escolhida entra em laco de atalhos. A mensagem e sempre o texto fixo de 6, nunca o texto da excecao original.

## Contexto herdado

-

## Features

### filepilot-fix-1-f1 Resolucao da pasta que converte laco de atalhos em PASTA_INVALIDA
Linhas da SPEC: .abt/SPEC.md L919-939
Arquivos:
- filepilot/services/scanner.py L36-102
- tests/services/test_scanner_loop.py (novo)
- tests/services/test_scanner_protected.py L1-50
Criterios de aceite:
- Com Path.resolve trocado por monkeypatch para levantar RuntimeError("Symlink loop") na pasta escolhida, scan_folder levanta FilePilotError com code PASTA_INVALIDA, message igual ao texto de 6 ("A pasta escolhida não existe ou não é uma pasta.") e sem o texto Symlink loop.
- Com OSError de errno.ELOOP na resolucao o resultado e PASTA_INVALIDA; com OSError de errno.EACCES continua sendo OSError (so o laco e convertido).
- Laco real, a apontando para b e b apontando para a, criado com Path.symlink_to, da PASTA_INVALIDA; o teste usa pytest.skip se o sistema recusar criar o link.
- Pasta valida com um link up apontando para .. dentro dela continua listando so os arquivos regulares.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_scanner_loop.py tests/services/test_scanner_protected.py -> exit 0
- parser: python -m py_compile filepilot/services/scanner.py -> exit 0
- grep deve casar: def _resolve_folder em filepilot/services/scanner.py
- grep deve casar: winerror em filepilot/services/scanner.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/scanner.py
Dicas:
- Hoje a resolucao esta em _is_protected (scanner.py L52, resolved = folder.resolve()). Crie o helper _resolve_folder(folder), que devolve folder.resolve() e converte RuntimeError, OSError com errno ELOOP e OSError com winerror 1921 em FilePilotError PASTA_INVALIDA com raise ... from exc.
- Leia winerror com getattr(exc, "winerror", None), como a funcao _failure_text de filepilot/services/organizer.py, para o mypy passar em qualquer plataforma.
- A assinatura passa a ser _is_protected(folder, resolved). Nenhum teste existente chama _is_protected direto (conferido em tests/), entao a mudanca nao quebra teste.
- Ordem das verificacoes em scan_folder: caminho de rede que comeca com duas barras invertidas (sem resolver), _resolve_folder, _is_protected, folder.is_dir(), listagem. O laco nunca chega a _is_protected.
- Ao trocar Path.resolve por monkeypatch, chame o original para qualquer outro caminho: o fixture tmp_path tambem usa resolve.
- Padrao de teste com monkeypatch em Path: tests/services/test_scanner_protected.py L36 (monkeypatch.setattr(Path, "iterdir", ...)).
- O ponto de falha e o do enunciado: pasta que e, ou esta dentro de, um laco de atalhos. Ver 6.1 para as demais regras de scan_folder, que nao mudam.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix/*.md
```
