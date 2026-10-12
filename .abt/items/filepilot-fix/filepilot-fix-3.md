# filepilot-fix-3 - Ordem estavel da lista de arquivos com nomes que so diferem por maiuscula
Epico: filepilot-fix | Ordem: 3 | Pontos: 1 | Depende de: filepilot-v1-2

## Objetivo

scan_folder devolve a mesma ordem em qualquer execucao quando dois nomes so diferem por maiuscula e minuscula, desempatando pelo nome exato.

## Contexto herdado

-

## Features

### filepilot-fix-3-f1 Chave de ordenacao total com desempate pelo nome exato
Linhas da SPEC: .abt/SPEC.md L958-975
Arquivos:
- filepilot/services/scanner.py L88-102
- tests/services/test_scanner_order.py (novo)
Criterios de aceite:
- Com Path.iterdir trocado por monkeypatch para devolver b.txt, a.txt e A.txt em qualquer das 6 permutacoes, a lista tem os nomes A.txt, a.txt e b.txt, nessa ordem.
- Foto.JPG, foto.jpg e FOTO.jpg dao a mesma lista nas 6 permutacoes de entrada.
- Nomes que ja diferiam em casefold (beta.txt e Alfa.txt) continuam em ordem alfabetica sem diferenciar maiusculas.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_scanner_order.py tests/services/test_scanner.py -> exit 0
- parser: python -m py_compile filepilot/services/scanner.py -> exit 0
- grep deve casar: item.name.casefold(), item.name em filepilot/services/scanner.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/scanner.py
Dicas:
- Hoje a chave e files.sort(key=lambda item: item.name.casefold()) (scanner.py L101). Troque por (item.name.casefold(), item.name): a ordem entre nomes que ja diferiam em casefold nao muda, e o desempate pela ordem dos pontos de codigo coloca A.txt antes de a.txt.
- NAO crie A.txt e a.txt no disco nos testes: os dois nomes colidem no runner windows-latest. Troque Path.iterdir (monkeypatch.setattr(Path, "iterdir", ...)) e scanner._scan_entry (devolve um ScannedFile sintetico com path, name, extension e size_bytes); a pasta continua sendo um tmp_path real para passar em is_dir e na checagem de pasta protegida.
- scanner._scan_entry e uma funcao de modulo buscada na hora da chamada em scan_folder, entao o monkeypatch vale. Padrao de teste que troca iterdir: tests/services/test_scanner_protected.py L36.
- Use itertools.permutations para as 6 permutacoes dos tres nomes.
- Ver 6.1 para a regra de ordenacao que esta feature substitui.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix/*.md
```
