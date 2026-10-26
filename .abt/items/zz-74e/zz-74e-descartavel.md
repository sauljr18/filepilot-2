# zz-74e-descartavel - Arquivo de prova rascunho/74e-prova.md do smoke 74e
Epico: zz-74e | Ordem: 1 | Pontos: 1 | Depende de: -

## Objetivo

O repositorio passa a ter `rascunho/74e-prova.md` com exatamente a linha `prova do smoke 74e` seguida de `\n` (19 bytes, LF no arquivo versionado), e nenhum arquivo de produto, de teste ou de configuracao muda.

## Contexto herdado

-

## Features

### zz-74e-descartavel-f1 Arquivo rascunho/74e-prova.md com a linha de prova
Âncoras da SPEC: 60.2=ca4d3b5c2b6b, 60.1=d05810934e3e
Arquivos:
- rascunho/74e-prova.md (novo)
Criterios de aceite:
- `git show HEAD:rascunho/74e-prova.md | cmp - <(printf 'prova do smoke 74e\n')` sai com 0 na branch do item (60.2).
- `git diff --name-only origin/main...HEAD` na branch do item lista `rascunho/74e-prova.md` e, alem dele, no maximo `.abt/reviews/zz-74e-descartavel.md` (ERR-001, Opcao A, do relatorio de validacao da SPEC).
- `git diff --name-only origin/main...HEAD -- filepilot tests packaging pyproject.toml .github .gitignore` nao imprime nada (60.1).
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot tests -> exit 0
- testes: pytest -> exit 0
- grep deve casar: ^prova do smoke 74e$ em rascunho/74e-prova.md
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em rascunho/74e-prova.md
Dicas:
- Crie a pasta e o arquivo com `printf 'prova do smoke 74e\n' > rascunho/74e-prova.md`: uma linha, quebra de linha final, sem BOM e sem linha em branco a mais (60.2).
- No Windows, confira o conteudo pelo arquivo versionado (`git show HEAD:...`), nao pela copia de trabalho: o repositorio nao tem `.gitattributes`, e com `core.autocrlf=true` a copia fica com CRLF (60.2).
- Nenhum codigo le o arquivo: `pyproject.toml:23` empacota so `filepilot*` e o `mypy` do CI (`.github/workflows/tests.yml:22`) confere so `filepilot` e `tests`; typecheck e testes so precisam continuar como hoje.
- Fora do item (60.1): codigo, testes, `.gitattributes`, `pyproject.toml`, `.github/` e qualquer outro arquivo.

## Gates do item

- python -m mypy --platform win32 filepilot tests -> exit 0, `Success: no issues found`
- pytest -> exit 0
- `git show HEAD:rascunho/74e-prova.md | cmp - <(printf 'prova do smoke 74e\n')` -> exit 0
- awk do placeholder sobre `.abt/SPEC.md` e `.abt/items/zz-74e/*.md` com saida vazia
