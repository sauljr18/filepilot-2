# Relatorio de Prontidao para o Fatiamento: FilePilot

**Data:** 2026-10-11
**Modo:** completo

## 1. Cobertura de Requisitos

| Requisito | Elemento da SPEC | Status |
|---|---|---|
| FR-001 Selecao de pasta | 6.1 `scan_folder` (inclui `PASTA_PROTEGIDA`); 7.2 `FolderBar`, `QFileDialog`; 8.1 | coberto |
| FR-002 Identificacao por extensao e categorizacao | 5.5 categorias; 6.1; 6.2 `build_plan`; 7.3 `FileTableView` | coberto |
| FR-003 Simulacao (dry-run) | 6.2 `build_plan`; 6.3 `simulate`; 7.2 botao "Simular" (relê a pasta) | coberto |
| FR-004 Organizacao em subpastas | 5.3 `operations`; 6.3 `organize`; 6.7 verificacoes | coberto |
| FR-005 Barra de progresso | 6.3 `progress_callback`; 7.2 `QProgressBar` e `OrganizeWorker` | coberto |
| FR-006 Conflito de nome no destino | 6.2 sufixo ` (n)`; 6.3 passo 3 | coberto |
| FR-007 Falha por arquivo | 5.3 status `falha`; 6.3 passo 5; 6.7 textos | coberto |
| FR-008 Historico de operacoes | 5.3; 6.4 `history`; 7.4 `HistoryTab` | coberto |
| FR-009 Desfazer a ultima organizacao | 6.4 `last_undoable`; 6.5 `undo_last`; 7.2 botao "Desfazer" | coberto |
| FR-010 Gestao de regras personalizadas | 5.4; 6.6 `rules`; 7.5 `RulesTab` e `RuleEditorDialog` | coberto |
| FR-011 Aplicacao das regras | 6.2 precedencia; 6.6 posicao; 7.3 coluna "Regra" | coberto |
| NFR-001 Seguranca dos arquivos | 6.2 guarda; 6.3 `os.rename`; 6.7; 11 | coberto |
| NFR-002 Integridade do historico | 6.3 `commit` por operacao; 5.3 `seq` | coberto |

**Lacunas:** 0. Nenhum requisito `parcial`, `ausente` ou `CORTADO` (o `stack-decision.md` nao corta requisito). Cobertura conferida na SPEC, nao so na Traceability Matrix (16.1 a 16.3). Itens `[DECISAO: ...]` sem FR (instancia unica, `PASTA_PROTEGIDA`, botao "Atualizar", textos amigaveis de falha, entre outros) estao na matriz com Status `-` e entram no fatiamento junto das partes a que pertencem.

## 2. Mapa de Dependencias

| Parte | Depende de |
|---|---|
| P1 Fundacao: `pyproject.toml`, `domain` (categorias, modelos incluindo `Rule`, erros), `db` (conexao, migracao `0001_initial`), workflow de testes no runner `windows-latest` | - |
| P2 `scanner` (leitura do nivel, ocultos e sistema, links, `PASTA_PROTEGIDA`, pasta de rede) | P1 |
| P3 `rules` (CRUD, validacao, reordenacao em duas etapas) | P1 |
| P4 `planner` (categorias, precedencia de regra, sufixo de conflito, guarda de pasta) | P1, P2 |
| P5 `organizer` (`organize`, `simulate`, trava, `commit` por operacao, 6.7, textos de falha) | P1, P4 |
| P6 `history` e `undo` (`list_organizations`, `get_organization_detail`, `last_undoable`, `undo_last`) | P1, P5 |
| P7 UI base: `MainWindow`, abas, instancia unica (`QLockFile`), abertura do banco, bloqueio de fechamento | P1 |
| P8 UI Organizar, leitura e simulacao: `OrganizeTab`, `FolderBar`, `FileTableView`, "Atualizar", "Simular" | P2, P3, P4, P7 |
| P9 UI Organizar, execucao: `OrganizeWorker`, barra, conferencia do plano, resumo, "Ver detalhes" | P5, P8 |
| P10 UI Historico e desfazer: `HistoryTab`, `show_organization`, botao "Desfazer ultima organizacao" | P6, P8, P9 |
| P11 UI Regras: `RulesTab`, `RuleEditorDialog`, confirmacao de exclusao | P3, P7 |
| P12 Empacotamento: script PyInstaller `--onedir` e job de build no `windows-latest` | P1 a P11 |

**Dependencias criticas:** P1 (bloqueia todas as outras 11 partes); P4 (bloqueia P5, P8 e, por P5, P6, P9 e P10); P5 (bloqueia P6, P9 e P10). Infraestrutura: o runner `windows-latest` (em P1) precisa existir antes dos testes que dependem do Windows (atributos de arquivo oculto, arquivo em uso `WinError 32`, junction). Nenhuma dependencia com epicos ou itens ja existentes: o projeto nao tem nenhum.

## 3. Guia de Tamanho para o Fatiamento

| Parte | Complexidade | Pontos |
|---|---|---|
| P1 Fundacao | Simples | 3 |
| P2 `scanner` | Medio | 4 |
| P3 `rules` | Medio | 5 |
| P4 `planner` | Complexo | 6 |
| P5 `organizer` | Complexo | 8 (no limite; ver risco R2, sugestao de dividir em nucleo `organize` com historico e em verificacoes 6.7 com textos de falha) |
| P6 `history` e `undo` | Complexo | 6 |
| P7 UI base | Simples | 3 |
| P8 UI leitura e simulacao | Medio | 5 |
| P9 UI execucao | Medio | 5 |
| P10 UI historico e desfazer | Medio | 5 |
| P11 UI regras | Medio | 5 |
| P12 Empacotamento | Simples | 3 |

Nenhuma parte acima de 8 pontos. A UI de "Organizar" foi dimensionada ja dividida em P8 e P9: junta, passaria de 8 pontos, com mais de 5 subcomportamentos (maquina de modos, leitura, simulacao, "Atualizar", worker, progresso, conferencia do plano, "Ver detalhes") e mais de 3 componentes; por isso o fatiamento mantem a divisao.

## 4. Riscos

| Risco | Severidade | Acao |
|---|---|---|
| R1: testes que dependem do Windows (atributos oculto e sistema, arquivo em uso, junction, `GetDriveTypeW`) so rodam no `windows-latest`; sem o workflow cedo, FR-007, NFR-001 e a guarda de junction ficam sem verificacao | Alto | Criar o workflow de testes no `windows-latest` ja em P1 e exigi-lo como gate dos itens P2, P5 e P6 |
| R2: P5 concentra NFR-001, NFR-002, a trava, 6.7 e a tabela de textos de falha em 8 pontos; estouro de tamanho derruba o item | Alto | Dividir P5 em dois itens (nucleo de `organize` com historico, depois verificacoes 6.7 com textos) no fatiamento |
| R3: `OrganizeWorker` em `QThread`, sinais Qt e pytest-qt sem display | Medio | Definir `QT_QPA_PLATFORM=offscreen` nos gates de P7 a P11 e testar o worker pelos sinais |
| R4: executavel sem assinatura pode disparar aviso do SmartScreen ou de antivirus (D-003 do PRD) | Medio | Aceito na v1; registrar no gate de P12 e testar o `.exe` no runner |
| R5: `os.path.isjunction`, `os.rename` e `st_file_attributes` tem comportamento diferente fora do Windows | Medio | Isolar chamadas em funcoes pequenas, com `pytest.mark.skipif` e mocks em Linux, como diz a SPEC 13 |
| R6: marcas `[DECISAO: <motivo>]` do Gabriel sem aprovacao explicita (13 no relatorio do Rafael) podem ser contestadas na implementacao | Baixo | Os itens citam as linhas da SPEC; mudanca de decisao pede nova execucao |
| R7: nenhuma pendencia do relatorio do Rafael (status `APROVAVEL`) | Baixo | Nenhuma acao |

## 5. Prontidao

**MVP pronto:** Sim - o MVP e a jornada da Ana (US-001 a US-010: escolher pasta, listar, simular, organizar com progresso, historico e desfazer) mais as regras do Carlos (US-011 e US-012), que fazem parte da v1. O caminho critico e P1, P2, P4, P5, P7, P8, P9, P6 e P10, todos com no maximo 8 pontos e na ordem das dependencias; no modo completo, o primeiro item e a fundacao (P1: projeto, dominio, banco e CI), sem funcionalidade de produto. Estimativa: 13 itens (P1 a P12, com P5 em dois itens).

## 6. Dados para o fatiamento

- Epicos ja usados no projeto (`abt epic list --ids --json`): nenhum.
- Itens ja usados no projeto (`abt queue list --json`): nenhum.
- Dependencias com itens existentes: nenhuma.
- Os ids do epico e dos itens nao foram escolhidos aqui: quem escolhe e o fatiamento, no formato `^[a-z0-9][a-z0-9-]{1,39}$`.

Pronto para fatiamento: SIM
