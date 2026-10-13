# Relatorio do Detalhe dos Itens: filepilot-fix3

**Data:** 2026-10-13
**Modo:** so SPEC + itens
**Stack:** Python 3.12 com PySide6, pytest, pytest-qt e mypy (comandos da SPEC 19.2 e 45.7, do manifesto `pyproject.toml` e da tabela do Passo 3; `.abt/WORKFLOW.md` nao traz secao de comandos)

## 1. Secao da SPEC

Secao nova `## 45. Correcao de sete defeitos remanescentes na main [DELTA 2026-10-13, ...]`, `.abt/SPEC.md` L1255-1460 (total do arquivo: 1460 linhas). Subsecoes de conteudo usadas: 45.2 a 45.8 (L1275-1422). Nao sao alvo de `Linhas da SPEC`: 45.9 `Pendencias para decisao` (L1423-1433) e 45.10 `Traceability Matrix` (L1434-1460).

## 2. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Features |
|---|---|---|---|---|---|
| 1 | filepilot-fix3-1 | Checagem de tipos do mypy cobre a pasta de testes | 2 | filepilot-mypy-win32-1,filepilot-mypy-win32-2 | 2 |
| 2 | filepilot-fix3-2 | Arquivo .gitignore na raiz do repositorio | 1 | - | 2 |
| 3 | filepilot-fix3-3 | Laco de atalhos detectado tambem no Windows | 5 | filepilot-fix2-4 | 2 |
| 4 | filepilot-fix3-4 | Desfazer com laco de atalhos vira PASTA_INVALIDA | 4 | filepilot-fix2-4,filepilot-v1-11 | 2 |
| 5 | filepilot-fix3-5 | Historico mostra a data como veio quando ela e invalida | 2 | filepilot-v1-11 | 2 |
| 6 | filepilot-fix3-6 | Barra de progresso some ao desfazer a organizacao | 2 | filepilot-v1-10,filepilot-v1-11 | 2 |
| 7 | filepilot-fix3-7 | Testes de instancia unica e desfazer falham em vez de travar | 4 | filepilot-fix2-3,filepilot-v1-11 | 2 |

Total: 7 itens, 20 pontos, 14 features. Detalhes em `.abt/items/filepilot-fix3/`.

## 3. Linhas da SPEC por feature

| Feature | Linhas da SPEC | Subsecao |
|---|---|---|
| filepilot-fix3-1-f1 | L1379-1382 | 45.7 D6: checagem de tipos cobre os testes |
| filepilot-fix3-1-f2 | L1383-1391 | 45.7 D6: checagem de tipos cobre os testes |
| filepilot-fix3-2-f1 | L1393-1414 | 45.8 D7: .gitignore |
| filepilot-fix3-2-f2 | L1416-1421 | 45.8 D7: .gitignore |
| filepilot-fix3-3-f1 | L1317-1323 | 45.4 D3: laco de atalhos provado tambem no Windows |
| filepilot-fix3-3-f2 | L1325-1335 | 45.4 D3: laco de atalhos provado tambem no Windows |
| filepilot-fix3-4-f1 | L1296-1302 | 45.3 D2: desfazer com laco de atalhos |
| filepilot-fix3-4-f2 | L1304-1311 | 45.3 D2: desfazer com laco de atalhos |
| filepilot-fix3-5-f1 | L1279-1283 | 45.2 D1: data invalida no Historico |
| filepilot-fix3-5-f2 | L1285-1290 | 45.2 D1: data invalida no Historico |
| filepilot-fix3-6-f1 | L1341-1345 | 45.5 D4: barra de progresso some ao desfazer |
| filepilot-fix3-6-f2 | L1347-1354 | 45.5 D4: barra de progresso some ao desfazer |
| filepilot-fix3-7-f1 | L1360-1364 | 45.6 D5: testes que travam em vez de falhar |
| filepilot-fix3-7-f2 | L1363-1372 | 45.6 D5: testes que travam em vez de falhar |

## 4. Checklist mecanico

1. ok: um detalhe por item do `itens.md`, em `.abt/items/filepilot-fix3/<item_id>.md`, com linha 1, cabecalho e as quatro secoes `## Objetivo`, `## Contexto herdado`, `## Features` e `## Gates do item` (conferido por script nesta execucao: 7 de 7 com 4 secoes).
2. ok: `Ordem`, `Pontos` e `Depende de` iguais aos do `itens.md`; `Pontos` de 1 a 5.
3. ok: toda feature (14 de 14) com `Linhas da SPEC`, `Arquivos:`, de 3 a 4 criterios, `Verificacao:` com typecheck e `Dicas:`.
4. ok: todo intervalo com `1 <= a <= b <= 1460`, de 4 a 22 linhas, dentro de uma subsecao de conteudo da secao nova; nenhum na matriz, na `Pendencias para decisao` nem num cabecalho de secao anexada pela integracao.
5. ok: ids no formato e livres (`abt epic list --ids` e `abt queue list --ids` reconferidos); dependencias so para itens existentes e prontos, sem ciclo.
6. ok: nenhum marcador do modelo sobrando; o `grep -nE` do Passo 6 sobre `.abt/items/filepilot-fix3/*.md` terminou com saida vazia.
7. ok: nenhum placeholder provisorio de secao fora de bloco cercado; o awk do Passo 6 sobre `.abt/SPEC.md` e `.abt/items/filepilot-fix3/*.md` terminou com saida vazia.

## 5. Destino e acao

| Destino | Acao | Status |
|---|---|---|
| .abt/items/filepilot-fix3/filepilot-fix3-1.md | criado | ok |
| .abt/items/filepilot-fix3/filepilot-fix3-2.md | criado | ok |
| .abt/items/filepilot-fix3/filepilot-fix3-3.md | criado | ok |
| .abt/items/filepilot-fix3/filepilot-fix3-4.md | criado | ok |
| .abt/items/filepilot-fix3/filepilot-fix3-5.md | criado | ok |
| .abt/items/filepilot-fix3/filepilot-fix3-6.md | criado | ok |
| .abt/items/filepilot-fix3/filepilot-fix3-7.md | criado | ok |

## 6. Pendencias e ajustes

- Bloqueante: nenhuma. `abt scaffold --check` confirmou `.abt/RULES.md`, `.abt/WORKFLOW.md` e `.abt/SPEC.md` como `mantido`; a pasta `.abt/items/filepilot-fix3/` nao existia.
- Ajustes do `itens.md`: nenhum.
- Comando de typecheck: os gates dos itens 2 a 7 checam `python -m mypy --platform win32 filepilot` mais os arquivos de teste novos ou alterados do proprio item, e so o item 1 roda o comando completo de 45.7 (`... filepilot tests`). Motivo: os tres erros de `mypy` nas fixtures existentes (45.7) so somem com o item 1, e um gate completo falharia nos outros itens se eles forem entregues antes. A fonte do comando e a SPEC 19.2 e 45.7, nao a linha `mypy . --no-error-summary` da tabela do Passo 3.
- Smoke omitido em todos os itens: o FilePilot e um aplicativo desktop sem servidor, porta nem rota de saude (Passo 3 nota 5).
- Previsao de falha, nao ha comando local que a prove: no item 3 a deteccao de laco no Windows foi medida so no Linux (45.4, 45.9 item 3); se o job `windows-latest` nao detectar o laco, o teste real falha e o item nao esta concluido.
- Recomendacao: acrescentar a `.abt/WORKFLOW.md` os comandos `python -m mypy --platform win32 filepilot tests` e `pytest` (a pessoa decide; Hugo nao escreve nele).
- Nenhum contrato compartilhado sem resolucao e nenhuma subsecao da SPEC acima de 60 linhas (a maior, 45.8, tem 30).
- Ordem recomendada pelo relatorio de prontidao: item 1 antes dos demais e item 3 antes do item 4; nenhuma das duas e dependencia obrigatoria (45.1).

Retorno: harness
