# Exportacao - filepilot-v1
Epico: filepilot-v1
Titulo do epico: FilePilot v1 organizador de arquivos para Windows
Branch: abt/spec-filepilot-v1

| Ordem | item_id | Titulo | --depends-on |
|---|---|---|---|
| 1 | filepilot-v1-1 | Fundacao: projeto, dominio, banco e CI Windows | - |
| 2 | filepilot-v1-2 | Leitura da pasta e pastas protegidas | filepilot-v1-1 |
| 3 | filepilot-v1-3 | Servico de regras personalizadas | filepilot-v1-1 |
| 4 | filepilot-v1-4 | Planejamento das operacoes e conflitos de nome | filepilot-v1-1,filepilot-v1-2 |
| 5 | filepilot-v1-5 | Organizacao com historico por arquivo | filepilot-v1-1,filepilot-v1-4 |
| 6 | filepilot-v1-6 | Verificacoes de destino e textos de falha | filepilot-v1-5 |
| 7 | filepilot-v1-7 | Historico e desfazer a ultima organizacao | filepilot-v1-1,filepilot-v1-5 |
| 8 | filepilot-v1-8 | Janela principal, abas e instancia unica | filepilot-v1-1 |
| 9 | filepilot-v1-9 | Aba Organizar: pasta, lista e simulacao | filepilot-v1-2,filepilot-v1-3,filepilot-v1-4,filepilot-v1-8 |
| 10 | filepilot-v1-10 | Aba Organizar: execucao com barra de progresso | filepilot-v1-5,filepilot-v1-6,filepilot-v1-9 |
| 11 | filepilot-v1-11 | Aba Historico e desfazer na interface | filepilot-v1-7,filepilot-v1-9,filepilot-v1-10 |
| 12 | filepilot-v1-12 | Aba Regras e dialogo de regra | filepilot-v1-3,filepilot-v1-8 |
| 13 | filepilot-v1-13 | Executavel Windows com PyInstaller e CI | filepilot-v1-10,filepilot-v1-11,filepilot-v1-12 |
