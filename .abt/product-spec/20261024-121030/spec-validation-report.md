# Relatorio de Validacao da SPEC - Round 1/3

**Data:** 2026-10-24
**Modo:** delta focado
**Secao auditada:** ## 56. Opcao --help na linha de comando

## Resumo

| Categoria | Encontrados | Corrigidos auto | Requer decisao |
|---|---|---|---|
| Erros | 0 | 0 | 0 |
| Inconsistencias | 0 | 0 | 0 |
| Scope Creep | 0 | 0 | 0 |
| Lacunas vs. PRD | 0 | 0 | 0 |
| Definicoes Vagas | 0 | 0 | 0 |
| Inconsistencia de Nomenclatura | 0 | 0 | 0 |
| Total | 0 | 0 | 0 |

Conferencias feitas nesta rodada (fonte de requisitos: o escopo de `discovery-notes.md`):

- Erros: os 5 itens do escopo (`--help`, `-h`, texto de uso, demais argumentos, sem saida padrao) tem comportamento descrito em 56.3 e teste em 56.4; nenhum diverge do escopo.
- Inconsistencias: 56.1, 56.2, 56.3 e 56.4 descrevem a mesma comparacao exata e o mesmo texto; o alinhamento declarado confere (descricoes na coluna 15: dois espacos + `--help, -h` + dois espacos = dois espacos + `--version` + tres espacos).
- Scope Creep: nenhum elemento sem origem; a linha `opções:` e o alinhamento, e `--help`/`-h` na mesma linha, tem `[DECISAO: ...]` e linha na matriz.
- Lacunas: os 5 itens do escopo, os 4 itens de fora de escopo e a metrica tem linha na matriz conferida contra 56.1 a 56.4.
- Definicoes Vagas: texto de uso literal (bloco `text` de 56.3), saida exata, codigo de saida e testes com valores esperados.
- Nomenclatura: `_USAGE`, `main()`, `app_main`, `QApplication`, `default_data_dir` e `open_main_window` com os nomes do codigo.
- Codigo conferido: `main()` em `filepilot/__main__.py:63` a `:73`, desvio de `--version` em `:64` a `:66`, `sys.exit(main())` em `:76` e `:77`; `packaging/filepilot.spec:34` com `console=False`; estilo e falsos de `tests/test_version_cli.py`. Secoes citadas existem: 7.1, 13, 17.3, 19.2, 37.4, 45.7, 54.1, 54.2.
- Itens existentes: `grep -l 'test_help_cli\|_USAGE' .abt/items/*/*.md` sem resultado; nenhum item ja cita o que a secao cria.
- Errata: `{acrescenta: 54.1}` aplicada pelo `abt spec vigente` na fase anterior; 54.1 nao foi editada.

## Correcoes Aplicadas Automaticamente

Nenhuma correcao necessaria.

## Itens Aguardando Decisao

Nenhum item aguardando decisao.

## Decisoes registradas

- `[DECISAO: aprovada no enriquecimento; sugestao 1]` em 56.3: saida padrao que nao codifica `ã` e `õ` sai com 1, limite aceito sem teste (decisao da pessoa, nao e achado). Conferido: o CI roda em `windows-latest` (`.github/workflows/tests.yml:9`) sem `PYTHONIOENCODING`.
- `[DECISAO: a linha "opções:" e o alinhamento das descricoes sao forma escolhida aqui; ...]` (Gabriel), em 56.3: isenta de Scope Creep; nao contradiz o escopo (primeira linha, portugues e uma linha por opcao mantidos).
- `[DECISAO: -h e o nome curto de --help; uma linha por opcao conta as duas como uma opcao]` (Gabriel), em 56.3: isenta de Scope Creep; nao contradiz o escopo.
- Nenhuma linha `CORTADO` (modo delta, sem decisao de stack).

## Status apos Round 1

APROVAVEL: SPEC sem erros, inconsistências ou lacunas; pronta para aprovação.

Retorno: validacao-spec
