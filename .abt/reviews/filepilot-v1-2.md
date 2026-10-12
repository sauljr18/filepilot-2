# Validacao do item filepilot-v1-2 - Leitura da pasta e pastas protegidas

**Item:** filepilot-v1-2 | **Epico:** filepilot-v1 | **Data:** 2026-10-11
Execucao: 20261012-004925
Veredito: APROVADO
**Tipo do item:** backend

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `python -m mypy --platform win32 filepilot` exit 0, "Success: no issues found in 10 source files"; contra a baseline (8 arquivos, exit 0) zero erro novo |
| 2 Criterios de aceite | PASS | 7/7 criterios atendidos (4 em f1, 3 em f2) |
| 3 Qualidade de codigo | PASS | grep de TODO, placeholder, not implemented e FIXME: zero; sem print e sem codigo comentado |
| 4 Autorizacao e seguranca | PASS | n/a: aplicativo local, sem endpoint; `scan_folder` so le (nao grava, nao move) |
| 5 Testes | PASS | `pytest` exit 0: 61 passed, 1 skipped; o pulado (`tests/services/test_scanner_protected.py:150`) so vale no Windows e roda no windows-latest; 26 testes novos sem assert fraco nem excecao engolida |
| 6 Consistencia entre documentos | PASS | codigos e as 4 mensagens de `scanner.py:13-16` batem caractere a caractere com a tabela de 6 da SPEC (grep -F: 1 ocorrencia na SPEC e 1 no codigo, cada); `ScannedFile` e `FilePilotError` usados como no contexto herdado |
| 7b Varredura adversarial | PASS | nenhum consumidor de `scan_folder` fora do item (grep em `filepilot/`); sem utilitario existente reinventado |
| 7c Degradacao e borda | FAIL (nao decide) | 3 achados, itens 1 a 3 da lista de correcoes |
| 7d Matriz (backend) | PASS | BE-1 n/a (nenhum criterio "nenhum ponto faz X"); BE-2 n/a (sem conteiner de injecao); BE-3 n/a (sem policies) |
| 7e Funcao irma e comando citado | PASS | nenhuma funcao lê, decide e grava estado compartilhado; nenhuma mensagem manda rodar comando |

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-v1-2-f1 | 3 arquivos visiveis, 1 pasta e 1 oculto (atributo simulado): devolve os 3, ordenados por nome sem diferenciar maiusculas | PASS | filepilot/services/scanner.py:76-79,98,101; tests/services/test_scanner.py:19,46 |
| filepilot-v1-2-f1 | extensao de `a.tar.gz`, `.gitignore` e `b.` e `gz`, vazio e vazio | PASS | filepilot/services/scanner.py:62-67; tests/services/test_scanner.py:83 |
| filepilot-v1-2-f1 | `PASTA_INVALIDA`, `PASTA_ILEGIVEL` e `PASTA_VAZIA` | PASS | filepilot/services/scanner.py:92-93,94-97,99-100; tests/services/test_scanner.py:91,99,108,123 |
| filepilot-v1-2-f1 | link simbolico fora da lista; `.lnk` com extensao `lnk` | PASS | filepilot/services/scanner.py:36-38,76-77; tests/services/test_scanner.py:133,144 |
| filepilot-v1-2-f2 | raiz de unidade, `%SystemRoot%`, `%ProgramFiles%`, `%ProgramFiles(x86)%` e pastas dentro delas dao `PASTA_PROTEGIDA` antes de listar | PASS | filepilot/services/scanner.py:48-58,90-91; tests/services/test_scanner_protected.py:26,30,42,54,75 |
| filepilot-v1-2-f2 | caminho `\\` e unidade de rede (`GetDriveTypeW` igual a 4, simulado) dao `PASTA_PROTEGIDA` | PASS | filepilot/services/scanner.py:50-51,59,45; tests/services/test_scanner_protected.py:96,100,125 |
| filepilot-v1-2-f2 | fora do Windows a verificacao de unidade e ignorada e os demais testes passam | PASS | filepilot/services/scanner.py:43-44; tests/services/test_scanner_protected.py:116,143 |

Gates do item rodados por Rita: typecheck exit 0, `pytest` exit 0 (61 passed, 1 skipped), awk do Passo 6 sem saida, grep de Unicode em `filepilot` sem resultado.

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | filepilot/services/scanner.py | 52 | Pasta escolhida com laco de link simbolico faz `folder.resolve()` levantar `RuntimeError: Symlink loop from '...'` (Python 3.12), em vez de `FilePilotError`. Antes da checagem de protegida entrar na frente, o `folder.is_dir()` devolvia `PASTA_INVALIDA`. Reproduzido com `a -> b` e `b -> a`. Sem teste para o caso | Capturar `OSError` e `RuntimeError` em volta do `resolve()` e levantar `PASTA_INVALIDA`, com teste do laco | nao |
| 2 | filepilot/services/scanner.py | 56 | Variavel de ambiente definida e vazia (`SystemRoot=""`) vira `Path("")`, que resolve para a pasta atual: a pasta atual e tudo dentro dela passam a dar `PASTA_PROTEGIDA`. Reproduzido com `SystemRoot=""` e pasta igual ao diretorio atual | Usar `os.environ.get(variable) or default` | nao |
| 3 | filepilot/services/scanner.py | 101 | Nomes que diferem so por maiuscula (`a.txt` e `A.txt`, possivel fora do Windows) empatam no `casefold()` e saem na ordem da listagem do sistema: reproduzido `['A.txt', 'a.txt', 'b.txt', 'B.txt']`, ordem nao deterministica entre sistemas | Chave `(item.name.casefold(), item.name)` | nao |

Observacao sem acao: `scanner.py:50` trata todo caminho que comeca com `\\` como de rede, o que inclui o prefixo de caminho longo `\\?\C:\...`; a pasta escolhida pela interface nao vem nesse formato, e a SPEC 6.1 manda recusar caminho que comeca com `\\`.
