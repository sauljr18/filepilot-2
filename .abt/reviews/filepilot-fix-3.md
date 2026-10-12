# Validacao do item filepilot-fix-3 - Ordem estavel da lista de arquivos com nomes que so diferem por maiuscula

**Item:** filepilot-fix-3 | **Epico:** filepilot-fix | **Data:** 2026-10-12
Execucao: 20261012-111328
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, 14 arquivos; `comm -13` contra a baseline do Carlos: zero erros novos |
| 2 Criterios de aceite | PASS | 3/3 criterios atendidos |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented e FIXME; zero Unicode proibido; sem bloco comentado nem print |
| 4 Autorizacao e seguranca | PASS | nenhum endpoint novo ou alterado (so leitura, sem efeitos) |
| 5 Testes | PASS | suite inteira 238 passed, 2 skipped (ambos so valem no Windows: `test_destination_checks.py:153` e `test_scanner_protected.py:185`); mutacao refeita por mim: 3 testes novos falham |
| 6 Consistencia entre documentos | PASS | codigo bate com a SPEC 27.4 (L958-975); ver Observacao 1 |
| 7b Varredura adversarial | PASS | nenhum outro consumidor reordena a lista (`planner.py` so usa `casefold` para colisao de destino); nenhum utilitario de ordenacao reinventado |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim": a chave e uma tupla de duas strings, sem excecao nova; lista vazia segue em `PASTA_VAZIA` antes do sort (`scanner.py:125`); docstring de `scan_folder` ("ordenados por nome") continua verdadeira |
| 7d Matriz (backend) | PASS | BE-1 n/a (nenhum criterio "nenhum ponto faz X"); BE-2 n/a (sem service ou interface nova); BE-3 n/a (sem policy no projeto) |
| 7e Funcao irma e comando citado | PASS | nenhuma funcao nova; nenhuma mensagem nova cita comando |

Evidencia dos comandos (rodados por mim, nao reaproveitados):

- typecheck: `Success: no issues found in 14 source files`, exit 0.
- `python -m py_compile filepilot/services/scanner.py`: exit 0.
- grep deve casar `item.name.casefold(), item.name`: `filepilot/services/scanner.py:127`.
- grep nao deve casar `[\x{2010}-\x{2015}\x{2018}-\x{201F}]` em `scanner.py` e no teste novo: vazio.
- placeholder `§EPIC-` fora de bloco cercado (`awk` do Gate do item): saida vazia.
- `pytest tests/services/test_scanner_order.py tests/services/test_scanner.py`: 18 passed.
- `pytest` (suite inteira): 238 passed, 2 skipped.

Mutacao refeita (escopo: suite inteira): em `scanner.py:127`, `(item.name.casefold(), item.name)` trocado por `item.name.casefold()` (diff: `-    files.sort(key=lambda item: (item.name.casefold(), item.name))` / `+    files.sort(key=lambda item: item.name.casefold())`). Resultado: 3 failed, 235 passed, 2 skipped (`test_empate_de_casefold_desempata_pelo_nome_exato`, `test_ordem_nao_depende_da_ordem_de_entrada`, `test_tres_variantes_do_mesmo_nome_em_todas_as_permutacoes`). Revertida por copia de arquivo; `git status --short` e `git diff --stat` identicos aos anotados antes da mutacao. O numero bate com o do Carlos (3 failed, 235 passed), no mesmo escopo.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix-3-f1 | Com Path.iterdir trocado por monkeypatch para devolver b.txt, a.txt e A.txt em qualquer das 6 permutacoes, a lista tem os nomes A.txt, a.txt e b.txt, nessa ordem | PASS | `filepilot/services/scanner.py:127`; `tests/services/test_scanner_order.py:28-33` (entrada `b.txt, a.txt, A.txt` devolve `A.txt, a.txt, b.txt`) e `:36-47` (3 entradas, incluindo `A.txt, a.txt, b.txt` e `a.txt, A.txt, b.txt`, dao o mesmo resultado). Cobre 3 das 6 permutacoes dos tres nomes (as da SPEC); ver Observacao 2. Mutacao reprova os dois |
| filepilot-fix-3-f1 | Foto.JPG, foto.jpg e FOTO.jpg dao a mesma lista nas 6 permutacoes de entrada | PASS | `tests/services/test_scanner_order.py:50-59` (`permutations` das 3 variantes, `len(results) == 6`, todas iguais a `["FOTO.jpg", "Foto.JPG", "foto.jpg"]`) |
| filepilot-fix-3-f1 | Nomes que ja diferiam em casefold (beta.txt e Alfa.txt) continuam em ordem alfabetica sem diferenciar maiusculas | PASS | `tests/services/test_scanner_order.py:62-66` (as 2 permutacoes devolvem `["Alfa.txt", "beta.txt"]`); `scanner.py:127` mantem o `casefold` como primeiro elemento da chave |

Entrega das features: `filepilot/services/scanner.py` (alterado, 1 linha) e `tests/services/test_scanner_order.py` (novo) existem; `git diff HEAD` mostra so essas duas mudancas. O teste nao cria dois nomes que so diferem por maiuscula no disco (usa `monkeypatch` em `Path.iterdir` e `scanner._scan_entry`), como a SPEC exige para o runner `windows-latest`.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| - | - | - | nenhuma correcao obrigatoria | - | - |

## Observacoes (nao decidem o veredito)

1. `.abt/SPEC.md:265` e `:474` ainda dizem "ordena por `name` sem diferenciar maiusculas". A propria SPEC 27.4 (L960) declara que substitui essa frase em 6.1; e redacao pendente da SPEC, nao defeito do codigo, e fica com o product-spec.
2. O criterio 1 do detalhe pede "qualquer das 6 permutacoes" dos tres nomes `b.txt`, `a.txt`, `A.txt`; o teste novo cobre 3 entradas desse conjunto (as da SPEC, "Testes obrigatorios" 1 e 2) e as 6 permutacoes completas valem para as variantes de `Foto` (item 3 da SPEC), que exercitam a mesma chave. A SPEC pede exatamente o que foi escrito; o texto do criterio e mais amplo que os "Testes obrigatorios" dela.
3. Numeracao: o detalhe e a SPEC citam `scanner.py:101` e `L88-102`; o `sort` esta hoje na linha 127. So a numeracao difere, o codigo e o descrito.
