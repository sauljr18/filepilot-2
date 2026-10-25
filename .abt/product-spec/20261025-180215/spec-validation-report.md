# Relatorio de Validacao da SPEC - Round 2/3

**Data:** 2026-10-25
**Modo:** delta focado
**Secao auditada:** ## 58. Opcao -V na linha de comando [DELTA 2026-10-25, python -m filepilot -V]

Auditoria cruzada da secao 58 contra o escopo de `discovery-notes.md`, contra as secoes que ela cita (54.1, 54.2, 56.1, 56.3, 56.4) e contra o codigo real (`filepilot/__main__.py`, `filepilot/__init__.py`, `pyproject.toml`, `tests/test_version_cli.py`, `tests/test_help_cli.py`). O Round 1 achou 2 itens corrigiveis sozinho, aplicados; o Round 2 reauditou a secao corrigida e nao achou nada novo. Skill ignorada por nao ser da stack: `vuetify-sneat-ui-patterns` (o manifesto mostra PySide6, `pyproject.toml:11`).

## Resumo

| Categoria | Encontrados | Corrigidos auto | Requer decisao |
|---|---|---|---|
| Erros | 1 | 1 | 0 |
| Inconsistencias | 0 | 0 | 0 |
| Scope Creep | 0 | 0 | 0 |
| Lacunas vs. PRD | 0 | 0 | 0 |
| Definicoes Vagas | 1 | 1 | 0 |
| Inconsistencia de Nomenclatura | 0 | 0 | 0 |
| Total | 2 | 2 | 0 |

## Correcoes Aplicadas Automaticamente

### ERR-001: Fim de main() citado na linha errada

- **Problema:** 58.1 dizia que `main()` vai de `filepilot/__main__.py:69` a `:83`; a ultima linha de `main()` e `return app.exec()`, na `:82` (a `:83` e linha em branco, e `if __name__ == "__main__":` esta na `:85`).
- **Referencia:** item do escopo 1 de `discovery-notes.md` (desvio do `-V` em `main()`).
- **Localizacao na SPEC:** 58.1, primeiro paragrafo.
- **Evidencia:** `filepilot/__main__.py:69` (`def main() -> int:`), `:82` (`return app.exec()`), `:85` e `:86`.
- **Correcao aplicada:** `filepilot/__main__.py:69` a `:83` -> `filepilot/__main__.py:69` a `:82`.

### VAG-001: ids dos casos parametrizados nao definidos

- **Problema:** 58.6 mandava parametrizar os testes com `--version` e `-V` e acrescentar casos ao teste 3 sem dizer os ids; o teste 3 ja usa `ids=["sem", "extra"]` (`tests/test_version_cli.py:63`), e um `ids` com tamanho diferente da lista quebra a coleta do pytest.
- **Referencia:** item do escopo 1 de `discovery-notes.md` (metrica verificavel por teste).
- **Localizacao na SPEC:** 58.6, itens 1 e 2.
- **Evidencia:** `tests/test_version_cli.py:62` e `:63`; `tests/test_help_cli.py:45` (`ids=["longo", "curto"]`).
- **Correcao aplicada:** item 1 ganhou `(ids=["longo", "curto"], como em tests/test_help_cli.py)`; item 2 ganhou `(ids curto-extra e minuscula, depois de sem e extra)`.

## Itens Aguardando Decisao

Nenhum item aguardando decisao. `### 58.7 Pendencias para decisao` segue sem pendencias.

## Decisoes registradas

- `[DECISAO: mesma regra de comparacao exata de 54.2; o pedido cobre -V como argumento unico]` (58.4): do Gabriel, isenta de Scope Creep; coerente com o fora de escopo de `discovery-notes.md` (`-V` com outros argumentos segue o caminho de hoje).
- `[DECISAO: mesma forma da linha --help, -h; uma linha por opcao conta o nome longo e o curto como uma opcao]` (58.5): do Gabriel, isenta de Scope Creep; cumpre o item do escopo 2 (o `--help` cita `-V`).
- `[DECISAO: o alinhamento de 56.3 mantido com o nome mais longo]` (58.5): do Gabriel, isenta de Scope Creep; conferido no literal: as duas descricoes comecam na mesma coluna.
- `[DECISAO: aprovada no enriquecimento; sugestao 1]` (58.5, limite de codificacao): decisao da pessoa vinda de 56.3, mantida como estava no trecho substituido; nao e achado.
- Erratas: `abt spec vigente` aplica as 4 marcas da secao (`acrescenta` 54.1, 56.1 e 54.2; `substitui` 56.3). Os itens ja entregues `filepilot-version-1` (54.1, 54.2) e `filepilot-help-1` (56.1, 56.3) citam essas ancoras e ficam com o sha antigo; os dois ja estao integrados (§55 e §57), e a ancora 54.1 ja tinha mudado pela errata 56.2 (sha `08ed0d63bb9d` no item, `a83704eced2a` antes desta secao).

## Status apos Round 2

APROVAVEL: SPEC sem erros, inconsistencias ou lacunas; pronta para aprovacao.

Retorno: validacao-spec
