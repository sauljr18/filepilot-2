# Validacao do item filepilot-v1-4 - Planejamento das operacoes e conflitos de nome

**Item:** filepilot-v1-4 | **Epico:** filepilot-v1 | **Data:** 2026-10-12
Execucao: 20261012-012101
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, 12 arquivos, zero erro novo vs baseline (`comm -13` sem linhas) |
| 2 Criterios de aceite | PASS | 11/11 criterios atendidos |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented, FIXME, print, type: ignore ou bloco comentado nos 4 arquivos do diff |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint; a guarda de caminho (`is_relative_to`) e coberta no Gate 2 |
| 5 Testes | PASS | suite completa 155 passed, 1 skipped (`test_scanner_protected.py:150`, "so vale no Windows", preexistente); 24 testes novos, todos passam |
| 6 Consistencia entre documentos | PASS | nomes e contratos batem com SPEC 6.2 (L276-291), 5.5 (L216-231) e o contexto herdado; categorias sem extensao repetida |
| 7b Varredura adversarial | PASS | sem coluna nova; `casefold` so no scanner e no planner, sem utilitario compartilhado que o planner reinvente |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim" as 4 perguntas (ver Observacoes) |
| 7d Matriz (backend) | PASS | BE-1: `grep mkdir` em planner.py = 0; BE-2 e BE-3: n/a (sem container de injecao nem policies) |
| 7e Funcao irma e comando citado | PASS | `_error(code)` com `_MESSAGES` proprio replica o padrao de `scanner.py` e `rules.py`; nenhuma mensagem manda rodar comando |

Gates do item, rodados nesta execucao: typecheck exit 0; `pytest` exit 0; awk do Passo 6 sem saida. `grep skipped`, `.suffix` e `is_relative_to` casam em `filepilot/services/planner.py`; `mkdir` nao casa; Unicode U+2010..U+201F ausente em `filepilot`; `py_compile` exit 0.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-4-f1 | fatura.pdf, foto.JPG e setup.exe: 2 operacoes (Documentos e Imagens) e 1 em `skipped` | PASS | planner.py:33-36, 71-73; tests/services/test_planner.py:26 |
| filepilot-v1-4-f1 | menor `position` vence regra posterior e categoria padrao | PASS | planner.py:30-32; test_planner.py:43, 54 |
| filepilot-v1-4-f1 | regra: `rule_name` da vencedora e `category` None; categoria: `category` preenchida e `rule_name` None | PASS | planner.py:32, 35, 92-93; test_planner.py:43, 77 |
| filepilot-v1-4-f1 | `seq` comeca em 1 e segue a ordem dos arquivos | PASS | planner.py:89; test_planner.py:86 |
| filepilot-v1-4-f2 | `Documentos/fatura.pdf` existente gera `fatura (1).pdf`; com `(1)` existente gera `fatura (2).pdf` | PASS | planner.py:52-61; test_planner_conflicts.py:25, 31 |
| filepilot-v1-4-f2 | `arquivo.tar.gz` ocupado vira `arquivo.tar (1).gz`; sem extensao vira `README (1)` | PASS | planner.py:56-57; test_planner_conflicts.py:43, 51 |
| filepilot-v1-4-f2 | comparacao ignora maiusculas e minusculas | PASS | planner.py:43, 54, 59, 78, 83; test_planner_conflicts.py:64, 70, 76 |
| filepilot-v1-4-f2 | nenhum arquivo existente alterado, nenhuma pasta criada | PASS | planner.py:42 (so `os.scandir`); test_planner_conflicts.py:101 |
| filepilot-v1-4-f3 | destino cujo `resolve()` sai da pasta levanta `DESTINO_FORA_DA_PASTA` e nenhum plano e devolvido | PASS | planner.py:48-49, 75-77; test_planner_guard.py:34, 57 |
| filepilot-v1-4-f3 | arvore da pasta identica antes e depois; banco nao e tocado | PASS | `build_plan` nao recebe conexao (planner.py:64); test_planner_guard.py:73 |
| filepilot-v1-4-f3 | `Plan.is_empty` verdadeiro quando nenhum arquivo tem categoria ou regra | PASS | filepilot/domain/models.py:51 `Plan.is_empty`; test_planner_guard.py:88, 97 |

## Prova independente (mutacoes da Rita)

O Carlos nao declarou prova por mutacao (feature nova); as mutacoes abaixo sao da Rita, escopo `pytest -q tests/services` (125 passed antes de mutar), revertidas por copia de arquivo com hash identico ao original conferido no fim.

| # | Mutacao (diff) | Resultado |
|---|----------------|-----------|
| M1 | planner.py:43 `entry.name.casefold()` -> `entry.name` | 3 falharam: pego |
| M4 | planner.py:58 `number = 1` -> `number = 2` | 6 falharam: pego |
| M5 | planner.py:30 `sorted(rules, key=...)` -> `rules` | 1 falhou: pego |
| M2 | removida a guarda de planner.py:85-86 | 125 passed: sobrevive (guarda redundante com a de 76-77) |
| M3 | removida a guarda de planner.py:76-77 | 125 passed: sobrevive (redundante com a de 85-86) |

Uma mutacao com as duas guardas removidas ao mesmo tempo nao foi executada: a permissao para o comando foi negada. Cada guarda sozinha tem teste de saida de pasta que passa por ambas, entao M2 e M3 sobreviverem e consequencia da redundancia, nao de teste ausente; o conjunto das duas nao foi medido.

## Observacoes (nao decidem o veredito)

- Sondas fora do repositorio: duas regras que apontam para a mesma pasta por caminhos diferentes (`b` e `x/../b`) usam chaves distintas em `taken_by_directory` (planner.py:78). Nao gera nome duplicado: o sufixo preserva a extensao, entao so arquivos de mesma extensao colidem, e eles caem na mesma regra. A validacao de `rules.py:77-89` tambem recusa `..`, `.` e segmento vazio. Destino vazio em `Rule` montada a mao devolve o proprio nome de origem; tambem inalcancavel pelo servico de regras.
- Estado da arvore igual ao do Passo 0: so os 4 arquivos novos nao rastreados, `git diff --stat` vazio, `.abt/` intacto.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/services/planner.py | 85 | A segunda guarda (apos o sufixo) e redundante com a de 76-77, pois o sufixo so acrescenta ` (n)` ao nome e nao muda a pasta; M2 e M3 sobrevivem | Manter as duas por defesa em profundidade ou remover uma e deixar um teste que prove a que ficou | nao |
| 2 | tests/services/test_planner.py, test_planner_conflicts.py, test_planner_guard.py | 7, 7, 10 | O helper `_file` esta copiado em tres arquivos de teste | Extrair para um `conftest.py` de `tests/services` se o item filepilot-v1-5 for reusar | nao |
| 3 | filepilot/ (raiz do repositorio) | - | Pastas `__pycache__` aparecem como nao rastreadas e nao ha `.gitignore` | Na entrega, o Ivan escopa o `git add` aos 4 arquivos do item e este relatorio | nao |
