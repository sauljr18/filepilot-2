# Exportacao - filepilot-fix3
Epico: filepilot-fix3
Titulo do epico: Correcao de sete defeitos remanescentes da main do FilePilot
Branch: abt/spec-filepilot-fix3

| Ordem | item_id | Titulo | --depends-on |
|---|---|---|---|
| 1 | filepilot-fix3-1 | Checagem de tipos do mypy cobre a pasta de testes | filepilot-mypy-win32-1,filepilot-mypy-win32-2 |
| 2 | filepilot-fix3-2 | Arquivo .gitignore na raiz do repositorio | - |
| 3 | filepilot-fix3-3 | Laco de atalhos detectado tambem no Windows | filepilot-fix2-4 |
| 4 | filepilot-fix3-4 | Desfazer com laco de atalhos vira PASTA_INVALIDA | filepilot-fix2-4,filepilot-v1-11 |
| 5 | filepilot-fix3-5 | Historico mostra a data como veio quando ela e invalida | filepilot-v1-11 |
| 6 | filepilot-fix3-6 | Barra de progresso some ao desfazer a organizacao | filepilot-v1-10,filepilot-v1-11 |
| 7 | filepilot-fix3-7 | Testes de instancia unica e desfazer falham em vez de travar | filepilot-fix2-3,filepilot-v1-11 |
