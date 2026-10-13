# Validacao do item filepilot-fix3-4 - Desfazer com laco de atalhos vira PASTA_INVALIDA

**Item:** filepilot-fix3-4 | **Epico:** filepilot-fix3 | **Data:** 2026-10-13
Execucao: 20261013-172902
Veredito: APROVADO
**Tipo do item:** backend (servico `undo.py` e testes; nenhum codigo de producao da interface mudou)

## Resumo dos gates

| Gate | Status | Detalhe |
|------|--------|---------|
| 1 Build/Typecheck | PASS | `mypy --platform win32 filepilot tests/services/test_undo_loop.py tests/ui/test_undo_loop.py`: exit 0, "Success: no issues found in 27 source files"; zero linha nova contra a baseline do Carlos |
| 2 Criterios de aceite | PASS | 8/8 atendidos, 0 NAO VERIFICAVEL |
| 3 Qualidade de codigo | PASS | zero TODO, placeholder, not implemented ou FIXME; sem `print`; sem Unicode tipografico; sem `.resolve()` nem `asyncio.new_event_loop` em `undo.py`; `resolve_folder` presente (3 ocorrencias) |
| 4 Autorizacao e seguranca | PASS | n/a: nenhum endpoint novo ou alterado |
| 5 Testes | PASS | suite completa: 505 passed, 2 skipped (os dois so do Windows, em outros arquivos); 32 passed nos arquivos de desfazer; mutacoes refeitas (ver abaixo) |
| 6 Consistencia entre documentos | PASS | SPEC L1296-1302 e L1304-1311 cobertas; nomes e texto de `PASTA_INVALIDA` iguais aos de `scanner.py:14` |
| 7b Varredura adversarial | PASS | `undo.py` reusa `resolve_folder`; nao reinventa a deteccao de laco |
| 7c Degradacao e borda | PASS | nenhuma resposta "sim" |
| 7d Matriz (backend) | PASS | BE-1 grep zero; BE-2 e BE-3 n/a (sem service novo nem Authorize) |
| 7e Funcao irma e comando citado | PASS | nenhuma divergencia; nenhuma mensagem nova cita comando |

Gate UI-1 nao se aplica: o item nao altera tela, layout nem CSS. O teste de interface fica em `tests/ui/` e nao muda codigo de producao da interface.

## Evidencias dos gates

- Gate 1: baseline `Success` em 25 arquivos; agora `Success` em 27 (os dois arquivos de teste novos). Saida em `abt-review-filepilot-fix3-4.typecheck` no diretorio git.
- Gate 5, mutacoes refeitas por mim na suite inteira, revertidas por copia de arquivo; `git status --short` e `git diff --stat` iguais ao anotado antes:

| Mutacao (diff) | Resultado (suite inteira) |
|----------------|---------------------------|
| M1 `undo.py:48` `resolve_folder(path).is_relative_to(resolve_folder(folder))` vira `path.resolve().is_relative_to(folder.resolve())` | 4 failed, 501 passed (mesma contagem da tabela do Carlos) |
| M2 `undo.py:116` `except FilePilotError:` vira `except ZeroDivisionError:` | 1 failed, 504 passed (mesma contagem) |
| M3 `undo.py:48` so o segundo operando volta a `folder.resolve()` | 0 failed, 505 passed: SOBREVIVEU (ver correcao 1) |
| M4 `undo.py:107` `resolve_folder(current)` vira `current.resolve()` no `while` da limpeza | 1 failed, 504 passed |

- Gate 2, comportamento fora da suite: com `Path.resolve` falhando so para a pasta escolhida e o caminho original fora do laco, `undo._is_inside` levanta `FilePilotError` `PASTA_INVALIDA` com `__cause__` `RuntimeError` (execucao direta, fora da arvore). No Python 3.12.3, `Path("laco").resolve()` de um link para si mesmo levanta `RuntimeError: Symlink loop`.

## Criterios de aceite

| Feature | Criterio | Status | Evidencia |
|---------|----------|--------|-----------|
| filepilot-fix3-4-f1 | Laco em `source_path` ou em `folder_path` faz `undo_last` levantar `PASTA_INVALIDA` com a mensagem de contrato, sem o texto original e com `__cause__` `RuntimeError` | PASS | `filepilot/services/undo.py:48`; `tests/services/test_undo_loop.py:95` e `:152`; execucao direta da pasta escolhida citada acima |
| filepilot-fix3-4-f1 | Depois do erro: restaurados continuam `restaurado`, demais `movido`, organizacao nao fica `desfeita`, `conn.in_transaction` False, `OPERATION_LOCK` livre | PASS | `tests/services/test_undo_loop.py:187` (linhas 207-208 e `_lock_is_free` em `:76`); `undo.py:181-182` (`finally` libera o lock) |
| filepilot-fix3-4-f1 | Laco numa pasta de destino ou em pai dela na limpeza nao levanta erro: `removed_folders == []`, pasta continua, organizacao `desfeita` | PASS | `filepilot/services/undo.py:106-117`; `tests/services/test_undo_loop.py:220` |
| filepilot-fix3-4-f1 | `OSError` com `EACCES` continua `OSError` e nao vira `PASTA_INVALIDA` | PASS | `tests/services/test_undo_loop.py:135`; `scanner.py:92-94` |
| filepilot-fix3-4-f2 | `pytest tests/services/test_undo_loop.py tests/ui/test_undo_loop.py` exit 0 e cobre os seis testes de 45.3 | PASS | 7 testes passam: `test_undo_loop.py:95`, `:117`, `:135`, `:152`, `:187`, `:220` e `tests/ui/test_undo_loop.py:50` |
| filepilot-fix3-4-f2 | Na interface: resumo com o texto de contrato, diferente do generico, botao habilitado e `window.organizing is False` | PASS | `tests/ui/test_undo_loop.py:50` |
| filepilot-fix3-4-f2 | Laco real: `pytest.skip` se o sistema recusar o link, exceto no Windows do Actions, onde falha | PASS | `tests/services/test_undo_loop.py:33-40` (`_symlink`), usado em `:152` |
| filepilot-fix3-4 | Gates do item: typecheck, `pytest` completo e awk de placeholder | PASS | exit 0; 505 passed, 2 skipped; awk com saida vazia |

## Lista de correcoes

| # | Arquivo | Linha | Problema | Correcao | Decide o veredito? |
|---|---------|-------|----------|----------|--------------------|
| 1 | tests/services/test_undo_loop.py | 152 | A mutacao M3 sobrevive: nenhum teste exercita laco so em `folder_path` com o caminho original fora do laco; no laco real o `path` falha antes de a pasta ser resolvida. O comportamento esta correto (execucao direta), mas um retorno a `folder.resolve()` em `_is_inside` passaria despercebido. | Acrescentar um teste com `Path.resolve` falhando so para a pasta escolhida e `source_path` fora do laco, esperando `PASTA_INVALIDA`. | nao |
