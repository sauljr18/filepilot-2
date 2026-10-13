# filepilot-fix3-3 - Laco de atalhos detectado tambem no Windows
Epico: filepilot-fix3 | Ordem: 3 | Pontos: 5 | Depende de: filepilot-fix2-4

## Objetivo

A recusa de pasta ou destino com laco de atalhos como PASTA_INVALIDA nao depende so de Path.resolve e e provada por testes que rodam no Windows sem serem pulados.

## Contexto herdado

-

## Features

### filepilot-fix3-3-f1 Helper de travessia de laco e ordem fixa em resolve_folder
Linhas da SPEC: .abt/SPEC.md L1317-1323
Arquivos:
- filepilot/services/scanner.py L1-14
- filepilot/services/scanner.py L30-62
- filepilot/services/planner.py L49-51
Criterios de aceite:
- Com `Path.resolve` trocado por `lambda self, strict=False: self` e um laco real, `resolve_folder` levanta `FilePilotError` com `code == "PASTA_INVALIDA"` e `__cause__ is None`.
- Com `Path.resolve` levantando `RuntimeError("Symlink loop")`, o `PASTA_INVALIDA` tem `__cause__` do tipo `RuntimeError` e `_crosses_symlink_loop` nao e chamado.
- `_crosses_symlink_loop` nunca levanta: `OSError` em `Path.is_symlink` ou em `os.readlink` devolve `False`.
- Passou de 40 saltos de link a travessia devolve `True`; link valido e caminho inexistente devolvem `False`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/services/test_planner_loop.py tests/services/test_scanner_loop.py -> exit 0
- testes: pytest tests/services/test_planner_loop.py tests/services/test_scanner_loop.py tests/services/test_planner_guard.py -> exit 0
- grep deve casar: def _crosses_symlink_loop em filepilot/services/scanner.py
- grep deve casar: os.readlink em filepilot/services/scanner.py
- grep nao deve casar: asyncio.new_event_loop em filepilot/services/scanner.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot/services/scanner.py
Dicas:
- Contrato canonico: `resolve_folder` em `filepilot/services/scanner.py` L52-61; ordem fixa de 45.4: primeiro o `resolve()` com o tratamento de 27.2 e 37.5 (`RuntimeError`, `OSError` com `errno.ELOOP` e `winerror` 1921 viram `PASTA_INVALIDA` com `raise ... from`); so se ele voltar sem erro, chama `_crosses_symlink_loop(folder)`.
- Algoritmo medido no Linux nesta especificacao: percorre o caminho absoluto componente a componente; `Path.is_symlink()` verdadeiro le `os.readlink`, soma um salto e segue pelo alvo (absoluto recomeca da raiz do alvo, relativo continua da pasta do link); `..` sobe um nivel; mais de 40 saltos devolve `True`. Devolve `True` para `link -> link` e para o ciclo `a -> b -> a`, e `False` para link valido e caminho inexistente.
- Alvo com prefixo `\\?\` devolvido pelo Windows e aceito como veio. Junction (`mklink /J`) fica fora de escopo (45.9).
- A hipotese de que o `Path.resolve()` do Python 3.12 no Windows trata o erro 1921 como inexistente vem da leitura do codigo de `ntpath`, nao foi medida; a prova e o job de testes em `windows-latest`.
- `planner._inside` (L49-51) ja chama `resolve_folder`; nao muda. `undo.py` passa a usar `resolve_folder` no item filepilot-fix3-4.
- Confirmar que `Path.is_symlink` e `os.readlink` existem na versao instalada (Python 3.12); nao use API de versao mais nova.

### filepilot-fix3-3-f2 Testes de laco com emulacao do Windows e erros do sistema
Linhas da SPEC: .abt/SPEC.md L1325-1335
Arquivos:
- tests/services/test_planner_loop.py L11-35
- tests/services/test_planner_loop.py L95-144
- tests/services/test_scanner_loop.py L1-30
- tests/services/test_scanner_loop.py L74-83
Criterios de aceite:
- `pytest tests/services/test_planner_loop.py tests/services/test_scanner_loop.py` termina com exit 0 no Linux e o codigo dos dois arquivos nao contem `Path.resolve nao detecta o laco nesta plataforma`.
- O helper `_symlink` dos dois arquivos faz `pytest.skip` quando o sistema recusa criar o link, exceto com `sys.platform == "win32"` e `GITHUB_ACTIONS` igual a `true`, onde faz `pytest.fail`.
- Os testes novos cobrem: emulacao do Windows com `build_plan` e com `scan_folder`, ciclo `a -> b -> a`, link valido dentro da pasta sem `PASTA_INVALIDA`, `__cause__` da ordem fixa, `os.readlink` com `OSError(errno.EACCES, ...)` e `Path.is_symlink` com `PermissionError`.
- O job de testes do GitHub Actions em `windows-latest` termina verde, sem teste de laco pulado.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests/services/test_planner_loop.py tests/services/test_scanner_loop.py -> exit 0
- testes: pytest tests/services/test_planner_loop.py tests/services/test_scanner_loop.py -> exit 0
- grep nao deve casar: nao detecta o laco nesta plataforma em tests/services/test_planner_loop.py
- grep deve casar: GITHUB_ACTIONS em tests/services/test_planner_loop.py
- grep deve casar: GITHUB_ACTIONS em tests/services/test_scanner_loop.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em tests/services/test_planner_loop.py
Dicas:
- Padrao a seguir: `tests/services/test_planner_loop.py` L16-29 (`_fail_resolve_for` e `_symlink`) e `tests/services/test_scanner_loop.py` L74-83 (`test_laco_real_de_atalhos_vira_pasta_invalida`, ciclo a -> b -> a).
- A emulacao do Windows troca `Path.resolve` com `monkeypatch.setattr(Path, "resolve", lambda self, strict=False: self)`; o laco real e `folder / "Documentos"` apontando para si mesmo.
- Previsao de falha, registrada no relatorio: se `windows-latest` nao detectar o laco, o teste real falha no job do GitHub Actions e o item nao esta concluido; nao ha comando local que prove isso no Linux.
- Regra de 45.7: toda fixture com yield em arquivo novo ou alterado e anotada `Iterator[tipo]`.

## Gates do item

- typecheck: python -m mypy --platform win32 filepilot tests/services/test_planner_loop.py tests/services/test_scanner_loop.py -> exit 0 (o comando completo de 45.7 so passa depois do item filepilot-fix3-1)
- testes: pytest -> exit 0
- placeholder provisorio de secao fora de bloco cercado: o awk abaixo termina com saida vazia

```bash
awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-fix3/*.md
```
