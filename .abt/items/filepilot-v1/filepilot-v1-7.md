# filepilot-v1-7 - Historico e desfazer a ultima organizacao
Epico: filepilot-v1 | Ordem: 7 | Pontos: 6 | Depende de: filepilot-v1-1,filepilot-v1-5

## Objetivo
Os servicos history e undo listam organizacoes e operacoes e devolvem os arquivos da ultima organizacao ao caminho e ao nome originais, sem sobrescrever nada.

## Contexto herdado
-

## Features

### filepilot-v1-7-f1 Listar organizacoes e detalhes
Linhas da SPEC: .abt/SPEC.md L314-334
Arquivos:
- filepilot/services/history.py (novo)
- tests/services/test_history.py (novo)
Criterios de aceite:
- `list_organizations` ordena por `started_at` decrescente com desempate por `id` decrescente, pagina em 50 e devolve `items` vazio e `total` 0 sem registros.
- `page` menor que 1 vira 1 e `page_size` fora de 1 a 200 vira 50.
- `get_organization_detail` devolve as operacoes por `seq` crescente e lista vazia para `organization_id` inexistente.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_history.py -> exit 0
- parser: python -m py_compile filepilot/services/history.py -> exit 0
- grep deve casar: page_size em filepilot/services/history.py
Dicas:
- `OrganizationRow` e `OperationRow` usam os mesmos nomes de coluna de 5.3 (L143-186) e a tabela de nomes entre camadas em 16.3.
- Use consultas parametrizadas com `?`.

### filepilot-v1-7-f2 last_undoable e organizacao interrompida
Linhas da SPEC: .abt/SPEC.md L314-334
Arquivos:
- filepilot/services/history.py (novo)
- filepilot/db/connection.py (novo)
- tests/services/test_last_undoable.py (novo)
Criterios de aceite:
- `last_undoable` devolve `None` sem organizacoes, para a ultima com `moved_count` 0 e para a ultima `desfeita`, e devolve a linha para `concluida` ou `interrompida` com `moved_count` maior ou igual a 1.
- Nao ha retrocesso: se a ultima nao e desfazivel, uma anterior desfazivel nao e devolvida.
- Ao abrir o banco, toda linha `em_andamento` vira `interrompida`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_last_undoable.py -> exit 0
- grep deve casar: interrompida em filepilot/db/connection.py
Dicas:
- A ultima organizacao e a de maior `started_at`, com desempate por `id` (SPEC 6.4, ultimo bloco).
- A conversao acontece em `open_connection`, criada no item filepilot-v1-1.

### filepilot-v1-7-f3 undo_last restaura os arquivos e limpa pastas vazias
Linhas da SPEC: .abt/SPEC.md L335-350
Arquivos:
- filepilot/services/undo.py (novo)
- tests/services/test_undo.py (novo)
Criterios de aceite:
- `undo_last` devolve cada arquivo ao caminho e nome originais (inclusive os que receberam sufixo), grava `restaurado`, deixa a organizacao `desfeita` com `undone_at` preenchido e `last_undoable` passa a devolver `None`.
- Subpastas de destino que ficam vazias sao removidas com `Path.rmdir`, subindo pelo pai ate a pasta escolhida (que nunca e removida); pasta com arquivo permanece.
- Arquivo apagado vira `nao_restaurado` com "arquivo não está mais no destino"; caminho original ocupado vira `nao_restaurado` com "caminho original ocupado"; os demais sao restaurados e nada e sobrescrito.
- Durante uma organizacao em andamento `undo_last` levanta `ORGANIZACAO_EM_ANDAMENTO`; sem organizacao desfazivel levanta `NADA_PARA_DESFAZER`.
Verificacao:
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest tests/services/test_undo.py -> exit 0
- parser: python -m py_compile filepilot/services/undo.py -> exit 0
- grep deve casar: OPERATION_LOCK em filepilot/services/undo.py
- grep nao deve casar: shutil.rmtree em filepilot/services
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Percorra as operacoes `movido` por `seq` decrescente; grave cada status com `commit` na hora.
- A guarda e sempre aplicada, sem parametro: cada `source_path` precisa ficar dentro de `folder_path` da organizacao (NFR-001).
- `OPERATION_LOCK` vem de filepilot/services/organizer.py (item filepilot-v1-5).

## Gates do item
- typecheck: python -m mypy --platform win32 filepilot -> exit 0
- testes: pytest -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
