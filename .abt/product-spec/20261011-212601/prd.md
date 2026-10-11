# PRD: FilePilot v1

## Sumario Executivo

A pasta Downloads de pessoas comuns no Windows vira uma bagunca, com todos os tipos de arquivo misturados, e hoje a unica saida e organizar tudo na mao, arquivo por arquivo. O FilePilot e um aplicativo desktop para Windows que organiza os arquivos de uma pasta escolhida em subpastas por categoria (documentos, imagens, videos e arquivos compactados), com regras personalizadas, e que mostra antes, em um modo de simulacao (dry-run), tudo o que vai acontecer sem alterar nenhum arquivo.

O publico e formado por Ana, usuaria domestica que quer a pasta em ordem com poucos cliques e sem medo de perder arquivo, e Carlos, que quer organizar do proprio jeito com regras personalizadas. A confianca vem de tres garantias: a simulacao nao altera nada, nenhum arquivo e sobrescrito e a ultima organizacao pode ser desfeita, devolvendo cada arquivo ao lugar original.

## Personas

### Ana (Usuaria domestica no Windows)

**Papel:** usuaria principal; escolhe uma pasta como Downloads e organiza seus arquivos por categoria.
**Objetivos:** deixar a pasta em ordem com poucos cliques, sem medo de perder arquivo.
**Frustracoes atuais:** a pasta Downloads esta desorganizada, com tudo misturado, e organiza-la na mao toma tempo.

### Carlos (Usuario que organiza com mais criterio)

**Papel:** usuario secundario; define regras personalizadas para o proprio jeito de guardar arquivos.
**Objetivos:** criar e manter regras personalizadas que organizem os arquivos do jeito dele.
**Frustracoes atuais:** organizar na mao nao segue o criterio dele e as categorias padrao nao cobrem tudo o que ele guarda.

## User Stories

### Selecao e identificacao

- **US-001**: Como Ana, eu quero escolher a pasta a organizar pelo explorador de arquivos do Windows, para que eu aponte a pasta Downloads sem digitar caminho.
  - AC (caminho feliz): Sistema abre o explorador de arquivos, e ao confirmar uma pasta, exibe o caminho escolhido e a quantidade de arquivos do nivel dela.
  - AC (erro/borda): Quando a pasta escolhida nao pode ser lida ou esta vazia, sistema exibe a mensagem correspondente e nao habilita a simulacao nem a organizacao.
- **US-002**: Como Ana, eu quero ver cada arquivo da pasta com a categoria identificada pela extensao, para que eu entenda onde cada um vai parar.
  - AC (caminho feliz): Sistema lista cada arquivo do nivel da pasta com extensao e categoria (documentos, imagens, videos ou compactados).
  - AC (erro/borda): Arquivo com extensao fora de toda categoria e sem regra personalizada aparece como "sem categoria" e permanece onde esta.

### Simulacao

- **US-003**: Como Ana, eu quero rodar uma simulacao antes de organizar, para que eu veja tudo o que vai acontecer sem que nada seja movido.
  - AC (caminho feliz): Sistema lista cada operacao prevista (arquivo, origem e destino) e nenhum arquivo e criado, movido ou alterado no disco.
  - AC (erro/borda): Quando nenhum arquivo da pasta tem categoria ou regra aplicavel, sistema informa que nao ha operacoes a executar e a organizacao real fica indisponivel.
- **US-004**: Como Carlos, eu quero que a simulacao considere as minhas regras personalizadas, para que eu confira o efeito delas antes de organizar.
  - AC (caminho feliz): Na simulacao, cada operacao decorrente de regra personalizada mostra o nome da regra aplicada.
  - AC (erro/borda): Quando duas regras casam com o mesmo arquivo, sistema mostra na simulacao a regra que prevalece.

### Organizacao

- **US-005**: Como Ana, eu quero organizar a pasta escolhida em subpastas por categoria, para que a pasta fique em ordem sem eu mover arquivo por arquivo.
  - AC (caminho feliz): Sistema cria as subpastas de categoria necessarias na pasta escolhida e move cada arquivo para a subpasta da sua categoria.
  - AC (erro/borda): Arquivo sem categoria e sem regra aplicavel nao e movido e continua na pasta escolhida.
- **US-006**: Como Ana, eu quero acompanhar o andamento da organizacao, para que eu saiba quanto falta e que o aplicativo nao travou.
  - AC (caminho feliz): Sistema exibe barra de progresso com a quantidade de arquivos processados sobre o total, atualizada durante toda a organizacao.
  - AC (erro/borda): Quando a organizacao termina com falhas, sistema encerra a barra em 100% e exibe a quantidade de arquivos movidos e de falhas.
- **US-007**: Como Ana, eu quero que um arquivo com nome repetido no destino nunca seja sobrescrito, para que eu nao perca nenhum arquivo.
  - AC (caminho feliz): Quando ja existe no destino um arquivo com o mesmo nome, sistema move o arquivo novo com nome acrescido de sufixo numerico (por exemplo, nome (1).pdf) e o arquivo existente permanece intacto.
  - AC (erro/borda): Quando o nome com sufixo tambem existe, sistema incrementa o numero ate encontrar um nome livre.
- **US-008**: Como Ana, eu quero que um arquivo bloqueado ou sem permissao nao interrompa a organizacao, para que o restante da pasta seja organizado.
  - AC (caminho feliz): Sistema pula o arquivo que nao pode ser movido, continua com os demais e registra a falha no historico com o motivo.
  - AC (erro/borda): Quando todos os arquivos falham, sistema conclui sem mover nenhum arquivo e exibe a quantidade de falhas.

### Historico e desfazer

- **US-009**: Como Ana, eu quero consultar o historico de operacoes, para que eu saiba o que o FilePilot ja fez nas minhas pastas.
  - AC (caminho feliz): Sistema lista cada organizacao com data e hora, pasta, quantidade de arquivos movidos e quantidade de falhas, e permite ver o detalhe de cada arquivo.
  - AC (erro/borda): Quando nao ha nenhuma organizacao registrada, sistema exibe o historico vazio com mensagem informativa.
- **US-010**: Como Ana, eu quero desfazer a ultima organizacao, para que os arquivos voltem ao lugar onde estavam se eu nao gostar do resultado.
  - AC (caminho feliz): Sistema devolve cada arquivo movido na ultima organizacao ao caminho e ao nome originais e registra o desfazer no historico.
  - AC (erro/borda): Quando um arquivo foi apagado, movido ou renomeado depois da organizacao, sistema nao o restaura, restaura os demais e informa quais nao puderam voltar.

### Regras personalizadas

- **US-011**: Como Carlos, eu quero criar regras personalizadas de organizacao, para que meus arquivos sejam guardados do meu jeito.
  - AC (caminho feliz): Sistema permite definir uma regra com nome, as extensoes que ela cobre e a subpasta de destino, e a regra passa a valer nas proximas simulacoes e organizacoes.
  - AC (erro/borda): Quando a regra esta sem nome, sem extensao ou sem destino, ou o destino e invalido para o Windows, sistema recusa o salvamento e indica o campo com problema.
- **US-012**: Como Carlos, eu quero editar e remover minhas regras, para que eu ajuste a organizacao quando meu criterio mudar.
  - AC (caminho feliz): Sistema permite alterar ou excluir uma regra e a mudanca vale a partir da proxima simulacao ou organizacao, sem afetar o historico ja registrado.
  - AC (erro/borda): Antes de excluir uma regra, sistema pede confirmacao e, se a pessoa cancelar, a regra permanece inalterada.

## Requisitos Funcionais

### FR-001: Selecao de pasta
- **Descricao:** o sistema permite escolher a pasta a organizar pelo explorador de arquivos do Windows.
- **Gatilho:** a pessoa aciona a escolha de pasta.
- **Ator:** Ana.
- **Comportamento:** o sistema abre o seletor de pastas do Windows; ao confirmar, exibe o caminho e a quantidade de arquivos do nivel da pasta; pasta ilegivel ou vazia mostra mensagem e mantem simulacao e organizacao indisponiveis.
- **Origem:** US-001

### FR-002: Identificacao por extensao e categorizacao
- **Descricao:** o sistema identifica cada arquivo do nivel da pasta pela extensao e o classifica em documentos, imagens, videos ou compactados.
- **Gatilho:** a pasta e escolhida ou atualizada.
- **Ator:** Ana.
- **Comportamento:** a extensao e comparada sem diferenciar maiusculas de minusculas; a lista mostra arquivo, extensao e categoria; arquivo sem categoria e sem regra aplicavel e marcado "sem categoria" e nunca e movido. Categorias padrao e subpastas: Documentos (pdf, doc, docx, txt, rtf, odt, xls, xlsx, ppt, pptx, csv), Imagens (jpg, jpeg, png, gif, bmp, webp, svg, tiff), Videos (mp4, mkv, avi, mov, wmv, webm) e Compactados (zip, rar, 7z, tar, gz); extensao fora dessa lista so e movida por regra personalizada. Arquivos ocultos ou de sistema sao ignorados (nao aparecem na lista e nao sao movidos); atalhos (.lnk) seguem a regra normal de extensao.
- **Origem:** US-002

### FR-003: Simulacao (dry-run)
- **Descricao:** o sistema mostra todas as operacoes que a organizacao executaria, sem alterar nenhum arquivo.
- **Gatilho:** a pessoa aciona a simulacao.
- **Ator:** Ana e Carlos.
- **Comportamento:** o sistema calcula as mesmas operacoes da organizacao real e lista cada uma com arquivo, origem, destino e, quando houver, a regra aplicada; nao cria pastas, nao move, nao renomeia e nao grava no historico de organizacoes; sem operacoes, informa isso e torna a organizacao real indisponivel.
- **Origem:** US-003, US-004

### FR-004: Organizacao em subpastas
- **Descricao:** o sistema move os arquivos para subpastas de categoria dentro da pasta escolhida.
- **Gatilho:** a pessoa aciona a organizacao.
- **Ator:** Ana.
- **Comportamento:** o sistema cria as subpastas necessarias, move cada arquivo com categoria ou regra aplicavel para a subpasta de destino e deixa os demais onde estao; so os arquivos do nivel da pasta escolhida sao tratados.
- **Origem:** US-005

### FR-005: Barra de progresso
- **Descricao:** o sistema exibe o andamento da organizacao.
- **Gatilho:** a organizacao e iniciada.
- **Ator:** Ana.
- **Comportamento:** a barra mostra arquivos processados sobre o total e e atualizada durante toda a execucao; ao terminar, mostra 100% e o resumo de movidos e falhas.
- **Origem:** US-006

### FR-006: Conflito de nome no destino
- **Descricao:** o sistema nunca sobrescreve um arquivo existente no destino.
- **Gatilho:** o destino ja contem um arquivo com o mesmo nome.
- **Ator:** Ana.
- **Comportamento:** o arquivo novo recebe sufixo numerico (nome (1).ext, nome (2).ext e assim por diante) ate um nome livre; o arquivo existente permanece intacto; o nome final fica registrado no historico.
- **Origem:** US-007

### FR-007: Falha por arquivo
- **Descricao:** a falha ao mover um arquivo nao interrompe a organizacao.
- **Gatilho:** um arquivo esta em uso por outro programa, sem permissao ou inacessivel.
- **Ator:** Ana.
- **Comportamento:** o sistema pula o arquivo, continua com os demais e registra no historico o arquivo e o motivo da falha; ao final informa a quantidade de falhas.
- **Origem:** US-008

### FR-008: Historico de operacoes
- **Descricao:** o sistema registra e exibe o historico das organizacoes e dos desfazeres.
- **Gatilho:** uma organizacao ou um desfazer termina; a pessoa abre o historico.
- **Ator:** Ana.
- **Comportamento:** cada registro traz data e hora, pasta, quantidade de arquivos movidos e de falhas e, por arquivo, origem, destino final e situacao; o historico e mantido entre sessoes do aplicativo [INFERIDO]; sem registros, exibe o historico vazio.
- **Origem:** US-009

### FR-009: Desfazer a ultima organizacao
- **Descricao:** o sistema devolve os arquivos movidos pela ultima organizacao ao lugar original.
- **Gatilho:** a pessoa aciona o desfazer.
- **Ator:** Ana.
- **Comportamento:** cada arquivo movido volta ao caminho e ao nome originais, inclusive os que receberam sufixo por conflito; arquivo apagado, movido ou renomeado depois da organizacao nao e restaurado e e listado como nao restaurado; o desfazer vale somente para a ultima organizacao [INFERIDO] e e registrado no historico; subpastas de categoria que ficarem vazias depois do desfazer sao removidas e as que ainda tiverem arquivo permanecem; o desfazer so fica disponivel quando ha uma ultima organizacao ainda nao desfeita e, depois de desfeita, fica indisponivel ate a proxima organizacao.
- **Origem:** US-010

### FR-010: Gestao de regras personalizadas
- **Descricao:** o sistema permite criar, editar e remover regras personalizadas.
- **Gatilho:** a pessoa abre a configuracao de regras.
- **Ator:** Carlos.
- **Comportamento:** uma regra tem nome, uma ou mais extensoes e subpasta de destino; o salvamento e recusado se faltar campo ou se o destino for invalido para o Windows; a extensao e aceita com ou sem ponto inicial e sem diferenciar maiusculas de minusculas; a subpasta de destino fica sempre dentro da pasta escolhida, nunca como caminho absoluto nem com ..; extensao ja coberta por outra regra e permitida e vale a primeira da lista; a exclusao pede confirmacao; as regras sao mantidas entre sessoes do aplicativo [INFERIDO].
- **Origem:** US-011, US-012

### FR-011: Aplicacao das regras
- **Descricao:** o sistema aplica as regras personalizadas junto com as categorias padrao.
- **Gatilho:** simulacao ou organizacao.
- **Ator:** Carlos.
- **Comportamento:** regra personalizada prevalece sobre a categoria padrao quando ambas casam com o arquivo [INFERIDO]; entre duas regras personalizadas que casam, prevalece a primeira da lista [INFERIDO]; a regra aplicada e mostrada na simulacao.
- **Origem:** US-004, US-011

## Requisitos Nao-Funcionais

Nenhum requisito de desempenho, responsividade ou escalabilidade foi definido pela pessoa que pediu o produto, por decisao dela; por isso esta secao nao traz valores para eles e nenhum deve ser presumido nas fases seguintes.

### NFR-001: Seguranca dos arquivos
Nenhum arquivo e sobrescrito ou apagado pelo sistema (0 ocorrencias) e nenhuma operacao ocorre fora da pasta escolhida e das subpastas de categoria dela (0 operacoes). A simulacao altera 0 arquivos.

### NFR-002: Integridade do historico
Cada arquivo movido tem seu registro de origem e destino gravado antes do fim da organizacao, de modo que o desfazer restaure 100% dos arquivos movidos e ainda presentes no destino.

## Metricas de Sucesso

**M1 Organizacao completa**: 100% dos arquivos de categoria conhecida da pasta escolhida ficam em subpasta da categoria apos organizar, ate a v1 (baseline: organizacao manual, sem medicao).
**M2 Simulacao segura**: a simulacao altera 0 arquivos e lista 100% das operacoes que a organizacao real executaria, ate a v1 (baseline: nao existe simulacao).
**M3 Desfazer fiel**: desfazer a ultima organizacao restaura 100% dos arquivos movidos ao caminho original, ate a v1 (baseline: nao existe desfazer).

## Fora do Escopo (v1)

- Organizacao automatica em segundo plano ou agendada: so roda quando a pessoa pede.
- Subpastas internas da pasta escolhida: so os arquivos do nivel da pasta sao organizados.
- Versoes para macOS e Linux: so Windows.
- Sincronizacao com nuvem e organizacao por conteudo do arquivo: so por extensao e regras.
- Recursos de rede.
- Organizacao por inteligencia artificial.
- Renomear arquivos (exceto o sufixo automatico de nome repetido no destino).
- Desfazer organizacoes anteriores a ultima.
- Mover para uma subpasta "Outros" os arquivos sem categoria: eles ficam onde estao.

## Dependencias e Riscos

| # | Dependencia/Risco | Impacto | Mitigacao |
|---|---|---|---|
| D-001 | Sistema de arquivos do Windows: arquivos em uso ou sem permissao nao podem ser movidos | Medio | Pular o arquivo, registrar a falha e seguir com os demais (FR-007) |
| D-002 | Arquivo alterado ou apagado fora do aplicativo depois da organizacao impede a restauracao completa | Medio | Restaurar o que for possivel e listar os arquivos nao restaurados (FR-009) |
| D-003 | Distribuicao como executavel para Windows: o executavel pode ser bloqueado ou sinalizado por antivirus ou pelo SmartScreen | Medio | Tratar na fase de stack e na distribuicao; fora do comportamento do produto |
| D-004 | Perda ou corrupcao do historico impede o desfazer | Alto | Gravar o registro de cada movimentacao antes de concluir a organizacao (NFR-002) |

## Registro da auditoria

**Data:** 2026-10-11
**Auditora:** Vera Verificacao
**Perguntas feitas:** 4
**Mudancas aplicadas:**
- FR-002: categorias padrao com extensoes e subpastas (Documentos, Imagens, Videos, Compactados).
- FR-002: arquivos ocultos ou de sistema ignorados; atalhos (.lnk) seguem a regra normal de extensao.
- FR-009: subpastas de categoria vazias removidas apos o desfazer; desfazer disponivel so com ultima organizacao nao desfeita.
- FR-010: extensao com ou sem ponto e sem diferenciar maiusculas; destino dentro da pasta escolhida; extensao repetida permitida, vale a primeira regra.
**Confirmados sem alteracao:** US-001 a US-012, FR-001, FR-003 a FR-008, FR-011, NFR-001 e NFR-002, M1 a M3, Fora do Escopo, D-001 a D-004.
**Pendencias:** sem requisitos de desempenho, responsividade e escalabilidade, por decisao da pessoa que pediu o produto.
