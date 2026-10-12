# Validacao do item filepilot-v1-3 - Servico de regras personalizadas

**Item:** filepilot-v1-3 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-010537
Veredito: APROVADO
**Tipo do item:** backend (service e persistencia SQLite; sem interface, sem migracao nova)

Skills de EF Core, Vuetify, Go, run-tests (.NET) e coverage-analysis (.NET) ignoradas: projeto Python.

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "no issues found in 11 source files"; `comm -13` contra a baseline (exit 0, 10 arquivos) sem linha de erro nova |
| 2 Criterios de aceite | PASS | 11/11 criterios atendidos (abaixo) |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented, FIXME e print em `filepilot/services/rules.py` e nos 3 testes; sem codigo comentado; zero aspas ou travessos tipograficos em `filepilot` |
| 4 Autorizacao e seguranca | PASS | nao ha endpoint; todo SQL e parametrizado com `?` (sem concatenacao de nome de regra: `filepilot/services/rules.py:114,117,140,158,195,198,225,240`), coberto por `tests/services/test_rules_storage.py:136` |
| 5 Testes | PASS | `pytest -v -rs`: 131 passed, 1 skipped; o skip e `tests/services/test_scanner_protected.py:150` ("so vale no Windows"), preexistente e justificado; 61 testes novos de regras; service novo com teste correspondente nos tres arquivos |
| 6 Consistencia entre documentos | PASS | SPEC L351-376 e L187-215 conferidas: assinaturas, erros, mensagens exatas de `fields` (`rules.py:19-23`), transacao unica, `UNIQUE (position)` em duas etapas, `operations.rule_name` como texto; nomes de colunas iguais a `migrations.py` e ao `Rule` de `models.py:20-28` |
| 7b Varredura adversarial | PASS | consumidores: nenhuma coluna nova em entidade com CRUD anterior (`rules` e `rule_extensions` ja existiam na migracao 1, sem CRUD); reuso: `grep Normalize/Resolver/Matcher/Parser/Similarity/reserved` fora de `rules.py` sem resultado (`scanner._extension` normaliza nome de ARQUIVO, escopo diferente) |
| 7c Degradacao e borda | PASS | sondagem com script independente: ver observacoes 1 a 4 da lista de correcoes (nenhuma e 5xx nem contradiz a SPEC) |
| 7d Matriz (backend) | PASS | BE-1: nenhum criterio "nenhum ponto faz X"; BE-2 e BE-3: n/a (sem contêiner de injecao nem policies no projeto) |
| 7e Funcao irma e comando citado | PASS | 7e-1: `rules.py` nao tem irma que leia, decida e grave o mesmo estado (o `scanner.py` so le disco); 7e-2: nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-3-f1 | `create_rule` com `PDF` e `.xlsx` grava `pdf` e `xlsx`, na ultima posicao; `list_rules` por `position` crescente | PASS | `rules.py:61-74` (normalizacao), `rules.py:158` (MAX+1), `rules.py:114` (ORDER BY position); `tests/services/test_rules.py:33,49` |
| filepilot-v1-3-f1 | Nome vazio ou >60, extensao `a-b` ou vazia e destinos `..\x`, `.`, `a//b`, `CON`, `a:b`, `C:\x` levantam `REGRA_INVALIDA` com `fields` e texto exato de 6.6 | PASS | `rules.py:92-106` e `rules.py:19-23`; `test_rules.py:65,70,84,124,132` (parametrizados com os seis destinos citados) |
| filepilot-v1-3-f1 | Destino com varios segmentos (`Trabalho/Planilhas`) e valido e fica como informado | PASS | `rules.py:87-89`; `test_rules.py:150` (confirma gravado e relido) |
| filepilot-v1-3-f1 | Extensao repetida na mesma regra e unida; extensao usada em outra regra e permitida | PASS | `rules.py:74` (`dict.fromkeys`); `test_rules.py:159,169` |
| filepilot-v1-3-f2 | `update_rule` altera nome, extensoes e destino e mantem a `position`; id inexistente levanta `REGRA_NAO_ENCONTRADA` | PASS | `rules.py:208-233`, `rules.py:177-181`; `tests/services/test_rules_order.py:43,60,71` |
| filepilot-v1-3-f2 | `delete_rule` e `move_rule` em 4 regras mantem posicoes de 1 a 4 sem lacuna e sem violar `UNIQUE (position)` | PASS | `rules.py:184-200` (etapa negativa na linha 191), `rules.py:236-254`; `test_rules_order.py:94,106,158`; mutacao refeita por mim (abaixo) |
| filepilot-v1-3-f2 | `move_rule` fora de 1 ate o total levanta `REGRA_INVALIDA` com `fields["position"]` igual a "Posição inválida." | PASS | `rules.py:249-250`, `rules.py:22`; `test_rules_order.py:171` (0, 5 e -1) |
| filepilot-v1-3-f3 | Extensoes em `rule_extensions` (uma linha por extensao) e `delete_rule` as apaga junto (ON DELETE CASCADE) | PASS | `rules.py:136-142`, `rules.py:240` (DELETE so em `rules`; cascata do banco); `tests/services/test_rules_storage.py:49,57` |
| filepilot-v1-3-f3 | Excluir regra nao altera `operations.rule_name` ja gravado | PASS | `test_rules_storage.py:69` (operacao inserida antes; tambem `:81` para renomear) |
| filepilot-v1-3-f3 | Falha na gravacao das extensoes desfaz a gravacao da regra | PASS | `rules.py:44-58` (rollback e BANCO_INDISPONIVEL); `test_rules_storage.py:93,107,122` (extensao invalida forcada em create e em update) |
| Gates do item | typecheck, pytest completo e awk do Passo 6 | PASS | mypy exit 0; 131 passed; `awk` sem saida |

Verificacoes das features: parser `py_compile` exit 0; grep deve casar: `rules.py:21` (mensagem de subpasta), `rules.py:191` (`position = -position`), `rules.py:117` (`rule_extensions`); grep nao deve casar: `FOREIGN KEY (rule_name` em `migrations.py` sem resultado; sem aspas ou travessos tipograficos em `filepilot`.

Mutacao refeita por mim (item novo, a prova nao era obrigatoria): troquei `UPDATE rules SET position = -position` por `position = position` em copia (`cp` antes e depois), suite inteira: 5 testes de `move_rule` falham; revertida por copia, suite de novo verde (131 passed, 1 skipped) e `git status --short` igual ao do inicio, exceto por este relatorio.

## Lista de correcoes

Nenhuma correcao obrigatoria. Observacoes que nao decidem o veredito, para a pessoa decidir:

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/services/rules.py | 77-84 | Destino com caractere de controle (`a\x00b`) e aceito; a SPEC 6.6 nao o proibe, mas o caminho nao e criavel no disco | Acrescentar a proibicao de caracteres de controle quando a SPEC for revista | nao |
| 2 | filepilot/services/rules.py | 77-84 | `con.txt` e aceito (a SPEC reserva so o nome exato `CON`), embora no Windows seja nome de dispositivo | Revisar a SPEC 6.6 para reservar o nome com extensao; hoje a guarda de 6.2 e quem protege | nao |
| 3 | filepilot/services/rules.py | 44-50 | `BEGIN` deferido: dois escritores simultaneos no mesmo banco poderiam colidir no `UNIQUE (position)` do `create_rule` (vira BANCO_INDISPONIVEL, sem corrupcao) | Usar `BEGIN IMMEDIATE`; hoje a instancia unica (item filepilot-v1-8) mitiga | nao |
| 4 | filepilot/services/rules.py | 61-66 | O sinal Kelvin (U+212A) vira a extensao `k` no `lower()`; inofensivo | Nenhuma | nao |
