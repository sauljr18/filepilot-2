# Discovery Notes: FilePilot

**Data:** 2026-10-11
**Condutora:** Dani Descoberta

Modo: completo

## Contexto e Problema

- **Problema central:** a pasta Downloads vira uma bagunca, com todos os tipos de arquivo misturados, e pessoas comuns no Windows precisam organiza-la na mao.
- **Situacao atual (sem o produto):** a organizacao dos arquivos em subpastas por categoria e feita manualmente, arquivo por arquivo.
- **Por que agora:** a pessoa que pediu o produto quer que usuarios comuns no Windows organizem pastas como Downloads por categoria sem fazer na mao e sem medo de perder arquivos.

## Personas

### Ana (Usuaria domestica no Windows)

- **Papel no produto:** usuaria principal; escolhe uma pasta como Downloads e organiza seus arquivos por categoria.
- **Objetivo principal:** deixar a pasta em ordem com poucos cliques, sem medo de perder arquivo (por isso a simulacao e o desfazer).
- **Frustracao atual:** a pasta Downloads esta desorganizada, com tudo misturado, e organiza-la na mao toma tempo.

### Carlos (Usuario que organiza com mais criterio)

- **Papel no produto:** usuario secundario; define regras personalizadas para o proprio jeito de guardar arquivos.
- **Objetivo principal:** criar e manter regras personalizadas que organizem os arquivos do jeito dele.
- **Frustracao atual:** organizar na mao nao segue o criterio dele e as categorias padrao nao cobrem tudo o que ele guarda.

## Funcionalidades Core (v1)

1. Selecao de pasta: o usuario escolhe a pasta a organizar pelo explorador de arquivos do Windows.
2. Identificacao por extensao: o sistema identifica cada arquivo da pasta pela extensao.
3. Categorizacao: o sistema classifica os arquivos em documentos, imagens, videos e arquivos compactados.
4. Simulacao (dry-run): o usuario visualiza todas as operacoes que seriam feitas, sem que nenhum arquivo seja alterado.
5. Organizacao em subpastas: o sistema move os arquivos para subpastas por categoria dentro da pasta escolhida.
6. Barra de progresso: o usuario acompanha o andamento da organizacao.
7. Historico de operacoes: o sistema registra as operacoes feitas, inclusive as falhas, e o usuario as consulta.
8. Desfazer a ultima organizacao: o usuario devolve os arquivos da ultima organizacao ao caminho original.
9. Regras personalizadas: o usuario cria, edita e remove regras proprias de organizacao, alem das categorias padrao.
10. Tratamento de conflitos e falhas: nome repetido no destino renomeia o arquivo novo (por exemplo, nome (1).pdf) sem sobrescrever; arquivo bloqueado ou sem permissao e pulado e registrado no historico sem interromper os demais; arquivo de extensao sem categoria e sem regra fica onde esta.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Backend | Python | Stack sugerida pela pessoa que pediu o produto |
| Interface grafica | PySide6 | Stack sugerida; interface desktop com seletor de pasta nativo |
| Banco de dados | SQLite | Stack sugerida; guarda historico de operacoes e regras |
| Testes | Pytest | Stack sugerida |
| Distribuicao | Executavel para Windows | Pessoas comuns no Windows instalam sem ambiente Python |

### Integracoes Externas

- Sistema de arquivos do Windows: leitura, movimentacao e restauracao dos arquivos da pasta escolhida.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- Aplicativo desktop para Windows com as funcionalidades core listadas acima.
- Modo de simulacao (dry-run) como diferencial do produto.
- Categorias padrao: documentos, imagens, videos e arquivos compactados, mais regras personalizadas.

### Fora do Escopo (v1)

- Organizacao automatica em segundo plano ou agendada: so roda quando a pessoa pede.
- Subpastas internas da pasta escolhida: so os arquivos do nivel da pasta sao organizados.
- Versoes para macOS e Linux: so Windows.
- Sincronizacao com nuvem e organizacao por conteudo do arquivo: so por extensao e regras.
- Recursos de rede.
- Organizacao por inteligencia artificial.
- Renomear arquivos (exceto o sufixo automatico de nome repetido no destino).

## Metricas de Sucesso

- M1 Organizacao completa: 100% dos arquivos de categoria conhecida da pasta escolhida ficam em subpasta da categoria apos organizar, na v1 (baseline atual: organizacao manual, sem medicao).
- M2 Simulacao segura: a simulacao altera 0 arquivos e lista 100% das operacoes que a organizacao real executaria, na v1 (baseline atual: nao existe simulacao).
- M3 Desfazer fiel: desfazer a ultima organizacao restaura 100% dos arquivos movidos ao caminho original, na v1 (baseline atual: nao existe desfazer).

Retorno: descoberta
