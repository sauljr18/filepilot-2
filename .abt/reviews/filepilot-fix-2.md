# Validacao do item filepilot-fix-2 - Variavel de ambiente vazia nao torna a pasta atual protegida

**Item:** filepilot-fix-2 | **Epico:** filepilot-fix | **Data:** 2026-10-12
Execucao: 20261012-105516
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `mypy --platform win32 filepilot` exit 0, "no issues found in 14 source files"; `comm` contra a baseline do Carlos sem linha nova |
| 2 Criterios de aceite | PASS | 3/3 criterios atendidos |
| 3 Qualidade de codigo | PASS | grep de TODO, placeholder, not implemented e FIXME vazio; sem `print`; sem caractere Unicode tipografico em scanner.py |
| 4 Autorizacao e seguranca | PASS | n/a: sem endpoint; a mudanca so le variavel de ambiente |
| 5 Testes | PASS | suite completa 234 passed, 2 skipped (ambos "so vale no Windows": test_destination_checks.py:153 e test_scanner_protected.py:185); 3 mutacoes refeitas pela Rita |
| 6 Consistencia entre documentos | PASS | SPEC L940-957 lida; helper `_protected_root(variable: str, default: str) -> Path` com a assinatura da SPEC; `_is_protected(folder, resolved)` do contexto herdado preservada; os 4 testes obrigatorios da SPEC existem |
| 7b Varredura adversarial | PASS | `_PROTECTED_ENV` e `_is_protected` so tem consumidor em scanner.py; unico `os.environ` do pacote e o do helper; nenhum utilitario equivalente a reinventar |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim" (ver abaixo); 2 observacoes desejaveis, sem efeito no veredito |
| 7d Matriz (backend) | PASS | BE-1 n/a (nenhum criterio "nenhum ponto faz X"); BE-2 n/a (helper privado de modulo, sem injecao); BE-3 n/a (sem `Authorize`) |
| 7e Funcao irma e comando citado | PASS | nenhuma: `_protected_root` so le, sem lock nem escrita; nenhuma mensagem nova manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix-2-f1 | Para cada uma das tres variaveis definida como "" e como "   ", com a pasta atual igual a tmp_path, scan_folder(tmp_path / "pasta") com um arquivo regular dentro devolve a lista e nao levanta PASTA_PROTEGIDA (6 casos) | PASS | tests/services/test_scanner_protected.py:96-107 (2 valores x 3 variaveis, chdir em tmp_path); scanner.py:64-69 e :79 |
| filepilot-fix-2-f1 | _protected_root("SystemRoot", r"C:\Windows") com a variavel vazia devolve Path(r"C:\Windows").resolve() e nao a pasta atual | PASS | tests/services/test_scanner_protected.py:110-120; scanner.py:66-69 |
| filepilot-fix-2-f1 | O teste existente com SystemRoot apontando para uma pasta de tmp_path continua dando PASTA_PROTEGIDA para as pastas dentro dela | PASS | tests/services/test_scanner_protected.py:41-64 (inalterados) passam na suite completa |

## Evidencia da prova por mutacao (refeita pela Rita, suite inteira, reversao por copia de arquivo)

| # | Mutacao (diff em scanner.py) | Resultado na suite inteira |
|---|------------------------------|----------------------------|
| M1 | linha 67: `if value is None or value.strip() == "":` vira `if value is None:` | 5 failed, 229 passed, 2 skipped (3 do teste de scan com `""` e 2 do teste do helper) |
| M2 | linha 79: `root = _protected_root(variable, default)` vira `root = Path(os.environ.get(variable, default)).resolve()` | 3 failed, 231 passed, 2 skipped (os 3 do teste de scan com `""`) |
| M3 | linha 67: `value is None or value.strip() == ""` vira `value is None or value == ""` | 1 failed, 233 passed, 2 skipped (so o teste do helper com `"   "`) |

Os numeros de M1 e M2 batem com os do Carlos. No fim: `git status --short` e `git diff --stat` identicos aos do inicio, sem `.bak`.

## Respostas as perguntas do 7c

1. Parametro que antes degradava e agora lanca: nao. `Path("   ").resolve()` nao levantava antes nem levanta agora; o valor vazio passa a usar o padrao.
2. Zero ou vazio inverte classificacao: era o defeito do item (vazio virava a pasta atual e protegia tudo dentro dela); corrigido. O inverso (guarda novo silenciando o que deveria aparecer): nao, o padrao continua protegendo `C:\Windows`, `C:\Program Files` e `C:\Program Files (x86)`.
3. Fraqueza antiga tornada material: nao. Valor nao vazio e relativo (por exemplo `windows`) continua resolvido a partir da pasta atual; e fora de escopo declarado na SPEC (27.3, linha 948).
4. Comentario que virou falso: nao. O comentario de `_PROTECTED_ENV` (scanner.py:22) continua verdadeiro e o docstring novo cita 27.3, secao que existe em SPEC.md:940.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | tests/services/test_scanner_protected.py | 96-107 | Desejavel: os 3 casos de `"   "` do teste de scan passam mesmo sem a correcao (M3 nao os derruba, porque `Path("   ").resolve()` e uma subpasta da pasta atual, que nao e pai de `pasta`); quem protege o caso so-espacos e o teste do helper (linha 110-120) | Se quiser que o teste de scan tambem pegue so-espacos, criar a pasta sob um diretorio chamado `"   "` ou comparar com `scanner._protected_root`; nao e necessario para o criterio | nao |
| 2 | filepilot/services/scanner.py | 69 | Desejavel: valor com espacos em volta de um caminho real (por exemplo `" C:\Windows "`) nao e aparado e segue como esta; e fora do escopo da SPEC (27.3 trata so vazio e so-espacos) | Nenhuma agora; registrar se for tratar | nao |

Nenhum item da lista decide o veredito.
