# filepilot-v1-3 - Servico de regras personalizadas
Epico: filepilot-v1 | Ordem: 3 | Pontos: 5 | Depende de: filepilot-v1-1

## Objetivo
O servico rules cria, edita, exclui, lista e reordena regras personalizadas com validacao por campo, extensoes normalizadas e posicoes sem lacuna.

## Contexto herdado
-

## Features

### filepilot-v1-3-f1 Criar e listar regras com validacao por campo
Linhas da SPEC: .abt/SPEC.md L351-376
Arquivos:
- filepilot/services/rules.py (novo)
- tests/services/test_rules.py (novo)
Criterios de aceite:
- `create_rule` com extensoes `PDF` e `.xlsx` grava `pdf` e `xlsx` e coloca a regra na ultima posicao; `list_rules` devolve as regras por `position` crescente.
- Nome vazio ou com mais de 60 caracteres, extensao `a-b` ou vazia e destinos `..\x`, `.`, `a//b`, `CON`, `a:b` e `C:\x` levantam `REGRA_INVALIDA` com `fields` e o texto exato de 6.6 para `name`, `extensions` e `destination_folder`.
- Destino com varios segmentos como `Trabalho/Planilhas` e valido e fica gravado como informado.
- Extensao repetida na mesma regra e unida; extensao ja usada em outra regra e permitida.
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest tests/services/test_rules.py -> exit 0
- parser: python -m py_compile filepilot/services/rules.py -> exit 0
- grep deve casar: Informe uma subpasta válida dentro da pasta escolhida. em filepilot/services/rules.py
- grep nao deve casar: -P '[\x{2010}-\x{2015}\x{2018}-\x{201F}]' em filepilot
Dicas:
- Normalizacao da extensao: `strip`, remover um `.` inicial, minusculas e casar `^[a-z0-9]{1,15}$`.
- Nomes reservados do Windows: `CON`, `PRN`, `AUX`, `NUL`, `COM1` a `COM9`, `LPT1` a `LPT9`; segmento nao pode terminar em ponto ou espaco.
- O tipo `Rule` vem de filepilot/domain/models.py (item filepilot-v1-1).

### filepilot-v1-3-f2 Editar, excluir e reordenar sem violar UNIQUE
Linhas da SPEC: .abt/SPEC.md L351-376
Arquivos:
- filepilot/services/rules.py (novo)
- tests/services/test_rules_order.py (novo)
Criterios de aceite:
- `update_rule` altera nome, extensoes e destino e mantem a `position`; id inexistente levanta `REGRA_NAO_ENCONTRADA`.
- `delete_rule` e `move_rule` em 4 regras mantem as posicoes de 1 a 4 sem lacuna e sem violar `UNIQUE (position)`.
- `move_rule` com posicao fora de 1 ate o total levanta `REGRA_INVALIDA` com `fields["position"]` igual a "Posição inválida.".
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest tests/services/test_rules_order.py -> exit 0
- parser: python -m py_compile filepilot/services/rules.py -> exit 0
- grep deve casar: position = -position em filepilot/services/rules.py
Dicas:
- Reordene em duas etapas na mesma transacao: primeiro as posicoes afetadas viram negativas e depois recebem o valor final (SPEC 6.6, ultimo item).
- Cada gravacao e uma transacao unica: regra e extensoes entram juntas ou nao entram.

### filepilot-v1-3-f3 Persistencia das regras e preservacao do historico
Linhas da SPEC: .abt/SPEC.md L187-215
Arquivos:
- filepilot/services/rules.py (novo)
- tests/services/test_rules_storage.py (novo)
Criterios de aceite:
- As extensoes ficam em `rule_extensions` (uma linha por extensao) e `delete_rule` as apaga junto (ON DELETE CASCADE).
- Excluir uma regra nao altera `operations.rule_name` ja gravado (teste com uma operacao de historico inserida antes).
- Falha na gravacao das extensoes desfaz a gravacao da regra (teste com extensao invalida forcada).
Verificacao:
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest tests/services/test_rules_storage.py -> exit 0
- grep deve casar: rule_extensions em filepilot/services/rules.py
- grep nao deve casar: FOREIGN KEY (rule_name em filepilot/db/migrations.py
Dicas:
- `operations.rule_name` e uma copia em texto, nunca chave estrangeira (SPEC 5.3, L143-186).
- Use consultas parametrizadas (`?`), nunca concatene nome de regra em SQL (SPEC 11).

## Gates do item
- typecheck: mypy . --no-error-summary -> exit 0
- testes: pytest -> exit 0
- awk do Passo 6 sem saida: awk 'FNR == 1 { f = 0 } { t = $0; sub(/^[ \t]+/, "", t) } t ~ /^```/ { f = !f; next } !f && /§EPIC-[a-z0-9][a-z0-9-]*-[0-9]+/ { print FILENAME ":" FNR ": " $0 }' .abt/SPEC.md .abt/items/filepilot-v1/*.md
