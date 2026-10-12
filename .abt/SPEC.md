# SPEC - filepilot-2

Documento de especificacao deste projeto. As secoes dos itens integrados
entram ao fim deste arquivo, uma por item, no formato `## §N <titulo>`,
escritas por `abt integrate apply`.

Projeto: filepilot-2

**Gerada em:** 2026-10-11
**Baseada em:** prd.md e stack-decision.md da execucao 20261011-212601

## 1. Objetivo

O FilePilot e um aplicativo desktop para Windows que organiza os arquivos de uma pasta escolhida em subpastas por categoria (Documentos, Imagens, Videos e Compactados), com regras personalizadas, e que mostra antes, em uma simulacao (dry-run), tudo o que vai acontecer sem alterar nenhum arquivo.

O publico e formado por Ana, usuaria domestica que quer a pasta Downloads em ordem com poucos cliques e sem medo de perder arquivo, e Carlos, que cria regras para o proprio jeito de guardar. A confianca vem de tres garantias: a simulacao nao altera nada, nenhum arquivo e sobrescrito e a ultima organizacao pode ser desfeita.

### 1.1 Resultado esperado

- Uma janela unica com tres abas (Organizar, Historico, Regras) que cobre FR-001 a FR-011.
- Pacote `filepilot` em Python 3.12 com camadas separadas: dominio, servicos, banco e interface.
- Banco SQLite local com historico por arquivo e regras (secao 5).
- Suite pytest que roda sem janela para a logica e com pytest-qt para os widgets.
- Executavel para Windows gerado com PyInstaller no runner Windows do GitHub Actions.

### 1.2 Fora de escopo

- Organizacao automatica em segundo plano ou agendada: so roda quando a pessoa pede.
- Subpastas internas da pasta escolhida: so os arquivos do nivel da pasta sao organizados.
- Versoes para macOS e Linux: so Windows.
- Sincronizacao com nuvem e organizacao por conteudo do arquivo: so por extensao e regras.
- Recursos de rede e organizacao por inteligencia artificial.
- Renomear arquivos, exceto o sufixo automatico de nome repetido no destino.
- Desfazer organizacoes anteriores a ultima.
- Subpasta "Outros": arquivo sem categoria e sem regra fica onde esta.
- Requisitos de desempenho, responsividade e escalabilidade: nao definidos pela pessoa que pediu o produto.
- Nenhum requisito do PRD foi `CORTADO` em `## Lacunas Resolvidas` do `stack-decision.md`.

## 2. Glossario

| Termo | Significado |
|---|---|
| Pasta escolhida | Pasta que a pessoa seleciona no explorador; so os arquivos do nivel dela sao tratados |
| Categoria padrao | Uma das quatro categorias fixas do produto (secao 5.5) |
| Regra personalizada | Regra criada por Carlos: nome, extensoes e subpasta de destino |
| Plano | Lista ordenada de operacoes (arquivo, origem, destino, regra) calculada antes de mover qualquer arquivo |
| Simulacao (dry-run) | Exibir o plano sem executa-lo; nao toca no disco nem no historico |
| Organizacao | Execucao real do plano, registrada no historico |
| Operacao | Movimentacao (ou falha de movimentacao) de um arquivo dentro de uma organizacao |
| Sem categoria | Arquivo cuja extensao nao esta em nenhuma categoria padrao nem em regra; nunca e movido |
| Sufixo de conflito | ` (n)` acrescentado ao nome base quando o nome ja existe no destino |
| Desfazer | Devolver os arquivos da ultima organizacao ao caminho original |

## 3. Arquitetura geral

O aplicativo e local e de processo unico. A interface PySide6 chama servicos Python; os servicos usam o sistema de arquivos e o SQLite. A organizacao roda em uma thread de trabalho para a janela nao travar.

```text
+----------------------------- ui (PySide6) -----------------------------+
|  MainWindow > OrganizeTab | HistoryTab | RulesTab | RuleEditorDialog    |
|        |  chama                                   ^ sinais (progresso)  |
+--------|------------------------------------------|--------------------+
         v                                          |
+---------------------------- services -------------------------------------+
| scanner -> planner -> organizer (QThread worker na ui) | undo | rules | history |
+------------|------------------------------|-------------------------------+
             v                              v
     sistema de arquivos             db (sqlite3, filepilot.db)
```

### 3.1 Componentes

| Componente | Modulo | Responsabilidade |
|---|---|---|
| Categorias | `filepilot/domain/categories.py` | Constantes das quatro categorias e suas extensoes |
| Modelos | `filepilot/domain/models.py` | Dataclasses `ScannedFile`, `PlannedOperation`, `Plan`, `OrganizationResult` |
| Erros | `filepilot/domain/errors.py` | `FilePilotError` com `code` e `message` |
| Banco | `filepilot/db/connection.py`, `filepilot/db/migrations.py` | Abrir conexao, `PRAGMA foreign_keys = ON`, aplicar migracoes |
| Scanner | `filepilot/services/scanner.py` | Listar arquivos elegiveis do nivel da pasta (FR-001, FR-002) |
| Planner | `filepilot/services/planner.py` | Categorizar, aplicar regras e calcular destinos (FR-002, FR-003, FR-006, FR-011) |
| Organizer | `filepilot/services/organizer.py` | Executar o plano, registrar historico, reportar progresso (FR-004 a FR-008) |
| Undo | `filepilot/services/undo.py` | Desfazer a ultima organizacao (FR-009) |
| Regras | `filepilot/services/rules.py` | CRUD e ordem das regras (FR-010) |
| Historico | `filepilot/services/history.py` | Consultar organizacoes e operacoes (FR-008) |
| Janela | `filepilot/ui/` | Widgets, worker `OrganizeWorker(QThread)` e mensagens |

### 3.2 Fronteiras

- A interface so chama `filepilot.services`; nunca usa `sqlite3`, `os` ou `shutil` direto.
- `filepilot.services` nunca importa PySide6: o progresso sai por funcao de retorno (`progress_callback`), e a interface a liga a um sinal Qt.
- Todo acesso ao banco passa por `filepilot.db`; so `organizer`, `undo`, `rules` e `history` gravam ou leem tabelas.
- `scanner` e `planner` so leem o disco; apenas `organizer` e `undo` o alteram.
- Nenhum modulo faz chamada de rede.

## 4. Stack e dependencias

| Camada | Tecnologia | Versao | Razao |
|---|---|---|---|
| Linguagem e backend | Python | 3.12 | `pathlib`, `os`, `shutil`, `stat` e `sqlite3` da biblioteca padrao |
| Interface grafica | PySide6 | 6.12.0 | Seletor de pastas nativo, `QProgressBar`, threads |
| Banco de dados | SQLite pelo modulo `sqlite3` | stdlib do Python 3.12 | Arquivo unico local, sem servidor |
| Testes | pytest | 9.1.1 | `tmp_path` para pastas temporarias |
| Testes de interface | pytest-qt | 4.5.0 | Testar widgets do PySide6 |
| Empacotamento | PyInstaller | 6.22.3 | Executavel Windows em modo `--onedir` |
| Build e testes no Windows | GitHub Actions, runner `windows-latest` | - | PyInstaller so gera `.exe` no Windows |

Dependencias novas: nenhuma alem da tabela. O manifesto sera `pyproject.toml` com `requires-python = ">=3.12"`, `PySide6==6.12.0` como dependencia e `pytest==9.1.1`, `pytest-qt==4.5.0` e `pyinstaller==6.22.3` como dependencias de desenvolvimento.

Restricoes vindas de `## Gotchas Conhecidos` do `stack-decision.md`: nenhuma particularidade registrada nas fontes do projeto; nada a acrescentar.

Restricoes vindas de `## Decisoes de Design` do `stack-decision.md`, mantidas aqui:

- A movimentacao usa `os.rename` (falha com `FileExistsError` se o destino existe); `os.replace` e `shutil.move` ficam proibidos nas camadas de execucao.
- Simulacao e organizacao usam a mesma camada de planejamento.
- O banco fica fora da pasta organizada (secao 5.1).
- O build usa `--onedir`; a entrega e a pasta compactada com o `.exe`.

Skill `vuetify-sneat-ui-patterns`: ignorada, porque o projeto nao usa Vuetify (a interface e desktop com PySide6 e nao ha manifesto web).

## 5. Modelo de dados

Banco SQLite local, aberto com `PRAGMA foreign_keys = ON` em toda conexao. Datas sao gravadas como texto ISO 8601 em UTC (`AAAA-MM-DDTHH:MM:SSZ`) `[DECISAO: texto UTC e simples de ordenar e a interface converte para o horario local na exibicao]`. Nomes de colunas seguem snake_case e reaparecem iguais nas dataclasses e na interface `[DECISAO: Python usa snake_case em todas as camadas, o que remove mapeamento de nomes]`.

Isolamento por usuario: nao se aplica. O arquivo `filepilot.db` fica no perfil do usuario do Windows (5.1) e pertence a uma unica pessoa, sem papeis nem contas dentro do aplicativo.

### 5.1 Arquivo do banco

- Caminho: `QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)` com o nome de aplicativo `FilePilot`, mais o arquivo `filepilot.db` `[DECISAO: pasta de dados do aplicativo no perfil do usuario, fora de qualquer pasta que a pessoa organiza]`.
- A interface calcula o caminho e o passa aos servicos (`db_path: Path`); os servicos nao conhecem o Qt. Os testes passam um caminho em `tmp_path`.
- Se a pasta de dados nao existir, `filepilot.db.connection.open_connection` a cria com `Path.mkdir(parents=True, exist_ok=True)`.
- Migracoes: tabela `schema_migrations`; a migracao `0001_initial` cria todas as tabelas abaixo. Migracoes futuras so acrescentam.

### 5.2 Tabela `schema_migrations`

| Coluna | Tipo | Nullable | Default | Descricao |
|---|---|---|---|---|
| version | INTEGER | NAO | - | Numero da migracao aplicada; chave primaria |
| applied_at | TEXT | NAO | - | Data e hora UTC em que foi aplicada |

- Restricoes: `PRIMARY KEY (version)`. Sem chaves estrangeiras. Sem indices adicionais: a leitura e por chave primaria.
- Tabela de infraestrutura: so `filepilot.db.migrations` a le e grava; nenhum servico, endpoint ou componente a consulta `[DECISAO: controle de versao do esquema para migracoes futuras so acrescentarem, sem requisito do PRD que o exija]`.

### 5.3 Tabelas `organizations` e `operations`

`organizations`: uma linha por organizacao real (a simulacao nunca grava).

| Coluna | Tipo | Nullable | Default | Descricao |
|---|---|---|---|---|
| id | INTEGER | NAO | autoincremento | Chave primaria |
| folder_path | TEXT | NAO | - | Caminho absoluto da pasta escolhida |
| started_at | TEXT | NAO | - | Inicio da organizacao (UTC) |
| finished_at | TEXT | SIM | NULL | Fim da organizacao (UTC); NULL enquanto em andamento |
| status | TEXT | NAO | `'em_andamento'` | `em_andamento`, `concluida`, `interrompida` ou `desfeita` |
| moved_count | INTEGER | NAO | 0 | Arquivos movidos com sucesso |
| failed_count | INTEGER | NAO | 0 | Arquivos que falharam |
| undone_at | TEXT | SIM | NULL | Quando o desfazer foi executado (UTC) |
| created_at | TEXT | NAO | - | Criacao da linha (UTC) |
| updated_at | TEXT | NAO | - | Ultima alteracao da linha (UTC) |

- `CHECK (status IN ('em_andamento','concluida','interrompida','desfeita'))`; `CHECK (moved_count >= 0 AND failed_count >= 0)`.
- Indice `idx_organizations_started_at` em `started_at`: a listagem do historico ordena por ela, da mais recente para a mais antiga.
- `interrompida`: ao abrir o banco, toda linha `em_andamento` (aplicativo encerrado no meio) vira `interrompida` `[DECISAO: as operacoes ja gravadas continuam validas e permitem desfazer]`.

`operations`: uma linha por arquivo tratado.

| Coluna | Tipo | Nullable | Default | Descricao |
|---|---|---|---|---|
| id | INTEGER | NAO | autoincremento | Chave primaria |
| organization_id | INTEGER | NAO | - | Organizacao a que pertence |
| seq | INTEGER | NAO | - | Ordem da operacao dentro da organizacao, a partir de 1 |
| source_path | TEXT | NAO | - | Caminho absoluto original do arquivo |
| destination_path | TEXT | SIM | NULL | Caminho absoluto final (com sufixo de conflito); NULL em `falha` |
| category | TEXT | SIM | NULL | Categoria padrao aplicada, ou NULL quando veio de regra |
| rule_name | TEXT | SIM | NULL | Nome da regra no momento da organizacao (copia, nao chave) |
| status | TEXT | NAO | - | `movido`, `falha`, `restaurado` ou `nao_restaurado` |
| error_message | TEXT | SIM | NULL | Motivo da falha ou do nao restaurado |
| created_at | TEXT | NAO | - | Criacao da linha (UTC) |
| updated_at | TEXT | NAO | - | Ultima alteracao da linha (UTC) |

- `FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE ON UPDATE CASCADE`.
- `UNIQUE (organization_id, seq)`; `CHECK (status IN ('movido','falha','restaurado','nao_restaurado'))`.
- `CHECK (status = 'falha' OR destination_path IS NOT NULL)`: so a falha pode nao ter destino.
- Indice `idx_operations_organization_seq` em `(organization_id, seq)`: o detalhe e o desfazer leem as operacoes de uma organizacao em ordem.
- `rule_name` e uma copia para a exclusao de regra nao alterar o historico (US-012); por isso nao e chave estrangeira.
- A aplicacao nunca exclui linhas destas tabelas; o `ON DELETE CASCADE` so protege o banco contra orfaos.

### 5.4 Tabelas `rules` e `rule_extensions`

`rules`: regras personalizadas, na ordem de prioridade.

| Coluna | Tipo | Nullable | Default | Descricao |
|---|---|---|---|---|
| id | INTEGER | NAO | autoincremento | Chave primaria |
| name | TEXT | NAO | - | Nome da regra, de 1 a 60 caracteres |
| destination_folder | TEXT | NAO | - | Subpasta de destino relativa a pasta escolhida |
| position | INTEGER | NAO | - | Ordem na lista, a partir de 1; menor numero prevalece |
| created_at | TEXT | NAO | - | Criacao da linha (UTC) |
| updated_at | TEXT | NAO | - | Ultima alteracao da linha (UTC) |

- `UNIQUE (position)`; `CHECK (length(name) BETWEEN 1 AND 60)`; `CHECK (length(destination_folder) >= 1)`.
- Indice `idx_rules_position` implicito pelo `UNIQUE (position)`: a leitura ordena por `position`.

`rule_extensions`: extensoes cobertas por cada regra, ja normalizadas.

| Coluna | Tipo | Nullable | Default | Descricao |
|---|---|---|---|---|
| id | INTEGER | NAO | autoincremento | Chave primaria |
| rule_id | INTEGER | NAO | - | Regra dona da extensao |
| extension | TEXT | NAO | - | Extensao em minusculas, sem ponto, de 1 a 15 letras ou digitos |

- `FOREIGN KEY (rule_id) REFERENCES rules(id) ON DELETE CASCADE ON UPDATE CASCADE`.
- `UNIQUE (rule_id, extension)`; `CHECK (length(extension) BETWEEN 1 AND 15)`.
- Indice `idx_rule_extensions_extension` em `extension`: o planner busca a regra pela extensao do arquivo.
- Limites de nome (60) e de extensao (15 caracteres alfanumericos) sao `[DECISAO: limites para a validacao ter regra objetiva, ja que o PRD nao os define]`.

### 5.5 Categorias padrao (constantes, nao persistidas)

Definidas em `filepilot/domain/categories.py` como `CATEGORIES: dict[str, CategoryDef]`; a comparacao e feita em minusculas, sem ponto.

| Categoria (`category`) | Subpasta | Extensoes |
|---|---|---|
| `documentos` | `Documentos` | pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx, csv |
| `imagens` | `Imagens` | jpg, jpeg, png, gif, bmp, webp, svg, tiff |
| `videos` | `Videos` | mp4, mkv, avi, mov, wmv, webm |
| `compactados` | `Compactados` | zip, rar, 7z, tar, gz |

- Extensao fora da tabela so e movida por regra personalizada.
- Nenhuma extensao aparece em duas categorias.
- A tabela `operations.category` guarda a chave (`documentos`, ...), nunca o nome da subpasta.
- Carga inicial: nenhuma. O banco nasce sem regras; as categorias nao sao linhas de banco.

## 6. Contratos / Interfaces

Aplicativo local sem HTTP: o contrato e a API Python de `filepilot.services`. Todas as funcoes sao sincronas; a interface chama as de longa duracao em thread de trabalho.

Autenticacao: nao se aplica (aplicativo local, uma pessoa por perfil do Windows). Nenhuma funcao e `[Publico]` nem restrita.

Erros: toda falha de contrato levanta `FilePilotError(code: str, message: str, fields: dict[str, str] | None = None)`. Excecoes inesperadas (`OSError` fora dos casos tratados) sobem como `FilePilotError("ERRO_INTERNO", ...)` na camada de interface.

Codigos e mensagens exibidas:

| code | Quando ocorre | message (texto da interface) |
|---|---|---|
| `PASTA_INVALIDA` | Caminho nao existe ou nao e pasta | "A pasta escolhida não existe ou não é uma pasta." |
| `PASTA_ILEGIVEL` | `PermissionError` ou `OSError` ao listar | "Não foi possível ler a pasta escolhida." |
| `PASTA_VAZIA` | Nenhum arquivo elegivel no nivel da pasta | "A pasta escolhida não tem arquivos para organizar." |
| `PASTA_PROTEGIDA` | Raiz de unidade, pasta do sistema ou de programas, ou pasta de rede (6.1) `[DECISAO: aprovada no enriquecimento; sugestoes 2 e 4]` | "Esta pasta é protegida e não pode ser organizada. Escolha outra pasta." |
| `ERRO_INTERNO` | Excecao inesperada fora do tratamento por arquivo `[DECISAO: aprovada no enriquecimento; sugestao 3]` | "Ocorreu um erro inesperado. Tente de novo." |
| `REGRA_INVALIDA` | Campo da regra invalido (traz `fields`) | "Corrija os campos destacados." |
| `REGRA_NAO_ENCONTRADA` | `rule_id` inexistente | "A regra não existe mais." |
| `NADA_PARA_DESFAZER` | Desfazer sem ultima organizacao desfazivel | "Não há organização para desfazer." |
| `ORGANIZACAO_EM_ANDAMENTO` | Segunda organizacao ou desfazer durante uma organizacao | "Aguarde a organização terminar." |
| `DESTINO_FORA_DA_PASTA` | Destino resolvido fora da pasta escolhida | "O destino fica fora da pasta escolhida." |
| `BANCO_INDISPONIVEL` | `sqlite3.Error` ao abrir ou gravar | "Não foi possível acessar o histórico do FilePilot." |

Listagens paginadas: so a do historico (6.4), por pagina `page` e `page_size` com padrao 50 `[DECISAO: paginar evita carregar historico longo de uma vez; o PRD nao define tamanho]`. Regras nao sao paginadas (poucas e todas aparecem na lista).

Middleware, integracoes externas, tarefas em segundo plano: a unica tarefa em segundo plano e o `OrganizeWorker` (7.2). Nao ha integracao externa alem do sistema de arquivos.

### 6.1 scanner.scan_folder

`scan_folder(folder: Path) -> list[ScannedFile]`

- `ScannedFile`: `path: Path`, `name: str`, `extension: str` (minusculas, sem ponto, `""` se nao houver), `size_bytes: int`.
- Le so o nivel da pasta com `Path.iterdir()`; ordena por `name` sem diferenciar maiusculas.
- Inclui apenas arquivos regulares. Ignora pastas, links simbolicos e junctions `[DECISAO: mover um link poderia mover o alvo; ignorar e o comportamento conservador]`.
- Ignora arquivo oculto ou de sistema: `os.stat(path).st_file_attributes & (stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM)` diferente de zero. Onde o atributo nao existe (fora do Windows), o arquivo conta como visivel.
- Atalho `.lnk` segue a regra normal: extensao `lnk`, sem categoria padrao.
- `extension` de `arquivo.tar.gz` e `gz`; de `.gitignore` e `""`; de `arquivo.` e `""`.
- Pasta protegida: antes de listar, `scan_folder` resolve `folder` e levanta `PASTA_PROTEGIDA` se ela for a raiz de uma unidade (`folder.resolve() == Path(folder.resolve().anchor)`), igual a `%SystemRoot%`, `%ProgramFiles%` ou `%ProgramFiles(x86)%` (variaveis de ambiente, com `C:\Windows`, `C:\Program Files` e `C:\Program Files (x86)` como padrao se ausentes) ou estiver dentro de qualquer uma delas `[DECISAO: aprovada no enriquecimento; sugestao 2]`.
- Pasta de rede: levanta `PASTA_PROTEGIDA` se o caminho comeca com `\\` ou se a unidade e de rede (`ctypes.windll.kernel32.GetDriveTypeW(anchor) == 4`); so pastas em discos locais sao aceitas `[DECISAO: aprovada no enriquecimento; sugestao 4]`. Fora do Windows, a verificacao de unidade e ignorada.
- Erros: `PASTA_INVALIDA` se `folder` nao e pasta existente; `PASTA_PROTEGIDA` (acima); `PASTA_ILEGIVEL` se a listagem falha; `PASTA_VAZIA` se a lista final tem zero arquivos.
- Arquivo cujo `os.stat` falha durante a listagem e omitido da lista (nao interrompe).
- Efeitos: nenhum; so le.

### 6.2 planner.build_plan

`build_plan(folder: Path, files: list[ScannedFile], rules: list[Rule]) -> Plan`

- `Rule`: `id: int`, `name: str`, `destination_folder: str`, `position: int`, `extensions: frozenset[str]`.
- `Plan`: `folder: Path`, `operations: list[PlannedOperation]`, `skipped: list[ScannedFile]` (sem categoria), `is_empty: bool` (verdadeiro quando `operations` esta vazia).
- `PlannedOperation`: `seq: int`, `source_path: Path`, `destination_path: Path`, `category: str | None`, `rule_name: str | None` (mesmos nomes de `operations`, 5.3).
- Precedencia por arquivo: a primeira regra (menor `position`) cuja `extensions` contem a extensao do arquivo; se nenhuma, a categoria padrao da extensao; se nenhuma, o arquivo vai para `skipped` e nao gera operacao.
- Regra sobre categoria: quando regra e categoria casam, vale a regra; `rule_name` guarda a regra vencedora e `category` fica `None`. Em categoria padrao, `rule_name` e `None`.
- Destino: `folder / <subpasta> / <nome>`; a subpasta da regra e `destination_folder`, a da categoria e a coluna "Subpasta" de 5.5.
- Conflito (FR-006): se `destino` ja existe, ou ja foi usado por operacao anterior do mesmo plano, o nome vira `<base> (n)<ext>` com `n` crescente a partir de 1, ate um nome livre. Comparacao de nomes sem diferenciar maiusculas, como no Windows.
- `seq` comeca em 1 e segue a ordem de `files`.
- Guarda de seguranca: todo `destination_path.resolve()` precisa satisfazer `destination_path.resolve().is_relative_to(folder.resolve())`; senao levanta `DESTINO_FORA_DA_PASTA` e nenhum plano e devolvido.
- Nao cria pastas, nao move e nao grava no banco: e a mesma funcao usada pela simulacao.
- Erros: `DESTINO_FORA_DA_PASTA`. Nenhum outro erro.

### 6.3 organizer.simulate e organizer.organize

`simulate(plan: Plan) -> Plan`: devolve o proprio plano; e a funcao que a interface chama na simulacao para o nome ficar explicito. Nao altera disco nem banco.

`organize(plan: Plan, conn: sqlite3.Connection, progress_callback: Callable[[int, int, str], None] | None = None) -> OrganizationResult`

- `OrganizationResult`: `organization_id: int`, `moved_count: int`, `failed_count: int`, `failures: list[tuple[str, str]]` (nome do arquivo, motivo).
- `progress_callback(done, total, filename)` e chamado uma vez antes de cada arquivo (com `done` igual ao numero ja processado) e uma vez ao final com `done == total`.
- Se `plan.is_empty`, devolve resultado com contagens zero (`organization_id` igual a 0) sem gravar organizacao. A interface nunca chama `organize` com plano vazio (botao indisponivel).
- Abertura: insere `organizations` com status `em_andamento` e faz `commit`.
- Para cada `PlannedOperation`, em ordem de `seq`:
  0. Verificacoes de 6.7 (caminho acima de 259 caracteres e subpasta de destino que e link ou junction): se falharem, a operacao vira `falha` sem tentar mover.
  1. `destination_path.parent.mkdir(parents=True, exist_ok=True)`.
  2. `os.rename(source_path, destination_path)`.
  3. `FileExistsError` em (2): recalcula o proximo sufixo livre e repete (2); nunca sobrescreve.
  4. Sucesso: insere `operations` com status `movido` e `destination_path` final e faz `commit` na hora (NFR-002); incrementa `moved_count`.
  5. `PermissionError`, `FileNotFoundError` ou `OSError` em (1) ou (2): insere `operations` com status `falha`, `destination_path` NULL e `error_message` com o texto amigavel da tabela de 6.7 (nunca o texto bruto do sistema); incrementa `failed_count`; segue para o proximo arquivo (FR-007).
- Antes de (2), reconfirma `destination_path.resolve().is_relative_to(folder.resolve())`; falha vira `DESTINO_FORA_DA_PASTA` e a operacao e registrada como `falha`.
- Fechamento: atualiza a organizacao com `finished_at`, contagens e status `concluida`; `commit`.
- Falha de `sqlite3.Error` em qualquer gravacao levanta `BANCO_INDISPONIVEL`; o arquivo ja movido sem registro e restaurado por `os.rename` de volta antes de levantar, para o desfazer nao perder nada.
- Duas organizacoes ao mesmo tempo: `filepilot/services/organizer.py` define `OPERATION_LOCK = threading.Lock()`, compartilhado com `undo_last` (6.5). `organize` e `undo_last` o adquirem sem bloquear (`acquire(blocking=False)`) e o liberam em `finally`; se ja estiver tomado, levantam `ORGANIZACAO_EM_ANDAMENTO`. A trava e do servico, nao da interface.

### 6.4 history

`list_organizations(conn, page: int = 1, page_size: int = 50) -> OrganizationPage`

- `OrganizationPage`: `items: list[OrganizationRow]`, `page: int`, `page_size: int`, `total: int`.
- `OrganizationRow`: `id`, `started_at`, `folder_path`, `moved_count`, `failed_count`, `status` (nomes iguais as colunas de 5.3).
- Ordem: `started_at` decrescente, desempate por `id` decrescente. `page` menor que 1 vira 1; `page_size` fora de 1 a 200 vira 50.
- Historico vazio devolve `items=[]` e `total=0`.

`get_organization_detail(conn, organization_id: int) -> list[OperationRow]`

- `OperationRow`: `seq`, `source_path`, `destination_path`, `category`, `rule_name`, `status`, `error_message`.
- Ordem por `seq` crescente. `organization_id` inexistente devolve lista vazia.
- Erro: `BANCO_INDISPONIVEL`.

`last_undoable(conn) -> OrganizationRow | None`

- Pega a organizacao de maior `started_at` (desempate por `id`); devolve a linha so se `status` e `concluida` ou `interrompida` e `moved_count >= 1`; senao `None`.
- Nao ha retrocesso para organizacao anterior `[DECISAO: o PRD limita o desfazer a ultima organizacao, entao uma ultima sem arquivos movidos deixa o desfazer indisponivel]`.
- A interface usa esta funcao para habilitar o botao Desfazer.

### 6.5 undo.undo_last

`undo_last(conn: sqlite3.Connection) -> UndoResult`

- `UndoResult`: `organization_id: int`, `restored_count: int`, `not_restored: list[tuple[str, str]]` (caminho original, motivo), `removed_folders: list[str]`.
- Seleciona `last_undoable(conn)`; se `None`, levanta `NADA_PARA_DESFAZER`.
- Percorre as operacoes com status `movido` em ordem de `seq` decrescente. Para cada uma:
  1. Se `destination_path` nao existe: status `nao_restaurado`, `error_message` "arquivo não está mais no destino".
  2. Se `source_path` ja existe: status `nao_restaurado`, `error_message` "caminho original ocupado" `[DECISAO: nunca sobrescrever, nem ao desfazer]`.
  3. Senao `os.rename(destination_path, source_path)`: sucesso grava `restaurado`; `OSError` grava `nao_restaurado` com o texto do erro.
- Operacoes `falha` ficam como estao. Cada status gravado e `commit` na hora.
- Pastas: depois do laco, para cada pasta de destino distinta das operacoes `movido`, tenta `Path.rmdir()` e sobe pelo pai enquanto o pai ainda estiver dentro da pasta escolhida (sem remove-la) e `rmdir` suceder. `OSError` (pasta nao vazia) para a subida sem erro. So remove pastas vazias `[DECISAO: rmdir so apaga pasta vazia, entao nenhum arquivo pode ser perdido aqui]`.
- Fim: organizacao com `status = 'desfeita'`, `undone_at` preenchido, `commit`. Vale mesmo com itens `nao_restaurado`; depois disso `last_undoable` devolve `None` ate a proxima organizacao.
- A guarda e sempre aplicada, sem parametro para desliga-la: cada `source_path` precisa ficar dentro de `folder_path` da organizacao; fora disso a operacao vira `nao_restaurado` (NFR-001).
- Erros: `NADA_PARA_DESFAZER`, `ORGANIZACAO_EM_ANDAMENTO`, `BANCO_INDISPONIVEL`.

### 6.6 rules

Funcoes de `filepilot.services.rules`, todas com `conn` como primeiro argumento.

| Funcao | Entrada | Saida | Erros |
|---|---|---|---|
| `list_rules()` | - | `list[Rule]` por `position` crescente | `BANCO_INDISPONIVEL` |
| `create_rule(name, extensions, destination_folder)` | `str`, `list[str]`, `str` | `Rule` (entra na ultima posicao) | `REGRA_INVALIDA`, `BANCO_INDISPONIVEL` |
| `update_rule(rule_id, name, extensions, destination_folder)` | `int`, `str`, `list[str]`, `str` | `Rule` (mantem a posicao) | `REGRA_INVALIDA`, `REGRA_NAO_ENCONTRADA` |
| `delete_rule(rule_id)` | `int` | `None`; reordena as demais sem lacunas | `REGRA_NAO_ENCONTRADA` |
| `move_rule(rule_id, new_position)` | `int`, `int` | `list[Rule]` reordenada | `REGRA_NAO_ENCONTRADA`, `REGRA_INVALIDA` (`fields["position"]` = "Posição inválida." quando `new_position` fica fora de 1 ate o total de regras; a interface nao chega a esse caso, pois "Subir" e "Descer" ficam desabilitados nos extremos) |

Validacao (devolve `REGRA_INVALIDA` com `fields` por campo; mensagens exatas):

| Campo | Regra | `fields[...]` |
|---|---|---|
| `name` | Obrigatorio, apos `strip` de 1 a 60 caracteres | "Informe um nome de até 60 caracteres." |
| `extensions` | Ao menos 1; cada uma, apos `strip`, remocao de um `.` inicial e minusculas, casa `^[a-z0-9]{1,15}$`; duplicadas na mesma regra sao unidas | "Informe ao menos uma extensão (letras e números, até 15)." |
| `destination_folder` | Obrigatorio; relativo; segmentos separados por `/` ou `\`; nenhum segmento vazio, `.` ou `..`; sem raiz ou unidade; cada segmento sem `< > : " | ? *`, nao terminado em ponto ou espaco e nao reservado (`CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9`) | "Informe uma subpasta válida dentro da pasta escolhida." |

- Destino com varios segmentos (`Fotos/2026`) e permitido `[DECISAO: o PRD diz "subpasta" sem proibir niveis; a guarda de 6.2 mantem tudo dentro da pasta escolhida]`.
- Extensao ja coberta por outra regra e permitida; vale a de menor `position` (FR-011).
- Excluir regra nao altera `operations.rule_name` ja gravado.
- Cada gravacao e uma transacao unica: regra e extensoes entram juntas ou nao entram.
- Reordenacao (`delete_rule` e `move_rule`) respeita `UNIQUE (position)`: na mesma transacao, primeiro todas as posicoes afetadas viram o valor negativo (`position = -position`) e depois recebem a posicao final de 1 ate o total, sem lacunas.

### 6.7 Verificacoes de destino e textos de falha por arquivo

Adicionado no enriquecimento. Usado por `organize` (6.3) e, nos itens de texto, por `undo_last` (6.5).

Verificacoes antes de mover cada arquivo, nesta ordem:

1. Caminho longo: se `len(str(destination)) > 259`, a operacao vira `falha` com o texto "caminho de destino muito longo", sem tentar mover `[DECISAO: aprovada no enriquecimento; sugestao 1]`.
2. Subpasta de destino que e atalho: se a subpasta de destino ja existe e e link simbolico (`Path.is_symlink()`) ou junction (`os.path.isjunction()` ou atributo `FILE_ATTRIBUTE_REPARSE_POINT` em `st_file_attributes`), nenhum arquivo vai para ela; a operacao vira `falha` com o texto "a subpasta de destino é um atalho" `[DECISAO: aprovada no enriquecimento; sugestao 8]`. Vale para cada nivel da subpasta de uma regra com varios segmentos.
3. Guarda de pasta (6.2): `is_relative_to` continua valendo depois das verificacoes 1 e 2.

Textos gravados em `operations.error_message` (e exibidos no historico, 7.4), por tipo de erro `[DECISAO: aprovada no enriquecimento; sugestao 3]`:

| Condicao | Texto de `error_message` |
|---|---|
| `PermissionError` com `winerror == 32`, ou `OSError` com `winerror == 32` (arquivo em uso) | "arquivo em uso por outro programa" |
| Outro `PermissionError` | "sem permissão para mover o arquivo" |
| `FileNotFoundError` | "arquivo não encontrado" |
| Verificacao 1 | "caminho de destino muito longo" |
| Verificacao 2 | "a subpasta de destino é um atalho" |
| `OSError` ao criar a subpasta (`mkdir`), exceto os casos acima | "não foi possível criar a subpasta de destino" |
| Qualquer outro `OSError` | "erro ao mover o arquivo" |

- No desfazer (6.5), os motivos de `nao_restaurado` mantem os textos de 6.5; um `OSError` ao restaurar usa "erro ao mover o arquivo".
- Excecao fora do tratamento por arquivo (no `OrganizeWorker`, no desfazer ou em outra chamada da interface): vira `FilePilotError("ERRO_INTERNO", ...)` com a mensagem de 6 e a interface mostra `QMessageBox.critical`.
- Caso de teste obrigatorio: subpasta `Documentos` criada como junction ou link para fora da pasta escolhida deve resultar em `falha` para todos os arquivos desse destino e em zero arquivos movidos para fora da pasta.

## 7. Componentes / Modulos

Interface em PySide6 com widgets nativos do Qt e o estilo padrao do Windows `[DECISAO: nao ha sistema visual definido no PRD nem codigo existente; o estilo nativo evita tema proprio]`. Nao existe codigo anterior no repositorio, entao nenhum padrao "ja existente" e citado.

Mensagens de interface comuns:

| Situacao | Texto |
|---|---|
| Nenhuma pasta escolhida | "Escolha uma pasta para começar." |
| Erro de servico | o `message` do `FilePilotError` de 6, com o botao "OK" |
| Carregando listagem | "Lendo a pasta..." |

### 7.1 MainWindow

Arvore: `MainWindow` > `QTabWidget` > `OrganizeTab`, `HistoryTab`, `RulesTab`.

| Propriedade/Estado | Tipo | Inicial | Descricao |
|---|---|---|---|
| `db_path` (propriedade) | `Path` | calculado em 5.1 | Passado pelo `main()` |
| `conn` (estado) | `sqlite3.Connection` | aberta em `__init__` | Usada pelas tabs; fechada em `closeEvent` |
| `organizing` (estado) | `bool` | `False` | Verdadeiro durante `OrganizeWorker` ou desfazer |

- Titulo da janela: "FilePilot". Abas: "Organizar", "Histórico", "Regras".
- Evento `closeEvent`: com `organizing == True`, ignora o fechamento e exibe "Aguarde a organização terminar para fechar." `[DECISAO: fechar no meio deixaria a organizacao interrompida; bloquear e o comportamento conservador]`. Sem organizacao, fecha a conexao e aceita.
- Falha em `open_connection` ao iniciar: `QMessageBox.critical` com "Não foi possível acessar o histórico do FilePilot." e o aplicativo encerra com codigo 1.
- Ao trocar para a aba Historico ou Regras, a aba recarrega seus dados (sinal `currentChanged`).
- Estados de carregamento, vazio e erro: da janela em si, nao se aplica (so contem abas); cada aba trata os seus.
- Eventos emitidos: `organization_finished(int)` do `OrganizeTab` para o `HistoryTab` recarregar; nao ha outros.
- Ponto de entrada: `filepilot/__main__.py` cria `QApplication`, define `setApplicationName("FilePilot")` e mostra a `MainWindow`.
- Instancia unica `[DECISAO: aprovada no enriquecimento; sugestao 7]`: antes de abrir o banco, `main()` tenta `QLockFile(<pasta de dados>/filepilot.lock).tryLock(0)`. Se falhar (outra instancia aberta), mostra `QMessageBox.information` com "O FilePilot já está aberto." e encerra com codigo 0, sem criar a janela e sem abrir o banco. A trava e liberada em `closeEvent` e, se o processo cair, o `QLockFile` recupera a trava velha na proxima abertura (`setStaleLockTime`).

### 7.2 OrganizeTab

Arvore: `OrganizeTab` > `FolderBar` (`QLineEdit` somente leitura, `QPushButton` "Escolher pasta...", `QPushButton` "Atualizar"), `FileTableView`, `ActionBar` (`QPushButton` "Simular", "Organizar", "Desfazer última organização"), `QProgressBar`, `QLabel` de resumo.

| Estado | Tipo | Inicial | Descricao |
|---|---|---|---|
| `folder` | `Path | None` | `None` | Pasta escolhida |
| `files` | `list[ScannedFile]` | `[]` | Resultado de 6.1 |
| `plan` | `Plan | None` | `None` | Ultimo plano calculado |
| `mode` | `str` | `"vazio"` | `vazio`, `carregando`, `listado`, `simulado`, `organizando`, `erro` |

- Evento "Escolher pasta...": `QFileDialog.getExistingDirectory`. Cancelar mantem tudo como esta. Pasta confirmada: `mode = "carregando"`, rotulo "Lendo a pasta...", chama `scan_folder` e depois `build_plan` com `list_rules`.
- Botao "Atualizar" (ao lado de "Escolher pasta...", habilitado com pasta escolhida e fora de `organizando`) `[DECISAO: aprovada no enriquecimento; sugestao 5]`: repete o mesmo fluxo de leitura da pasta e recalculo do plano, volta a `mode = "listado"` e descarta a simulacao exibida.
- Sucesso: `mode = "listado"`; resumo "N arquivos na pasta" (N = `len(files)`); `FileTableView` mostra todos os arquivos.
- `PASTA_VAZIA`, `PASTA_INVALIDA`, `PASTA_ILEGIVEL`: `mode = "erro"`, resumo com a mensagem do erro, tabela vazia, "Simular" e "Organizar" desabilitados.
- "Simular": relê a pasta (`scan_folder`) e recalcula o plano com `list_rules` atuais antes de exibir, para a simulacao refletir regras criadas, editadas ou excluidas desde a escolha da pasta (US-012) e arquivos novos; depois exibe `plan` na tabela (colunas de 7.3), `mode = "simulado"`, resumo "Simulação: N operações. Nenhum arquivo foi alterado." Com `plan.is_empty`: resumo "Não há operações para executar." e "Organizar" desabilitado.
- "Organizar": habilitado em `listado` ou `simulado` com plano nao vazio. Primeiro relê a pasta (`scan_folder`) e recalcula o plano com `list_rules` atuais `[DECISAO: aprovada no enriquecimento; sugestao 5]`. Se o plano recalculado estiver vazio (`plan.is_empty`), nao executa nada, mostra "Não há operações para executar." e desabilita "Organizar". Se `mode == "simulado"` e o plano novo for diferente do exibido (compara `source_path`, `destination_path` e `rule_name` de cada operacao), nao executa nada: mostra o plano novo na tabela e o aviso "A pasta mudou desde a simulação. Confira a nova simulação e clique em Organizar de novo."; `mode` continua `simulado`. Se `mode == "listado"` (sem simulacao exibida) ou o plano for igual, dispara `OrganizeWorker(plan, db_path)` em `QThread`; `mode = "organizando"`; botoes, "Atualizar" e "Escolher pasta..." desabilitados; `MainWindow.organizing = True`.
- `OrganizeWorker` emite `progress(done: int, total: int, filename: str)` (liga o `progress_callback`), `finished(result)` e `failed(code, message)`.
- Barra: `setRange(0, total)`; `setValue(done)`; texto `"%v de %m arquivos"`. Em `finished`: valor igual ao total (100%) e resumo "Concluído: X movidos, Y falhas."
- Botao "Ver detalhes" `[DECISAO: aprovada no enriquecimento; sugestao 6]`: aparece ao lado do resumo so quando `failed_count` e maior que 0; ao clicar, abre a aba "Histórico" com a organizacao de `result.organization_id` selecionada (`HistoryTab.show_organization(organization_id)`); some ao escolher outra pasta, atualizar ou iniciar nova organizacao.
- Apos `finished`: reescaneia a pasta, `mode = "listado"`, emite `organization_finished`, reabilita botoes.
- `failed`: `QMessageBox.critical` com a mensagem; `mode = "erro"`.
- "Desfazer última organização": habilitado quando `last_undoable(conn)` nao e `None` e `organizing` e falso; reavaliado ao abrir a aba e depois de organizar ou desfazer. Executa `undo_last`; resumo "Desfeito: X arquivos restaurados." e, se `not_restored` nao estiver vazio, "Não restaurados: " seguido dos caminhos; reescaneia a pasta se for a atual.
- Sem pasta, "Simular", "Organizar" ficam desabilitados e o resumo mostra "Escolha uma pasta para começar.".

### 7.3 FileTableView

Subcomponente de `OrganizeTab`: `QTableView` com `QAbstractTableModel` `FileTableModel`.

| Coluna (cabecalho) | Fonte | Observacao |
|---|---|---|
| "Arquivo" | `ScannedFile.name` | Alinhado a esquerda |
| "Extensão" | `ScannedFile.extension` | Vazia se nao houver |
| "Categoria" | nome da subpasta da categoria padrao ("Documentos", "Imagens", "Videos" ou "Compactados"), "Regra personalizada" quando uma regra cobre o arquivo, ou "sem categoria" `[DECISAO: aprovada no ponto de checagem; opcao A do VAG-005, o nome da regra aparece so na coluna "Regra"]` | Em `listado` mostra o valor previsto |
| "Destino" | `PlannedOperation.destination_path` relativo a pasta escolhida | Vazio em `listado` e para "sem categoria" |
| "Regra" | `PlannedOperation.rule_name` | Vazio se for categoria padrao |

- Propriedade `model`: `FileTableModel`; metodo `set_rows(files, plan | None)`.
- Estados: carregamento (a `OrganizeTab` mostra "Lendo a pasta..." no lugar da tabela), vazio (mensagem "Nenhum arquivo para mostrar." centralizada) e erro (a mensagem da `OrganizeTab`).
- Marcador de status: linha "sem categoria" em cinza (`QPalette.Disabled`); linha com regra em negrito na coluna "Regra".
- Ordenacao: ordem de `files` (nome sem diferenciar maiusculas); sem ordenacao por clique `[DECISAO: nao pedida; manter a ordem do plano deixa a simulacao igual ao que sera executado]`.
- Tela estreita: colunas "Arquivo" e "Destino" com `setStretchLastSection(False)` e rolagem horizontal; as demais com largura ao conteudo.
- Selecao: nenhuma acao de contexto; so leitura.
- Eventos: nenhum emitido.

### 7.4 HistoryTab

Arvore: `HistoryTab` > `QTableView` `OrganizationTableView` (esquerda), `QTableView` `OperationTableView` (direita), `QLabel` de estado e botoes "Anterior" e "Próxima".

| Estado | Tipo | Inicial | Descricao |
|---|---|---|---|
| `page` | `int` | 1 | Pagina atual (50 por pagina) |
| `selected_id` | `int | None` | `None` | Organizacao selecionada |

- Colunas de organizacoes: "Data e hora" (horario local, `dd/MM/yyyy HH:mm`), "Pasta", "Movidos", "Falhas", "Situação" (`concluida` mostra "Concluída", `interrompida` "Interrompida", `desfeita` "Desfeita", `em_andamento` "Em andamento").
- Colunas de operacoes: "Arquivo" (nome de `source_path`), "Origem", "Destino final", "Situação" (`movido` "Movido", `falha` "Falha", `restaurado` "Restaurado", `nao_restaurado` "Não restaurado"), "Detalhe" (`error_message`).
- Ao selecionar uma linha, carrega `get_organization_detail`; o painel direito mostra "Selecione uma organização." enquanto nao houver selecao.
- Detalhes `[DECISAO: aprovada no enriquecimento; sugestao 6]`: enquanto `get_organization_detail` carrega, o painel direito mostra "Carregando detalhes..."; organizacao sem nenhuma operacao mostra "Nenhum arquivo nesta organização."; erro de leitura mostra a mensagem de `BANCO_INDISPONIVEL`.
- Metodo `show_organization(organization_id: int)`: carrega a pagina que contem a organizacao, seleciona a linha e mostra os detalhes; chamado pelo botao "Ver detalhes" da `OrganizeTab` (7.2) depois de trocar para esta aba.
- A coluna "Detalhe" mostra o `error_message` ja amigavel de 6.7.
- Carregando: rotulo "Carregando histórico...". Vazio (`total == 0`): "Nenhuma organização registrada ainda." Erro: a mensagem de `BANCO_INDISPONIVEL`, com botao "Tentar de novo".
- Botoes: "Anterior" desabilitado na pagina 1; "Próxima" desabilitado quando `page * 50 >= total`.
- A simulacao nunca aparece no historico (so organizacoes reais e seus desfazeres, como `status = 'desfeita'`).
- Evento recebido: `organization_finished` recarrega a pagina 1.

### 7.5 RulesTab e RuleEditorDialog

`RulesTab`: `QTableView` `RuleTableView`, botoes "Nova regra", "Editar", "Excluir", "Subir", "Descer".

- Colunas: "Prioridade" (posicao), "Nome", "Extensões" (separadas por virgula), "Subpasta".
- Estados: carregando ("Carregando regras..."), vazio ("Nenhuma regra personalizada. Use \"Nova regra\" para criar a primeira."), erro (mensagem do servico).
- "Editar", "Excluir", "Subir" e "Descer" so ficam habilitados com uma linha selecionada; "Subir" na primeira linha e "Descer" na ultima ficam desabilitados.
- "Excluir" abre `QMessageBox.question`: "Excluir a regra \"<nome>\"? O histórico não será alterado." com botoes "Excluir" e "Cancelar". "Cancelar" nao altera nada; "Excluir" chama `delete_rule`.

`RuleEditorDialog(QDialog)`:

| Campo | Widget | Obrigatorio | Texto de exemplo |
|---|---|---|---|
| Nome | `QLineEdit` | Sim | "Planilhas do trabalho" |
| Extensões | `QLineEdit` (separadas por virgula) | Sim | "xlsx, csv" |
| Subpasta de destino | `QLineEdit` | Sim | "Trabalho/Planilhas" |

- Botoes: "Salvar" (durante a gravacao o texto vira "Salvando..." e o botao fica desabilitado) e "Cancelar".
- Validacao: ao clicar "Salvar" chama `create_rule` ou `update_rule`; `REGRA_INVALIDA` mostra a mensagem de `fields` em vermelho abaixo de cada campo com erro, sem fechar o dialogo.
- Sucesso: fecha o dialogo (`accept`) e a `RulesTab` recarrega e seleciona a regra.
- Erro geral (`BANCO_INDISPONIVEL`): `QMessageBox.critical` com a mensagem; o dialogo continua aberto.
- Evento: `saved(rule_id: int)` emitido ao salvar.

## 8. Fluxos / Casos de uso

### 8.1 Simular e organizar (Ana)

1. Ana abre o aplicativo: `mode = "vazio"`, resumo "Escolha uma pasta para começar.".
2. Ela clica em "Escolher pasta..." e confirma a pasta Downloads no explorador do Windows.
3. O aplicativo mostra "Lendo a pasta..." (`mode = "carregando"`), le o nivel da pasta e mostra a lista com a categoria de cada arquivo e o resumo "N arquivos na pasta".
4. Ela clica em "Simular": a tabela mostra o destino de cada arquivo; arquivos sem categoria aparecem em cinza sem destino. Nada muda no disco.
5. Ela clica em "Organizar": o aplicativo relê a pasta e confere o plano com a simulacao exibida; sendo igual, a barra de progresso avanca "k de N arquivos" e os botoes ficam desabilitados.
6. Terminado, o resumo mostra "Concluído: X movidos, Y falhas." e a lista e recarregada. O botao "Desfazer última organização" fica habilitado.
- Alternativa: sem simular, Ana clica direto em "Organizar": o aplicativo relê a pasta, recalcula o plano e o executa.
- Alternativa: a pasta mudou depois da simulacao (por exemplo, um download terminou): ao clicar "Organizar" o aplicativo nao executa, mostra a nova simulacao e o aviso "A pasta mudou desde a simulação. Confira a nova simulação e clique em Organizar de novo."
- Alternativa: Ana clica em "Atualizar" para reler a pasta; a simulacao exibida e descartada.
- Alternativa: pasta de sistema, raiz de unidade ou de rede: erro `PASTA_PROTEGIDA` com a mensagem de 6 e botoes de acao desabilitados.
- Alternativa: organizacao termina com falhas: o resumo traz "Ver detalhes", que abre o Historico naquela organizacao.
- Alternativa: segunda abertura do aplicativo: mostra "O FilePilot já está aberto." e encerra.
- Alternativa: pasta sem arquivos ou ilegivel: mensagem de 6 e botoes de acao desabilitados.
- Alternativa: sem operacoes no plano: "Não há operações para executar." e "Organizar" desabilitado.

### 8.2 Desfazer (Ana)

1. Ana abre a aba Organizar; "Desfazer última organização" esta habilitado.
2. Ela clica nele: o aplicativo chama `undo_last`.
3. Os arquivos voltam ao caminho e nome originais (inclusive os que receberam sufixo); subpastas de categoria vazias sao removidas.
4. O resumo mostra "Desfeito: X arquivos restaurados.". O botao fica desabilitado ate a proxima organizacao.
- Alternativa: arquivo apagado, movido ou renomeado depois: os demais voltam e o resumo lista "Não restaurados: <caminhos>".
- Alternativa: caminho original ocupado por outro arquivo: o arquivo fica no destino e entra em "Não restaurados"; nada e sobrescrito.
- Alternativa: ultima organizacao sem arquivos movidos, ou ja desfeita: botao desabilitado (`NADA_PARA_DESFAZER` nao chega a ser chamado).

### 8.3 Criar e usar regra (Carlos)

1. Carlos abre a aba "Regras" e clica "Nova regra".
2. Preenche nome "Planilhas do trabalho", extensoes "xlsx, csv" e subpasta "Trabalho/Planilhas" e clica "Salvar".
3. A regra entra na ultima posicao. Ele pode usar "Subir" para dar mais prioridade a ela.
4. Na aba Organizar, escolhe uma pasta e clica "Simular": os arquivos `xlsx` e `csv` mostram a regra "Planilhas do trabalho" na coluna "Regra" e o destino `Trabalho/Planilhas`.
- Alternativa: campo invalido: mensagem em vermelho no campo, dialogo aberto.
- Alternativa: duas regras cobrem a mesma extensao: a de menor posicao aparece na coluna "Regra".
- Alternativa: Carlos edita ou exclui uma regra (com confirmacao); a mudanca vale da proxima simulacao em diante e o historico nao muda.

### 8.4 Consultar historico (Ana)

1. Ana abre a aba "Historico": ve as organizacoes da mais recente para a mais antiga.
2. Seleciona uma: o painel direito lista cada arquivo com origem, destino final e situacao.
3. Falhas aparecem com "Falha" e o motivo na coluna "Detalhe".
- Alternativa: historico vazio: "Nenhuma organização registrada ainda.".
- Alternativa: mais de 50 organizacoes: botoes "Anterior" e "Próxima".

## 9. Tratamento de erros

Politica: erro de servico levanta `FilePilotError` com `code` de 6; a interface mostra o `message` e nunca encerra o aplicativo, exceto a falha de abertura do banco (7.1). Falha por arquivo nunca interrompe a organizacao (FR-007).

| Caso | Severidade | Acao |
|---|---|---|
| Arquivo em uso, sem permissao ou inacessivel ao mover | Media | Registrar `falha` com o motivo no historico, seguir com os demais |
| Nome ja existe no destino | Baixa | Sufixo ` (n)`; nunca sobrescrever |
| Destino aparece entre o plano e a execucao | Baixa | `FileExistsError` no `os.rename`: recalcular sufixo e repetir |
| Pasta escolhida ilegivel, inexistente ou vazia | Media | Mensagem de 6; desabilitar Simular e Organizar |
| Arquivo apagado entre o plano e a execucao | Baixa | `FileNotFoundError` vira `falha` com o motivo e a execucao segue |
| Arquivo ausente ou origem ocupada no desfazer | Media | `nao_restaurado` com motivo; restaurar os demais |
| Destino fora da pasta escolhida | Alta | `DESTINO_FORA_DA_PASTA`; nada e movido |
| Falha de gravacao no banco | Alta | `BANCO_INDISPONIVEL`; desfazer a ultima movimentacao ainda nao registrada |
| Aplicativo encerrado no meio da organizacao | Media | Na proxima abertura, linha vira `interrompida`; operacoes gravadas podem ser desfeitas |
| Fechar a janela durante a organizacao | Baixa | Bloquear com aviso (7.1) |
| Regra invalida | Baixa | `REGRA_INVALIDA` com mensagem por campo |
| Caminho de destino acima de 259 caracteres | Media | `falha` com "caminho de destino muito longo" (6.7); segue com os demais |
| Subpasta de destino e link simbolico ou junction | Alta | `falha` com "a subpasta de destino é um atalho" (6.7); nada e movido para ela |
| Pasta escolhida e raiz de unidade, pasta do sistema, de programas ou de rede | Alta | `PASTA_PROTEGIDA`; Simular e Organizar desabilitados |
| Pasta mudou entre a simulacao e o clique em Organizar | Media | Nao executar; mostrar a nova simulacao e o aviso de 7.2 |
| Segunda instancia do aplicativo | Media | Mensagem "O FilePilot já está aberto." e encerrar sem tocar no banco (7.1) |
| Excecao inesperada fora do tratamento por arquivo | Media | `ERRO_INTERNO` com a mensagem de 6; a janela continua aberta |

## 10. Observabilidade

Nao se aplica: o PRD nao pede log, metrica nem rastreamento. As falhas por arquivo ficam no historico (FR-007) e sao a unica trilha de diagnostico da v1.

## 11. Seguranca / Permissoes

O aplicativo tem um unico perfil de uso: a pessoa logada no Windows. Nao ha login, tokens, papeis nem sessao.

| Papel | Recurso | Acao | Permitido |
|---|---|---|---|
| Pessoa logada no Windows (Ana ou Carlos) | Pasta escolhida | Ler, mover arquivos do nivel dela | Sim, conforme as permissoes do Windows |
| Pessoa logada no Windows | Banco `filepilot.db` | Ler e gravar | Sim, no perfil dela |
| Qualquer | Arquivo fora da pasta escolhida | Mover, apagar | Nao |
| Qualquer | Qualquer arquivo | Sobrescrever ou apagar | Nao |

Lista de verificacao:

- NFR-001, zero sobrescritas: toda movimentacao usa `os.rename`; `os.replace`, `shutil.move`, `os.remove`, `Path.unlink` e `shutil.rmtree` nao aparecem em `filepilot/services`. Teste de repositorio busca esses nomes no codigo.
- NFR-001, zero operacoes fora da pasta: guarda `is_relative_to` em 6.2, 6.3 e 6.5; destino com `..`, absoluto ou unidade e recusado na regra (6.6) e na guarda.
- Subpasta de destino que e link simbolico ou junction nunca recebe arquivo: teste cria uma junction ou link para fora da pasta escolhida e verifica `falha` em todos os arquivos desse destino e zero arquivos fora da pasta (6.7).
- Pastas protegidas e de rede sao recusadas por `scan_folder` antes de qualquer listagem (6.1): teste cobre raiz de unidade, `%SystemRoot%`, `%ProgramFiles%` e caminho `\\servidor\pasta`.
- Instancia unica por `QLockFile` (7.1): impede duas janelas escrevendo no mesmo banco.
- A simulacao altera zero arquivos: teste compara a arvore da pasta antes e depois de `simulate`.
- Validacao de entrada de regra e obrigatoria em toda escrita (6.6).
- Sem rede: nenhuma importacao de `socket`, `http`, `urllib` ou `requests` em `filepilot` (teste de repositorio).
- Consulta SQL sempre parametrizada (`?`); nunca concatenar nome de arquivo ou de regra em SQL.
- Variaveis de ambiente necessarias: nenhuma. Nenhum segredo existe; nada de credencial em artefato (regra 1 de `.abt/RULES.md`).
- O aplicativo nao pede privilegio de administrador: o aplicativo roda por usuario e grava so em `AppData` do perfil.
- Aviso do SmartScreen (executavel sem assinatura, risco D-003): aceito, assinatura de codigo fora da v1.

## 12. Performance / Limites

Sem limite de desempenho pedido.

O que a SPEC fixa mesmo sem meta numerica: a organizacao roda em thread de trabalho para a janela continuar respondendo (6.3, 7.2); os arquivos sao tratados em sequencia, um por vez; e o historico e paginado a 50 organizacoes por vez (6.4).

## 13. Compatibilidade / Migracao

Nao se aplica a dados ou clientes existentes: o projeto e novo e nao ha codigo anterior. O banco nasce com a migracao `0001_initial` (5.1). Migracoes futuras so acrescentam colunas ou tabelas e sao aplicadas na abertura da conexao, em ordem de `version`.

Sistema operacional alvo: Windows 10 e 11 em 64 bits. A suite de testes tambem roda em Linux (para desenvolvimento), com `pytest.mark.skipif` nos testes que dependem de atributos de arquivo do Windows.

## 14. Plano de entrega

So a ordem de dependencia; o fatiamento em itens e da fase seguinte.

1. Dados e base: `domain` (categorias, modelos, erros) e `db` (conexao, migracao `0001_initial`).
2. Servicos de leitura: `scanner` e `planner` (dependem de `domain`; `planner` depende de `rules` para ler regras).
3. Servico de regras: `rules` (depende de `db`).
4. Servicos de escrita: `organizer`, `history` e `undo` (dependem de `db`, `planner` e `domain`).
5. Interface: `MainWindow`, `OrganizeTab` e `FileTableView` (dependem de 2 a 4), depois `HistoryTab` e `RulesTab` com `RuleEditorDialog` (dependem de `history` e `rules`).
6. Empacotamento e CI: `pyproject.toml`, script PyInstaller e fluxo no runner `windows-latest` (dependem de tudo funcionar).

## 15. Anexos

### 15.1 Exemplo de plano

Pasta `C:\Users\Ana\Downloads` com `fatura.pdf`, `foto.JPG`, `setup.exe` e `fatura.pdf` ja existente em `Documentos`:

| seq | source_path | destination_path | category | rule_name |
|---|---|---|---|---|
| 1 | `...\fatura.pdf` | `...\Documentos\fatura (1).pdf` | `documentos` | `None` |
| 2 | `...\foto.JPG` | `...\Imagens\foto.JPG` | `imagens` | `None` |

`setup.exe` vai para `Plan.skipped` (sem categoria) e permanece onde esta.

### 15.2 Decisoes de design

| Contexto | Decisao | Consequencia | Alternativas rejeitadas |
|---|---|---|---|
| Nunca sobrescrever (NFR-001) | `os.rename` com tentativa de novo sufixo em `FileExistsError` | Sem corrida entre planejamento e execucao | `os.replace` e `shutil.move`, que sobrescrevem |
| Simulacao igual a organizacao | `build_plan` unico, `simulate` so o devolve | M2 vale por construcao | Calcular a simulacao em outra funcao |
| Historico por arquivo, em ordem | `seq` e `commit` por operacao | M3 e NFR-002 cumpridos; desfazer em ordem inversa | Gravar o historico so ao final |
| Copia do nome da regra | `operations.rule_name` e texto, nao chave | Excluir regra nao muda o historico | Chave estrangeira para `rules` |
| Desfazer so da ultima | `last_undoable` sem retrocesso | Regra simples e previsivel | Pilha de desfazer |
| Interface sem confirmacao ao organizar e ao desfazer | Botoes agem direto `[DECISAO: ha simulacao antes e desfazer depois, o PRD nao pede confirmacao e so exclusao de regra pede]` | Menos cliques para Ana | Dialogo de confirmacao |

## 16. Traceability Matrix

### 16.1 FR para elementos da SPEC

| FR | Elementos da SPEC | Status | Origem |
|---|---|---|---|
| FR-001 | 6.1 `scan_folder`; 7.2 `FolderBar`; 8.1 | coberto | prd.md |
| FR-002 | 5.5 categorias; 6.1 `scan_folder`; 6.2 `build_plan`; 7.3 `FileTableView` | coberto | prd.md |
| FR-003 | 6.2 `build_plan`; 6.3 `simulate`; 7.2 botao "Simular" | coberto | prd.md |
| FR-004 | 5.3 `operations`; 6.3 `organize` | coberto | prd.md |
| FR-005 | 6.3 `progress_callback`; 7.2 `QProgressBar` e `OrganizeWorker` | coberto | prd.md |
| FR-006 | 6.2 sufixo de conflito; 6.3 passo 3 | coberto | prd.md |
| FR-007 | 5.3 status `falha`; 6.3 passo 5 | coberto | prd.md |
| FR-008 | 5.3; 6.4 `history`; 7.4 `HistoryTab` | coberto | prd.md |
| FR-009 | 6.4 `last_undoable`; 6.5 `undo_last`; 7.2 botao "Desfazer" | coberto | prd.md |
| FR-010 | 5.4; 6.6 `rules`; 7.5 `RulesTab` e `RuleEditorDialog` | coberto | prd.md |
| FR-011 | 6.2 precedencia; 6.6 posicao; 7.3 coluna "Regra" | coberto | prd.md |
| NFR-001 | 6.2 guarda; 6.3 `os.rename`; 11 lista de verificacao | coberto | prd.md |
| NFR-002 | 6.3 `commit` por operacao; 5.3 `seq` | coberto | prd.md |
| - | 5 datas UTC e nomes snake_case | - | `[DECISAO: texto UTC e simples de ordenar; snake_case remove mapeamento]` |
| - | 5.2 tabela `schema_migrations` | - | `[DECISAO: controle de versao do esquema para migracoes futuras so acrescentarem, sem requisito do PRD que o exija]` |
| - | 5.1 caminho do banco em `AppData` | - | `[DECISAO: pasta de dados do aplicativo no perfil do usuario]` |
| - | 5.3 status `interrompida` | - | `[DECISAO: operacoes ja gravadas continuam validas]` |
| - | 5.4 limites de nome e de extensao | - | `[DECISAO: limites para a validacao ter regra objetiva]` |
| - | 6 historico paginado a 50 | - | `[DECISAO: paginar evita carregar historico longo]` |
| - | 6.1 ignorar links simbolicos e junctions | - | `[DECISAO: ignorar e o comportamento conservador]` |
| - | 6.4 sem retrocesso no desfazer | - | `[DECISAO: ultima sem arquivos movidos deixa o desfazer indisponivel]` |
| - | 6.5 caminho original ocupado | - | `[DECISAO: nunca sobrescrever, nem ao desfazer]` |
| - | 6.5 so remover pastas vazias | - | `[DECISAO: rmdir so apaga pasta vazia]` |
| - | 6.6 destino com varios segmentos | - | `[DECISAO: o PRD nao proibe niveis; a guarda mantem dentro da pasta]` |
| - | 7 estilo nativo do Qt | - | `[DECISAO: sem sistema visual no PRD]` |
| - | 7.1 bloquear fechamento durante a organizacao | - | `[DECISAO: bloquear e o comportamento conservador]` |
| - | 7.3 sem ordenacao por clique | - | `[DECISAO: manter a ordem do plano deixa a simulacao igual a execucao]` |
| - | 7.3 coluna "Categoria" com nome da subpasta, "Regra personalizada" ou "sem categoria" | - | `[DECISAO: aprovada no ponto de checagem; opcao A do VAG-005, o nome da regra aparece so na coluna "Regra"]` |
| - | 6.7 verificacao 1: caminho de destino acima de 259 caracteres vira falha; 9 | - | `[DECISAO: aprovada no enriquecimento; sugestao 1]` |
| - | 6.1 `PASTA_PROTEGIDA` para raiz de unidade, `%SystemRoot%`, `%ProgramFiles%` e `%ProgramFiles(x86)%`; 6; 9 | - | `[DECISAO: aprovada no enriquecimento; sugestao 2]` |
| - | 6.7 textos amigaveis de `error_message` e `ERRO_INTERNO`; 6; 9 | - | `[DECISAO: aprovada no enriquecimento; sugestao 3]` |
| - | 6.1 `PASTA_PROTEGIDA` para pasta de rede | - | `[DECISAO: aprovada no enriquecimento; sugestao 4]` |
| - | 7.2 botao "Atualizar" e conferencia do plano antes de organizar; 8.1; 9 | - | `[DECISAO: aprovada no enriquecimento; sugestao 5]` |
| - | 7.2 botao "Ver detalhes"; 7.4 estados "Carregando detalhes..." e "Nenhum arquivo nesta organização." e `show_organization` | - | `[DECISAO: aprovada no enriquecimento; sugestao 6]` |
| - | 7.1 instancia unica com `QLockFile`; 9 | - | `[DECISAO: aprovada no enriquecimento; sugestao 7]` |
| - | 6.7 verificacao 2: subpasta de destino que e link ou junction vira falha; 11 | - | `[DECISAO: aprovada no enriquecimento; sugestao 8]` |

### 16.2 US para fluxo

| US | Endpoints | Componentes | Status | Origem |
|---|---|---|---|---|
| US-001 | 6.1 `scan_folder` | 7.2 `FolderBar`, `QFileDialog` | coberto | prd.md |
| US-002 | 6.1, 6.2 | 7.3 `FileTableView` | coberto | prd.md |
| US-003 | 6.2, 6.3 `simulate` | 7.2 "Simular", 7.3 | coberto | prd.md |
| US-004 | 6.2 `build_plan`, 6.6 `rules` | 7.3 coluna "Regra" | coberto | prd.md |
| US-005 | 6.3 `organize` | 7.2 "Organizar" | coberto | prd.md |
| US-006 | 6.3 `progress_callback` | 7.2 `QProgressBar` | coberto | prd.md |
| US-007 | 6.2 sufixo, 6.3 passo 3 | 7.3 coluna "Destino" | coberto | prd.md |
| US-008 | 6.3 passo 5 | 7.2 resumo "falhas", 7.4 coluna "Detalhe" | coberto | prd.md |
| US-009 | 6.4 `list_organizations`, `get_organization_detail` | 7.4 `HistoryTab` | coberto | prd.md |
| US-010 | 6.4 `last_undoable`, 6.5 `undo_last` | 7.2 "Desfazer" | coberto | prd.md |
| US-011 | 6.6 `create_rule` | 7.5 `RuleEditorDialog` | coberto | prd.md |
| US-012 | 6.6 `update_rule`, `delete_rule`, `move_rule` | 7.5 `RulesTab`, confirmacao de exclusao | coberto | prd.md |

### 16.3 Nomes entre camadas

| Coluna | Campo da API | Propriedade da interface | Consistente |
|---|---|---|---|
| `organizations.started_at` | `OrganizationRow.started_at` | coluna "Data e hora" | Sim |
| `organizations.folder_path` | `OrganizationRow.folder_path` | coluna "Pasta" | Sim |
| `organizations.moved_count` | `OrganizationRow.moved_count` | coluna "Movidos" | Sim |
| `organizations.failed_count` | `OrganizationRow.failed_count` | coluna "Falhas" | Sim |
| `organizations.status` | `OrganizationRow.status` | coluna "Situação" | Sim |
| `operations.source_path` | `OperationRow.source_path` | coluna "Origem" | Sim |
| `operations.destination_path` | `OperationRow.destination_path` | coluna "Destino final" | Sim |
| `operations.rule_name` | `OperationRow.rule_name` | coluna "Regra" | Sim |
| `operations.error_message` | `OperationRow.error_message` | coluna "Detalhe" | Sim |
| `rules.destination_folder` | `Rule.destination_folder` | campo "Subpasta de destino" | Sim |
| `rules.position` | `Rule.position` | coluna "Prioridade" | Sim |
| `rule_extensions.extension` | `Rule.extensions` | campo "Extensões" | Sim |

## 17. Ferramentas de desenvolvimento e plataforma alvo [DELTA 2026-10-11, mypy e Windows 10 e 11 em 64 bits]

### 17.1 Objetivo e fora de escopo

Esta secao registra duas decisoes da especificacao, vindas de `.abt/product-spec/20261011-231916/discovery-notes.md`:

1. A checagem de tipos com mypy faz parte das ferramentas de desenvolvimento, junto com pytest.
2. A plataforma alvo do FilePilot e Windows 10 e 11 em 64 bits.

Fora de escopo desta secao: mudar codigo do produto (ainda nao existe codigo no repositorio); anotar tipos no codigo existente; macOS e Linux como plataforma alvo (continuam fora de escopo, como em 1.2); reabrir PRD ou stack. Nenhum dado, servico ou tela muda: o modelo de dados (5), os contratos (6) e os componentes (7) ficam como estao.

### 17.2 Ferramentas de desenvolvimento: mypy

Acrescenta uma linha a tabela de 4. Nao altera as linhas existentes:

| Camada | Tecnologia | Versao | Razao |
|---|---|---|---|
| Checagem de tipos | mypy | 2.4.0 | Verifica as anotacoes de tipo do pacote `filepilot` junto com os testes do pytest `[DECISAO: a versao 2.4.0 e a mais recente publicada no PyPI em 2026-10-11; a pessoa nao indicou versao]` |

Complementa o ultimo paragrafo de 4 sobre o manifesto: `pyproject.toml` declara `mypy==2.4.0` entre as dependencias de desenvolvimento, ao lado de `pytest==9.1.1`, `pytest-qt==4.5.0` e `pyinstaller==6.22.3`. Dependencias novas desta secao: so `mypy==2.4.0`.

Comando de checagem: `python -m mypy --platform win32 filepilot`, executado na raiz do repositorio, com saida que comeca por `Success: no issues found` (a linha completa traz a contagem de arquivos analisados) e codigo de saida 0 `[DECISAO: o pacote filepilot e o unico codigo do produto (3.1); a pessoa nao pediu configuracao estrita nem arquivo de configuracao proprio, entao vale a configuracao padrao do mypy]`. A opcao `--platform win32` faz o mypy analisar o codigo para a plataforma alvo de 17.3, mesmo quando a checagem roda em Linux; sem ela, `ctypes.windll` (6.1) e `st_file_attributes` (6.1 e 6.7) seriam apontados como erro fora do Windows `[DECISAO: aprovada no enriquecimento; sugestao 1]`.

Escopo negativo: esta secao NAO cria o arquivo de configuracao do mypy; NAO acrescenta mypy ao fluxo do GitHub Actions; NAO exige anotacao de tipos alem da que as demais secoes ja usam. A checagem e um comando manual de desenvolvimento.

Rodar mypy em Linux e permitido, como o pytest (13), sempre com `--platform win32`.

### 17.3 Plataforma alvo

Decisao da especificacao: a plataforma alvo do FilePilot e Windows 10 e 11 em 64 bits. Isto formaliza a frase de 13 ("Sistema operacional alvo: Windows 10 e 11 em 64 bits") como decisao e a mantem como esta; nada em 13 e editado.

O que a decisao fixa:

- O executavel gerado com PyInstaller (4) e entregue para Windows 10 e 11 em 64 bits e nao e entregue para outra plataforma.
- O Python do ambiente de build e dos testes no Windows e a distribuicao de 64 bits da versao 3.12 `[DECISAO: o runner windows-latest do GitHub Actions (4) e de 64 bits; a decisao de plataforma vale tambem para o ambiente de build]`.
- Versoes de 32 bits do Windows e outras versoes do Windows nao sao alvo e nao ganham teste.
- Linux continua so como ambiente de desenvolvimento e de testes (13), nunca como plataforma alvo.

Escopo negativo: esta secao NAO cria teste que verifique a arquitetura do sistema em execucao; NAO muda `requires-python` (4).

### 17.4 Pendencias para decisao

Nenhuma pendencia aberta nesta secao.

### 17.5 Traceability Matrix

| Item do escopo | Elementos da SPEC | Status | Origem |
|---|---|---|---|
| mypy faz parte das ferramentas de desenvolvimento, junto com pytest | 17.2; complementa 4 | coberto | discovery-notes.md |
| Plataforma alvo: Windows 10 e 11 em 64 bits, como decisao | 17.3; formaliza 13 | coberto | discovery-notes.md |
| - | 17.2 versao `mypy==2.4.0` | - | `[DECISAO: a versao 2.4.0 e a mais recente publicada no PyPI em 2026-10-11; a pessoa nao indicou versao]` |
| - | 17.2 comando `python -m mypy --platform win32 filepilot` com configuracao padrao | - | `[DECISAO: o pacote filepilot e o unico codigo do produto (3.1); a pessoa nao pediu configuracao estrita nem arquivo de configuracao proprio, entao vale a configuracao padrao do mypy]` e `[DECISAO: aprovada no enriquecimento; sugestao 1]` |
| - | 17.3 Python de 64 bits no ambiente de build e de testes no Windows | - | `[DECISAO: o runner windows-latest do GitHub Actions (4) e de 64 bits; a decisao de plataforma vale tambem para o ambiente de build]` |

## §18 Fundacao: projeto, dominio, banco e CI Windows

Item: filepilot-v1-1 (filepilot-2)

## 19. Comando unico de checagem de tipos com mypy [DELTA 2026-10-11, mypy --platform win32 em todos os itens e no GitHub Actions]

### 19.1 Objetivo e fora de escopo

Esta secao registra uma decisao da especificacao, vinda de `.abt/product-spec/20261011-235554/discovery-notes.md`: a checagem de tipos roda igual no Linux e no Windows, com UM unico comando de mypy, sempre com `--platform win32`, em todos os itens e no fluxo do GitHub Actions.

Hoje existem duas formas do comando: `python -m mypy --platform win32 filepilot` (17.2) e `mypy . --no-error-summary` (`.github/workflows/tests.yml:22` e o campo `Verificacao:` dos itens de `.abt/items/filepilot-v1/`). Esta secao fixa a primeira como a unica.

Fora de escopo desta secao: mudar codigo do produto; anotar tipos no codigo existente; criar arquivo de configuracao do mypy; mudar a versao `mypy==2.4.0` (`pyproject.toml:19`); mudar a plataforma alvo (17.3); reabrir PRD ou stack. Nenhum dado, servico ou tela muda: o modelo de dados (5), os contratos (6) e os componentes (7) ficam como estao.

### 19.2 Comando unico

O comando unico de checagem de tipos do FilePilot e, literalmente:

```text
python -m mypy --platform win32 filepilot
```

Regras:

- Executado na raiz do repositorio, no Linux e no Windows, com a configuracao padrao do mypy e sem arquivo de configuracao proprio.
- Saida que comeca por `Success: no issues found` e codigo de saida 0, como em 17.2. O comando nao leva `--no-error-summary`: a linha de sucesso e a evidencia da checagem.
- Nenhum item, gate, script ou workflow usa outra forma de chamar o mypy (nem `mypy . --no-error-summary`, nem `mypy` sem `--platform win32`). Excecao unica: o detalhe de filepilot-v1-1 (`.abt/items/filepilot-v1/filepilot-v1-1.md`), ja entregue e nao editado (19.4), mantem a forma antiga como registro historico. `[DECISAO: aprovada no ponto de checagem; tirar da excecao o trecho sobre a verificacao por grep (VAG-001, opcao B)]`

Substitui a parte de 17.2 que diz "NAO acrescenta mypy ao fluxo do GitHub Actions" e que chama a checagem de "comando manual de desenvolvimento": a checagem passa a ser tambem um passo do fluxo do GitHub Actions (19.3). As demais frases de 17.2 e 17.3 continuam valendo.

A pasta tests/ fica fora da checagem de tipos; nenhum item, gate ou workflow a checa.

`[DECISAO: aprovada no enriquecimento; diverge de comportamento atual de mypy . no workflow]`

### 19.3 Fluxo do GitHub Actions

O passo `Checagem de tipos` de `.github/workflows/tests.yml` (linhas 21 e 22) passa a executar o comando unico de 19.2 no lugar de `mypy . --no-error-summary`.

- O job continua em `windows-latest` com Python 3.12 e instalacao por `pip install -e .[dev]` (`.github/workflows/tests.yml:9` a `:18`); NAO muda a ordem dos passos (`Testes` antes de `Checagem de tipos`) nem o nome do passo.
- NAO acrescenta job, matriz de sistemas operacionais ou etapa de Linux ao workflow: o Linux so roda o comando localmente (17.2).
- Verificacao objetiva: `grep -n "python -m mypy --platform win32 filepilot" .github/workflows/tests.yml` encontra uma linha e `grep -n "mypy . --no-error-summary" .github/workflows/tests.yml` nao encontra nenhuma.

### 19.4 Itens existentes e o item de mypy

Os itens `filepilot-v1-2` a `filepilot-v1-13` (`.abt/items/filepilot-v1/`) trazem `typecheck: mypy . --no-error-summary -> exit 0` nos campos `Verificacao:` e `Gates do item`, e `filepilot-v1-2.md` descreve esse comando nas linhas 18 e 30. Cada ocorrencia passa a usar o comando unico de 19.2, com o mesmo `-> exit 0`.

- `filepilot-v1-1` ja foi entregue e mesclado (commit `940e833`): seu detalhe NAO e editado; o workflow que ele criou e ajustado por item novo (19.3).
- `filepilot-mypy-1` (`.abt/items/filepilot-mypy/filepilot-mypy-1.md`) ja esta atendido: `mypy==2.4.0` esta em `pyproject.toml:19`, entregue por `filepilot-v1-1`. Ele e encerrado sem implementar e esta secao NAO cria item de substituicao para ele. O encerramento e feito pela pessoa na fila; esta secao so o registra.

Escopo negativo: esta secao NAO altera `.abt/SPEC.md` fora de 19; NAO renumera nem edita secoes existentes; NAO edita itens ja entregues.

### 19.5 Pendencias para decisao

Nenhuma pendencia aberta nesta secao.

### 19.6 Traceability Matrix

| Item do escopo | Elementos da SPEC | Status | Origem |
|---|---|---|---|
| Comando unico `python -m mypy --platform win32 filepilot` em todos os itens | 19.2; 19.4; complementa 17.2 | coberto | discovery-notes.md |
| O mesmo comando no passo de checagem de tipos do GitHub Actions | 19.3; substitui o escopo negativo de 17.2 | coberto | discovery-notes.md |
| SPEC 17.2 reflete que o mypy roda no GitHub Actions | 19.2 (substitui a frase de 17.2) | coberto | discovery-notes.md |
| Itens novos para o workflow e para os itens existentes, sem tocar o codigo do produto | 19.3; 19.4; 19.1 (fora de escopo) | coberto | discovery-notes.md |
| `filepilot-mypy-1` registrado como atendido e encerrado sem implementar | 19.4 | coberto | discovery-notes.md |
| Saida `Success: no issues found` e codigo 0 no Linux e no runner windows-latest | 19.2; 19.3 | coberto | discovery-notes.md |
| - | 19.2 a checagem deixa de cobrir a pasta tests/ | - | `[DECISAO: aprovada no enriquecimento; diverge de comportamento atual de mypy . no workflow]` |
| - | 19.2 excecao de filepilot-v1-1 sem trecho sobre verificacao por grep | - | `[DECISAO: aprovada no ponto de checagem; tirar da excecao o trecho sobre a verificacao por grep (VAG-001, opcao B)]` |

## §20 Checagem de tipos com mypy no pyproject

Item: filepilot-mypy-1 (filepilot-2)

## §21 Comando unico de mypy nos itens filepilot-v1-2 a 13

Item: filepilot-mypy-win32-1 (filepilot-2)

## §22 Passo de mypy do workflow com comando unico

Item: filepilot-mypy-win32-2 (filepilot-2)

## §23 Leitura da pasta e pastas protegidas

Item: filepilot-v1-2 (filepilot-2)

## §24 Servico de regras personalizadas

Item: filepilot-v1-3 (filepilot-2)
