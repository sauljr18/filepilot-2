# Itens - FilePilot v1 organizador de arquivos para Windows

Epico: filepilot-v1
Titulo do epico: FilePilot v1 organizador de arquivos para Windows
**Data:** 2026-10-11
**Modo:** completo

## 1. Itens

| Ordem | item_id | Titulo | Pontos | Depende de | Objetivo |
|---|---|---|---|---|---|
| 1 | filepilot-v1-1 | Fundacao: projeto, dominio, banco e CI Windows | 5 | - | Projeto Python 3.12 instalavel, com pacotes domain e db, as cinco tabelas pela migracao 0001_initial e um workflow que roda o pytest no windows-latest |
| 2 | filepilot-v1-2 | Leitura da pasta e pastas protegidas | 4 | filepilot-v1-1 | scan_folder lista os arquivos elegiveis do nivel da pasta e recusa pastas invalidas, vazias, protegidas e de rede com o erro certo |
| 3 | filepilot-v1-3 | Servico de regras personalizadas | 5 | filepilot-v1-1 | O servico rules cria, edita, exclui, lista e reordena regras com validacao por campo e posicoes sem lacuna |
| 4 | filepilot-v1-4 | Planejamento das operacoes e conflitos de nome | 6 | filepilot-v1-1,filepilot-v1-2 | build_plan calcula a lista de operacoes com categoria padrao, precedencia de regra, sufixo de nome repetido e guarda de pasta, sem tocar no disco |
| 5 | filepilot-v1-5 | Organizacao com historico por arquivo | 5 | filepilot-v1-1,filepilot-v1-4 | organize move os arquivos do plano com os.rename, grava cada operacao com commit imediato, reporta progresso e nunca sobrescreve |
| 6 | filepilot-v1-6 | Verificacoes de destino e textos de falha | 3 | filepilot-v1-5 | A organizacao recusa caminho acima de 259 caracteres e subpasta de destino que e atalho, e grava os textos amigaveis de falha por arquivo |
| 7 | filepilot-v1-7 | Historico e desfazer a ultima organizacao | 6 | filepilot-v1-1,filepilot-v1-5 | Os servicos history e undo listam organizacoes e operacoes e devolvem os arquivos da ultima organizacao ao caminho e ao nome originais |
| 8 | filepilot-v1-8 | Janela principal, abas e instancia unica | 3 | filepilot-v1-1 | python -m filepilot abre a MainWindow com as abas Organizar, Historico e Regras, com instancia unica e bloqueio de fechamento durante a organizacao |
| 9 | filepilot-v1-9 | Aba Organizar: pasta, lista e simulacao | 5 | filepilot-v1-2,filepilot-v1-3,filepilot-v1-4,filepilot-v1-8 | Na aba Organizar a pessoa escolhe a pasta, ve cada arquivo com categoria e destino e roda a simulacao sem alterar nada |
| 10 | filepilot-v1-10 | Aba Organizar: execucao com barra de progresso | 5 | filepilot-v1-5,filepilot-v1-6,filepilot-v1-9 | O botao Organizar executa o plano em thread de trabalho com barra de progresso, conferencia da simulacao e resumo de movidos e falhas |
| 11 | filepilot-v1-11 | Aba Historico e desfazer na interface | 5 | filepilot-v1-7,filepilot-v1-9,filepilot-v1-10 | A aba Historico lista organizacoes e detalhes, o botao Ver detalhes abre a organizacao com falhas e o botao Desfazer restaura a ultima organizacao |
| 12 | filepilot-v1-12 | Aba Regras e dialogo de regra | 5 | filepilot-v1-3,filepilot-v1-8 | A aba Regras permite criar, editar, excluir com confirmacao e reordenar regras pelo dialogo, com a mensagem exata por campo invalido |
| 13 | filepilot-v1-13 | Executavel Windows com PyInstaller e CI | 3 | filepilot-v1-10,filepilot-v1-11,filepilot-v1-12 | O workflow gera no windows-latest a pasta FilePilot com o executavel em modo onedir e publica o zip como artefato |

## 2. Criterios de aceite

- filepilot-v1-1:
  - `pip install -e .[dev]` termina com exit 0 no Python 3.12.
  - `pytest` termina com exit 0, com teste que abre a conexao e confere as 5 tabelas criadas e `PRAGMA foreign_keys` igual a 1.
  - Abrir o banco duas vezes deixa `schema_migrations` com exatamente 1 linha (version 1).
  - Inserir em `operations` um status fora de movido, falha, restaurado e nao_restaurado levanta `sqlite3.IntegrityError`.
  - O workflow no runner `windows-latest` roda `pytest` e termina verde.
- filepilot-v1-2:
  - Em `tmp_path` com 3 arquivos visiveis, 1 pasta e 1 arquivo oculto, `scan_folder` devolve exatamente os 3 arquivos, ordenados por nome sem diferenciar maiusculas.
  - A extensao de `a.tar.gz`, `.gitignore` e `b.` vale `gz`, vazio e vazio.
  - Raiz de unidade, `%SystemRoot%`, `%ProgramFiles%` e `\\servidor\pasta` levantam `PASTA_PROTEGIDA`; pasta inexistente levanta `PASTA_INVALIDA`; pasta sem arquivos levanta `PASTA_VAZIA`.
  - Link simbolico para arquivo nao aparece na lista.
- filepilot-v1-3:
  - `create_rule` com extensoes `PDF` e `.xlsx` grava `pdf` e `xlsx` e coloca a regra na ultima posicao.
  - Nome vazio, extensao `a-b` e destinos `..\x`, `.`, `CON` e `a:b` levantam `REGRA_INVALIDA` com `fields` e o texto exato de 6.6.
  - `delete_rule` e `move_rule` em 4 regras mantem as posicoes de 1 a 4 sem lacuna e sem violar `UNIQUE (position)`.
  - Excluir uma regra nao altera `operations.rule_name` ja gravado.
- filepilot-v1-4:
  - Com `fatura.pdf`, `foto.JPG` e `setup.exe`, `build_plan` devolve 2 operacoes (Documentos e Imagens) e 1 arquivo em `skipped`.
  - A regra de menor `position` vence regra posterior e a categoria padrao, e `rule_name` guarda a vencedora.
  - Destino com `fatura.pdf` ja existente gera `fatura (1).pdf`, com `(1)` existente gera `(2)`, e `arquivo.tar.gz` vira `arquivo.tar (1).gz`.
  - Destino que resolve fora da pasta escolhida levanta `DESTINO_FORA_DA_PASTA` e nenhum plano e devolvido.
  - A arvore da pasta e identica antes e depois de `build_plan`.
- filepilot-v1-5:
  - `organize` em `tmp_path` move os N arquivos do plano e grava 1 `organizations` (status `concluida`, `moved_count` igual a N) e N `operations` `movido` com `seq` de 1 a N.
  - `progress_callback` e chamado N+1 vezes, com `done` de 0 ate N.
  - Arquivo criado no destino entre o plano e a execucao faz o novo receber o sufixo (1) e o existente manter o mesmo conteudo.
  - `PermissionError` simulado em 1 arquivo grava `falha` com `destination_path` NULL e os demais arquivos sao movidos.
  - Uma segunda chamada de `organize` durante a primeira levanta `ORGANIZACAO_EM_ANDAMENTO`.
- filepilot-v1-6:
  - Destino com mais de 259 caracteres vira `falha` com "caminho de destino muito longo" e nenhum `os.rename` e chamado para ele.
  - Subpasta `Documentos` que e junction ou link para fora da pasta resulta em `falha` com "a subpasta de destino é um atalho" para todos os arquivos desse destino e zero arquivos fora da pasta (teste no `windows-latest`).
  - `error_message` usa "arquivo em uso por outro programa" para `winerror` 32, "sem permissão para mover o arquivo" para outro `PermissionError`, "arquivo não encontrado" para `FileNotFoundError`, "não foi possível criar a subpasta de destino" para falha de `mkdir` e "erro ao mover o arquivo" para outro `OSError`.
  - Teste de repositorio: `os.replace`, `shutil.move`, `os.remove`, `Path.unlink`, `shutil.rmtree` e importacao de `socket`, `http`, `urllib` ou `requests` aparecem 0 vezes em `filepilot`.
- filepilot-v1-7:
  - `list_organizations` ordena por `started_at` decrescente, pagina em 50 e devolve `items` vazio e `total` 0 sem registros.
  - `last_undoable` devolve `None` para ultima com `moved_count` 0, para ultima `desfeita` e sem organizacoes, e devolve a linha para `concluida` ou `interrompida` com `moved_count` maior ou igual a 1.
  - `undo_last` devolve cada arquivo ao caminho e nome originais (inclusive os com sufixo), marca `restaurado`, remove subpastas de categoria vazias e deixa a organizacao `desfeita` com `undone_at` preenchido.
  - Arquivo apagado ou caminho original ocupado vira `nao_restaurado` com o texto de 6.5, os demais voltam e nenhum arquivo e sobrescrito.
  - Ao abrir o banco, linha `em_andamento` vira `interrompida`.
- filepilot-v1-8:
  - Com pytest-qt em modo offscreen, `python -m filepilot` abre a `MainWindow` com as abas "Organizar", "Histórico" e "Regras".
  - Segunda abertura com o `QLockFile` tomado mostra "O FilePilot já está aberto." e termina com codigo 0 sem criar janela nem abrir o banco.
  - `closeEvent` com `organizing` verdadeiro ignora o fechamento e mostra "Aguarde a organização terminar para fechar."; com `organizing` falso fecha e libera a trava.
  - Falha em `open_connection` mostra "Não foi possível acessar o histórico do FilePilot." e termina com codigo 1.
- filepilot-v1-9:
  - Escolher uma pasta com 5 arquivos mostra "5 arquivos na pasta" e 5 linhas com as colunas Arquivo, Extensão, Categoria, Destino e Regra.
  - Pasta vazia, ilegivel ou protegida mostra a mensagem de 6 e deixa Simular e Organizar desabilitados.
  - Depois de criar uma regra, Simular relê a pasta e mostra "Regra personalizada" na coluna Categoria e o nome da regra na coluna Regra, com o resumo "Simulação: N operações. Nenhum arquivo foi alterado." e a arvore da pasta identica.
  - Plano vazio mostra "Não há operações para executar." e deixa Organizar desabilitado; Atualizar descarta a simulacao exibida.
- filepilot-v1-10:
  - Organizar roda em `QThread` e a barra vai de 0 a N com o texto "k de N arquivos", terminando em 100% e no resumo "Concluído: X movidos, Y falhas.".
  - Durante a organizacao, Simular, Organizar, Atualizar e Escolher pasta ficam desabilitados e `MainWindow.organizing` e verdadeiro; ao fim volta a falso.
  - Com simulacao exibida diferente do plano recalculado, nada e movido e aparece "A pasta mudou desde a simulação. Confira a nova simulação e clique em Organizar de novo.".
  - Excecao inesperada no worker mostra "Ocorreu um erro inesperado. Tente de novo." e a janela continua aberta.
- filepilot-v1-11:
  - A aba Historico lista as organizacoes da mais recente para a mais antiga, com Data e hora no formato dd/MM/yyyy HH:mm, Pasta, Movidos, Falhas e Situação; vazio mostra "Nenhuma organização registrada ainda.".
  - Selecionar uma organizacao mostra Origem, Destino final, Situação e Detalhe de cada arquivo, com "Carregando detalhes..." durante a carga e "Nenhum arquivo nesta organização." quando nao ha operacoes.
  - O botao Ver detalhes so aparece com falhas maiores que 0 e abre a aba Histórico com aquela organizacao selecionada.
  - Desfazer última organização so fica habilitado com `last_undoable`; ao clicar mostra "Desfeito: X arquivos restaurados." (e "Não restaurados: " com os caminhos, se houver) e fica desabilitado.
- filepilot-v1-12:
  - A aba Regras lista as regras por prioridade com Prioridade, Nome, Extensões e Subpasta; vazio mostra a mensagem de 7.5.
  - Salvar uma regra valida fecha o dialogo e a regra aparece selecionada; campo invalido mostra a mensagem exata de 6.6 abaixo do campo sem fechar o dialogo.
  - Excluir mostra "Excluir a regra "<nome>"? O histórico não será alterado." e Cancelar mantem a regra.
  - Subir e Descer reordenam e ficam desabilitados na primeira e na ultima regra.
- filepilot-v1-13:
  - O job no `windows-latest` roda `pyinstaller` em modo `--onedir` e termina com exit 0 gerando `dist/FilePilot/FilePilot.exe`.
  - O job inicia o `.exe` e confirma que o processo continua rodando depois de 5 segundos, sem codigo de saida.
  - O job publica `FilePilot-windows.zip` com a pasta `dist/FilePilot` como artefato do workflow.

## 3. Mapa para a SPEC

- filepilot-v1-1: 3.1 Componentes; 4. Stack e dependencias; 5.1 Arquivo do banco; 5.2 Tabela schema_migrations; 5.3 Tabelas organizations e operations; 5.4 Tabelas rules e rule_extensions; 5.5 Categorias padrao (constantes, nao persistidas); 6. Contratos / Interfaces; 13. Compatibilidade / Migracao
- filepilot-v1-2: 6.1 scanner.scan_folder; 11. Seguranca / Permissoes
- filepilot-v1-3: 5.4 Tabelas rules e rule_extensions; 6.6 rules
- filepilot-v1-4: 5.5 Categorias padrao (constantes, nao persistidas); 6.2 planner.build_plan
- filepilot-v1-5: 5.3 Tabelas organizations e operations; 6.3 organizer.simulate e organizer.organize
- filepilot-v1-6: 6.7 Verificacoes de destino e textos de falha por arquivo; 9. Tratamento de erros; 11. Seguranca / Permissoes
- filepilot-v1-7: 6.4 history; 6.5 undo.undo_last; 5.3 Tabelas organizations e operations
- filepilot-v1-8: 7.1 MainWindow; 9. Tratamento de erros
- filepilot-v1-9: 7.2 OrganizeTab; 7.3 FileTableView; 8.1 Simular e organizar (Ana)
- filepilot-v1-10: 7.2 OrganizeTab; 8.1 Simular e organizar (Ana); 6.3 organizer.simulate e organizer.organize
- filepilot-v1-11: 7.2 OrganizeTab; 7.4 HistoryTab; 8.2 Desfazer (Ana); 8.4 Consultar historico (Ana)
- filepilot-v1-12: 7.5 RulesTab e RuleEditorDialog; 8.3 Criar e usar regra (Carlos)
- filepilot-v1-13: 4. Stack e dependencias; 13. Compatibilidade / Migracao; 14. Plano de entrega

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| Testes que dependem do Windows (atributos oculto e sistema, arquivo em uso, junction, tipo de unidade) so rodam no windows-latest; sem o workflow cedo, filepilot-v1-2, filepilot-v1-5 e filepilot-v1-6 ficam sem verificacao | Alto | O workflow nasce em filepilot-v1-1 e e gate dos itens 2, 5, 6 e 7 |
| filepilot-v1-5 e filepilot-v1-6 concentram NFR-001, NFR-002, a trava e os textos de falha; item unico passaria de 8 pontos | Alto | Ja divididos em dois itens; manter a divisao no detalhe dos itens |
| Worker em QThread, sinais Qt e pytest-qt sem display nos itens 8 a 12 | Medio | Gates dos itens de interface usam QT_QPA_PLATFORM offscreen e testam o worker pelos sinais |
| Executavel sem assinatura pode disparar aviso do SmartScreen ou de antivirus em filepilot-v1-13 (risco D-003 do PRD) | Medio | Aceito na v1; o CI confere que o .exe sobe |
| os.path.isjunction, os.rename e st_file_attributes se comportam diferente fora do Windows | Medio | Isolar em funcoes pequenas, com skipif e mocks em Linux, como diz a SPEC 13 |
| Marcas DECISAO do Gabriel sem aprovacao explicita da pessoa podem ser contestadas na implementacao | Baixo | Os itens citam as secoes da SPEC; mudar uma decisao pede nova execucao |

## 5. Cobertura

| Requisito | Itens que cobrem |
|---|---|
| FR-001 | filepilot-v1-2, filepilot-v1-9 |
| FR-002 | filepilot-v1-1, filepilot-v1-2, filepilot-v1-4, filepilot-v1-9 |
| FR-003 | filepilot-v1-4, filepilot-v1-5, filepilot-v1-9 |
| FR-004 | filepilot-v1-5 |
| FR-005 | filepilot-v1-10 |
| FR-006 | filepilot-v1-4, filepilot-v1-5 |
| FR-007 | filepilot-v1-5, filepilot-v1-6, filepilot-v1-10 |
| FR-008 | filepilot-v1-1, filepilot-v1-5, filepilot-v1-7, filepilot-v1-11 |
| FR-009 | filepilot-v1-7, filepilot-v1-11 |
| FR-010 | filepilot-v1-3, filepilot-v1-12 |
| FR-011 | filepilot-v1-4, filepilot-v1-9 |
| NFR-001 | filepilot-v1-4, filepilot-v1-5, filepilot-v1-6 |
| NFR-002 | filepilot-v1-5, filepilot-v1-7 |
| US-001 | filepilot-v1-2, filepilot-v1-9 |
| US-002 | filepilot-v1-2, filepilot-v1-9 |
| US-003 | filepilot-v1-4, filepilot-v1-5, filepilot-v1-9 |
| US-004 | filepilot-v1-4, filepilot-v1-9 |
| US-005 | filepilot-v1-5, filepilot-v1-10 |
| US-006 | filepilot-v1-5, filepilot-v1-10 |
| US-007 | filepilot-v1-4, filepilot-v1-5 |
| US-008 | filepilot-v1-5, filepilot-v1-6, filepilot-v1-10 |
| US-009 | filepilot-v1-7, filepilot-v1-11 |
| US-010 | filepilot-v1-7, filepilot-v1-11 |
| US-011 | filepilot-v1-3, filepilot-v1-12 |
| US-012 | filepilot-v1-3, filepilot-v1-12 |

Itens de infraestrutura e entrega sem FR proprio: filepilot-v1-1 (fundacao e CI), filepilot-v1-8 (janela, instancia unica, bloqueio de fechamento) e filepilot-v1-13 (executavel). Nenhum requisito `CORTADO`.
