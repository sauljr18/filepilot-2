# Itens - Correcao de quatro defeitos do FilePilot na leitura de pasta, na ordem da lista e na organizacao

Epico: filepilot-fix
Titulo do epico: Correcao de quatro defeitos do FilePilot na leitura de pasta, na ordem da lista e na organizacao

**Data:** 2026-10-12
**Modo:** so SPEC + itens

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-fix-1 | Laco de atalhos na leitura da pasta vira PASTA_INVALIDA | 2 | filepilot-v1-2 | scan_folder levanta PASTA_INVALIDA, e nao erro interno, quando a resolucao da pasta escolhida entra em laco de atalhos |
| 2 | filepilot-fix-2 | Variavel de ambiente vazia nao torna a pasta atual protegida | 2 | filepilot-fix-1 | SystemRoot, ProgramFiles e ProgramFiles(x86) vazias valem como ausentes e a pasta atual deixa de ser tratada como protegida |
| 3 | filepilot-fix-3 | Ordem estavel da lista de arquivos com nomes que so diferem por maiuscula | 1 | filepilot-v1-2 | scan_folder devolve a mesma ordem em qualquer execucao quando dois nomes so diferem por maiuscula e minuscula |
| 4 | filepilot-fix-4 | Organizacao interrompida e recuperacao ao abrir o banco | 8 | filepilot-v1-6 | uma organizacao nunca fica em andamento depois de BANCO_INDISPONIVEL: vira interrompida na hora, ou ao reabrir o banco, com as contagens das operacoes gravadas |

## 2. Criterios de aceite

- filepilot-fix-1:
  - Com Path.resolve trocado por monkeypatch para levantar RuntimeError, scan_folder levanta FilePilotError com code PASTA_INVALIDA e message igual ao texto de 6, sem o texto Symlink loop.
  - Com OSError de errno.ELOOP na resolucao, o resultado e PASTA_INVALIDA; com errno.EACCES continua sendo OSError.
  - Pasta valida com um link up -> .. dentro dela continua listando so os arquivos regulares.
  - pytest tests/services/test_scanner_loop.py termina com exit 0.
- filepilot-fix-2:
  - Com cada uma das tres variaveis definida como "" ou "   " e a pasta atual igual a tmp_path, scan_folder(tmp_path / "pasta") lista o arquivo e nao levanta PASTA_PROTEGIDA (6 casos).
  - _protected_root("SystemRoot", r"C:\Windows") com a variavel vazia devolve Path(r"C:\Windows").resolve() e nao a pasta atual.
  - O teste existente com SystemRoot apontando para uma pasta de tmp_path continua dando PASTA_PROTEGIDA para as pastas dentro dela.
  - pytest tests/services/test_scanner_protected.py termina com exit 0.
- filepilot-fix-3:
  - Com iterdir trocado por monkeypatch para devolver b.txt, a.txt e A.txt em qualquer das 6 permutacoes, a lista tem os nomes A.txt, a.txt, b.txt nessa ordem.
  - Foto.JPG, foto.jpg e FOTO.jpg dao a mesma lista nas 6 permutacoes de entrada.
  - Nomes que ja diferiam em casefold (beta.txt, Alfa.txt) continuam em ordem alfabetica sem diferenciar maiusculas.
  - pytest tests/services/test_scanner_order.py termina com exit 0.
- filepilot-fix-4:
  - Com a gravacao da segunda operacao de um plano de 3 arquivos falhando, organize levanta BANCO_INDISPONIVEL; a linha fica interrompida com moved_count 1, failed_count 0 e finished_at preenchido; conn.in_transaction e False; o arquivo da segunda operacao esta no lugar original.
  - Com o UPDATE de fechamento falhando por gatilho, a linha fica interrompida com as contagens finais; com a linha ja concluida, o helper nao altera status, contagens nem finished_at.
  - open_connection sobre um banco com uma organizacao em_andamento e 3 operacoes (2 movido e 1 falha) a deixa interrompida com moved_count 2 e failed_count 1; linhas concluida, interrompida e desfeita ficam identicas.
  - Depois da falha, OPERATION_LOCK.acquire(blocking=False) devolve True; os testes de last_undoable usam a condicao em SQL de 6.4, sem importar history.
  - pytest tests/services/test_organizer_interrupted.py tests/db/test_connection_recovery.py termina com exit 0.

## 3. Mapa para a SPEC

- filepilot-fix-1: 27.2 D1: pasta com laco de atalhos e pasta invalida (substitui o tratamento de resolve de 6.1).
- filepilot-fix-2: 27.3 D2: variavel de ambiente vazia vale como ausente (substitui a frase das variaveis de 6.1).
- filepilot-fix-3: 27.4 D3: ordem total e repetivel da lista de arquivos (substitui a frase de ordenacao de 6.1).
- filepilot-fix-4: 27.5 D4: banco indisponivel no meio da organizacao (substitui a frase de falha de sqlite3.Error de 6.3 e implementa a recuperacao de 5.3).
- Contexto de todos: 27.1 Objetivo e fora de escopo.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| A recuperacao ao abrir o banco tambem consta em filepilot-v1-7-f2 (na fila), que nao recalcula as contagens; a opcao A foi confirmada: filepilot-fix-4 e o dono | Alto | Retirar de filepilot-v1-7-f2 o criterio Ao abrir o banco, toda linha em_andamento vira interrompida, numa mudanca a parte feita pela pessoa; sem isso os dois itens implementam a mesma funcao em connection.py |
| last_undoable nao existe no codigo (history.py e de filepilot-v1-7) | Alto | Os testes de filepilot-fix-4 usam a condicao em SQL de 6.4 (status IN concluida, interrompida e moved_count >= 1) |
| filepilot-v1-6 esta implementando e reescreve organizer.py | Medio | filepilot-fix-4 depende de filepilot-v1-6; o detalhe cita as funcoes _run, _open_organization e _close_organization, nao so numeros de linha |
| filepilot-fix-1 e filepilot-fix-2 alteram a mesma funcao, _is_protected | Medio | filepilot-fix-2 depende de filepilot-fix-1 |
| filepilot-fix-3 altera scan_folder perto do trecho de filepilot-fix-1 | Baixo | Rebase trivial; sem dependencia |
| Teste com laco real e link up -> .. pode falhar no Windows sem privilegio | Baixo | Os testes preveem pytest.skip e os testes por monkeypatch cobrem os dois sistemas |
| A recuperacao ao abrir o banco assume que nenhuma organizacao esta em curso (7.1: conexao e instancia unicas) | Baixo | Registrar a premissa no item; nenhuma acao extra |

## 5. Cobertura

| Item do escopo | Item que o cobre |
|---|---|
| F1: laco de atalho na leitura de pasta vira pasta invalida | filepilot-fix-1 |
| F2: SystemRoot vazia nao torna a pasta atual protegida | filepilot-fix-2 |
| F3: ordem da lista estavel com nomes que so diferem por maiuscula e minuscula | filepilot-fix-3 |
| F4: banco indisponivel no meio da organizacao encerra a organizacao | filepilot-fix-4 |
| F5: um item de correcao com ao menos um teste por defeito | filepilot-fix-1, filepilot-fix-2, filepilot-fix-3 e filepilot-fix-4 |
