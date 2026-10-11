# Relatorio do Detalhe dos Itens: filepilot-v1

**Data:** 2026-10-11
**Modo:** completo
**Stack:** Python 3.12 com PySide6 6.12.0, SQLite, pytest e PyInstaller (comandos da tabela por stack do Passo 3; `.abt/WORKFLOW.md` nao traz secao de comandos)

## 1. Secao da SPEC

Modo completo: secoes `## 1.` a `## 15.` de `.abt/SPEC.md` (745 linhas no total, contadas pelo awk do mapa). A `## 16. Traceability Matrix` e a lista de requisitos e nao e alvo de `Linhas da SPEC`. Maior subsecao de conteudo: 5.3, com 44 linhas; nenhuma passa de 60.

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-v1-1 | Fundacao: projeto, dominio, banco e CI Windows | 5 | - | 4 |
| 2 | filepilot-v1-2 | Leitura da pasta e pastas protegidas | 4 | filepilot-v1-1 | 2 |
| 3 | filepilot-v1-3 | Servico de regras personalizadas | 5 | filepilot-v1-1 | 3 |
| 4 | filepilot-v1-4 | Planejamento das operacoes e conflitos de nome | 6 | filepilot-v1-1,filepilot-v1-2 | 3 |
| 5 | filepilot-v1-5 | Organizacao com historico por arquivo | 5 | filepilot-v1-1,filepilot-v1-4 | 3 |
| 6 | filepilot-v1-6 | Verificacoes de destino e textos de falha | 3 | filepilot-v1-5 | 3 |
| 7 | filepilot-v1-7 | Historico e desfazer a ultima organizacao | 6 | filepilot-v1-1,filepilot-v1-5 | 3 |
| 8 | filepilot-v1-8 | Janela principal, abas e instancia unica | 3 | filepilot-v1-1 | 3 |
| 9 | filepilot-v1-9 | Aba Organizar: pasta, lista e simulacao | 5 | filepilot-v1-2,filepilot-v1-3,filepilot-v1-4,filepilot-v1-8 | 3 |
| 10 | filepilot-v1-10 | Aba Organizar: execucao com barra de progresso | 5 | filepilot-v1-5,filepilot-v1-6,filepilot-v1-9 | 3 |
| 11 | filepilot-v1-11 | Aba Historico e desfazer na interface | 5 | filepilot-v1-7,filepilot-v1-9,filepilot-v1-10 | 3 |
| 12 | filepilot-v1-12 | Aba Regras e dialogo de regra | 5 | filepilot-v1-3,filepilot-v1-8 | 3 |
| 13 | filepilot-v1-13 | Executavel Windows com PyInstaller e CI | 3 | filepilot-v1-10,filepilot-v1-11,filepilot-v1-12 | 2 |

Total: 13 itens, 60 pontos, 38 features. Detalhes em `.abt/items/filepilot-v1/`.

## 3. Linhas da SPEC por feature

| Feature | Linhas da SPEC | Subsecao |
|---|---|---|
| filepilot-v1-1-f1 | L95-119 | 4. Stack e dependencias |
| filepilot-v1-1-f2 | L216-231 | 5.5 Categorias padrao |
| filepilot-v1-1-f3 | L143-186 | 5.3 Tabelas organizations e operations |
| filepilot-v1-1-f4 | L629-634 | 13. Compatibilidade / Migracao |
| filepilot-v1-2-f1 | L260-275 | 6.1 scanner.scan_folder |
| filepilot-v1-2-f2 | L260-275 | 6.1 scanner.scan_folder |
| filepilot-v1-3-f1 | L351-376 | 6.6 rules |
| filepilot-v1-3-f2 | L351-376 | 6.6 rules |
| filepilot-v1-3-f3 | L187-215 | 5.4 Tabelas rules e rule_extensions |
| filepilot-v1-4-f1 | L276-291 | 6.2 planner.build_plan |
| filepilot-v1-4-f2 | L276-291 | 6.2 planner.build_plan |
| filepilot-v1-4-f3 | L276-291 | 6.2 planner.build_plan |
| filepilot-v1-5-f1 | L292-313 | 6.3 organizer.simulate e organizer.organize |
| filepilot-v1-5-f2 | L292-313 | 6.3 organizer.simulate e organizer.organize |
| filepilot-v1-5-f3 | L292-313 | 6.3 organizer.simulate e organizer.organize |
| filepilot-v1-6-f1 | L377-402 | 6.7 Verificacoes de destino e textos de falha por arquivo |
| filepilot-v1-6-f2 | L377-402 | 6.7 Verificacoes de destino e textos de falha por arquivo |
| filepilot-v1-6-f3 | L597-622 | 11. Seguranca / Permissoes |
| filepilot-v1-7-f1 | L314-334 | 6.4 history |
| filepilot-v1-7-f2 | L314-334 | 6.4 history |
| filepilot-v1-7-f3 | L335-350 | 6.5 undo.undo_last |
| filepilot-v1-8-f1 | L415-433 | 7.1 MainWindow |
| filepilot-v1-8-f2 | L415-433 | 7.1 MainWindow |
| filepilot-v1-8-f3 | L415-433 | 7.1 MainWindow |
| filepilot-v1-9-f1 | L434-458 | 7.2 OrganizeTab |
| filepilot-v1-9-f2 | L459-478 | 7.3 FileTableView |
| filepilot-v1-9-f3 | L434-458 | 7.2 OrganizeTab |
| filepilot-v1-10-f1 | L434-458 | 7.2 OrganizeTab |
| filepilot-v1-10-f2 | L434-458 | 7.2 OrganizeTab |
| filepilot-v1-10-f3 | L434-458 | 7.2 OrganizeTab |
| filepilot-v1-11-f1 | L479-498 | 7.4 HistoryTab |
| filepilot-v1-11-f2 | L479-498 | 7.4 HistoryTab |
| filepilot-v1-11-f3 | L434-458 | 7.2 OrganizeTab |
| filepilot-v1-12-f1 | L499-521 | 7.5 RulesTab e RuleEditorDialog |
| filepilot-v1-12-f2 | L499-521 | 7.5 RulesTab e RuleEditorDialog |
| filepilot-v1-12-f3 | L499-521 | 7.5 RulesTab e RuleEditorDialog |
| filepilot-v1-13-f1 | L95-119 | 4. Stack e dependencias |
| filepilot-v1-13-f2 | L635-645 | 14. Plano de entrega |

## 4. Checklist mecanico

1. Um detalhe por item em `.abt/items/filepilot-v1/<item_id>.md`, com linha 1, cabecalho e as secoes `## Objetivo`, `## Contexto herdado`, `## Features` e `## Gates do item`: ok (13 de 13).
2. `Ordem`, `Pontos` e `Depende de` iguais aos do `itens.md`, pontos de 1 a 8: ok.
3. Toda feature com `Linhas da SPEC`, `Arquivos:`, de 2 a 5 criterios, `Verificacao:` com typecheck e `Dicas:`: ok (38 features).
4. Todo intervalo com `1 <= a <= b <= 745`, no maximo 60 linhas e dentro de subsecao de conteudo (nenhum na matriz): ok.
5. Ids no formato `^[a-z0-9][a-z0-9-]{1,39}$`, livres no projeto (`abt epic list --ids` e `abt queue list --ids` com 0 resultados); dependencias sem ciclo e so para item anterior: ok.
6. Nenhum marcador do modelo sobrando (grep dos nomes longos e das letras do modelo): ok, saida vazia.
7. Nenhum `§EPIC-` fora de bloco cercado em `.abt/SPEC.md` e nos detalhes: ok, saida do awk vazia.

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-v1/filepilot-v1-1.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-2.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-3.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-4.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-5.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-6.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-7.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-8.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-9.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-10.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-11.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-12.md | criado | ok |
| .abt/items/filepilot-v1/filepilot-v1-13.md | criado | ok |

Estado do alvo antes da gravacao: `.abt/items/` nao existia; `abt scaffold --check` devolveu `mantido` para `RULES.md`, `WORKFLOW.md` e `SPEC.md` (estrutura completa, sem pendencia Bloqueante).

## 6. Pendencias e ajustes

- Ajustes no `itens.md`: nenhum (nenhuma falha em ids, titulos, pontos ou ordem).
- Contrato nao resolvido na SPEC: o `mypy` e o typecheck da stack Python e foi usado em todos os detalhes, mas a SPEC secao 4 e o `stack-decision.md` nao o listam entre as dependencias de desenvolvimento. O item filepilot-v1-1 manda acrescenta-lo ao `pyproject.toml` (versao a confirmar na instalacao); recomenda-se registrar a decisao na SPEC numa proxima execucao.
- Smoke omitido em todos os itens: o aplicativo e desktop, sem servidor, sem porta e sem rota de saude (Passo 3, nota 5). A conferencia do processo real fica no job de build do item filepilot-v1-13 (o `.exe` precisa ficar rodando por 5 segundos).
- Comandos de verificacao no `.abt/WORKFLOW.md`: o arquivo nao tem secao de comandos. Recomenda-se acrescentar `mypy . --no-error-summary`, `pytest` e `QT_QPA_PLATFORM=offscreen pytest tests/ui`; a decisao e da pessoa, Hugo nao escreve nesse arquivo.
- Arquivos que ainda nao existem estao marcados `(novo)` em todos os detalhes, inclusive os que um item anterior cria e um item posterior altera (o repositorio ainda nao tem codigo).
- Varias features compartilham o mesmo intervalo de `Linhas da SPEC` (por exemplo 7.2, L434-458); como a secao e unica e tem 25 linhas, isso e esperado. Qualquer mudanca na SPEC desloca os intervalos e pede nova execucao desta fase.
- Testes que dependem do Windows (atributos de arquivo, junction, tipo de unidade) usam `skipif` e so rodam de verdade no `windows-latest`, criado em filepilot-v1-1 (risco R1 do relatorio de prontidao).

Retorno: harness
