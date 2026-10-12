# filepilot-fix-2 - Variavel de ambiente vazia nao torna a pasta atual protegida
Epico: filepilot-fix | Ordem: 2 | Pontos: 2 | Depende de: filepilot-fix-1

## Objetivo

SystemRoot, ProgramFiles e ProgramFiles(x86) definidas como vazias, ou so com espacos, valem como ausentes: scan_folder usa o padrao de 6.1 e a pasta atual deixa de ser tratada como protegida.

## Contexto herdado

Entregue por filepilot-fix-1 (commit 2d6bd08):

Artefatos criados:
- filepilot/services/scanner.py - alterado - `_resolve_folder(folder: Path) -> Path` (converte laco de atalhos em PASTA_INVALIDA) e `_is_protected(folder: Path, resolved: Path) -> bool` (recebe o caminho ja resolvido); constante `_WINERROR_CANT_RESOLVE = 1921`
- tests/services/test_scanner_loop.py - novo - testes do laco de atalhos (monkeypatch de `Path.resolve`, ELOOP, EACCES, laco real, link `up -> ..`)

Contratos:
- `scan_folder` em filepilot/services/scanner.py: ordem (1) caminho de rede `\\` sem resolver, (2) `_resolve_folder`, (3) `_is_protected(folder, resolved)`, (4) `folder.is_dir()`, (5) listagem. Armadilha: `_is_protected` nao chama mais `folder.resolve()`; o laco de variaveis de ambiente (`Path(os.environ.get(variable, default)).resolve()`) continua dentro dele e e o ponto do item atual.

Nomes decididos:
- `_resolve_folder` e o unico ponto que resolve a pasta escolhida; so o laco de atalhos vira PASTA_INVALIDA, outro OSError (como EACCES) continua subindo.

Padroes estabelecidos:
- Teste que troca `Path.resolve` por monkeypatch guarda o original (`_original_resolve`) e o chama para qualquer outro caminho, porque o fixture `tmp_path` tambem usa `resolve`.

filepilot-fix-1 ja entregou a conversao do laco de atalhos: NAO reimplementar `_resolve_folder` nem mexer na mensagem de PASTA_INVALIDA.

## Features

### filepilot-fix-2-f1 Raiz protegida lida por helper que ignora variavel vazia
Linhas da SPEC: .abt/SPEC.md L940-957
Arquivos:
- filepilot/services/scanner.py L19-60
- tests/services/test_scanner_protected.py L1-152
Criterios de aceite:
- Para cada uma das tres variaveis definida como "" e como "   ", com a pasta atual igual a tmp_path, scan_folder(tmp_path / "pasta") com um arquivo regular dentro devolve a lista e nao levanta PASTA_PROTEGIDA (6 casos).
- _protected_root("SystemRoot", r"C:\Windows") com a variavel vazia devolve Path(r"C:\Windows").resolve() e nao a pasta atual.
- O teste existente com SystemRoot apontando para uma pasta de tmp_path continua dando PASTA_PROTEGIDA para as pastas dentro dela.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_scanner_protected.py -> exit 0
- parser: python -m py_compile filepilot/services/scanner.py -> exit 0
- grep deve casar: def _protected_root em filepilot/services/scanner.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/scanner.py
Dicas:
- Hoje o laco de _is_protected faz Path(os.environ.get(variable, default)).resolve() (scanner.py L56): variavel vazia vira Path(""), que resolve para a pasta atual, e L57 (root in resolved.parents) protege tudo dentro dela.
- _protected_root(variable, default) le os.environ.get(variable); se o valor for None, "" ou so espacos (value.strip() == ""), usa default; devolve Path(value).resolve(). O laco sobre _PROTECTED_ENV (scanner.py L22-26) passa a chamar o helper para as tres variaveis.
- Valor relativo nao vazio, como windows, nao muda: continua resolvido a partir da pasta atual. Fora de escopo (ver 27.3).
- Este item depende de filepilot-fix-1 porque os dois alteram _is_protected: parta da assinatura _is_protected(folder, resolved) que o item anterior deixa.
- Nos testes use monkeypatch.setenv(variavel, "") e monkeypatch.chdir(tmp_path), parametrizados nas tres variaveis e nos dois valores; no Linux o padrao C:\Windows vira um caminho relativo dentro da pasta atual, o que nao protege a pasta de teste.
- Padrao de teste de pasta protegida: tests/services/test_scanner_protected.py L80-92 (setenv de SystemRoot para uma pasta de tmp_path).

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- Nenhum marcador de placeholder fora de bloco cercado (saida vazia):

```text
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix/*.md
```
