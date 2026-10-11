# Stack Decision: FilePilot

**Data:** 2026-10-11

## Stack Final

| Componente | Tecnologia | Versao | Justificativa |
|---|---|---|---|
| Linguagem e backend | Python | 3.12 | Stack sugerida pela pessoa; `pathlib`, `os` e `shutil` da biblioteca padrao cobrem leitura, movimentacao e restauracao de arquivos sem dependencia externa |
| Interface grafica | PySide6 | 6.12.0 | Stack sugerida; traz o seletor de pastas nativo do Windows (`QFileDialog`), `QProgressBar` e threads para manter a interface responsiva durante a organizacao |
| Banco de dados | SQLite pelo modulo `sqlite3` | stdlib do Python 3.12 | Stack sugerida; arquivo unico local, sem servidor, para historico, registros por arquivo e regras |
| Testes | pytest | 9.1.1 | Stack sugerida; `tmp_path` cria pastas temporarias para testar movimentacao, conflito e desfazer sem tocar em arquivos reais |
| Testes de interface | pytest-qt | 4.5.0 | Permite testar os widgets do PySide6 (selecao, simulacao, progresso) dentro do pytest |
| Empacotamento | PyInstaller | 6.22.3 | Gera o executavel para Windows a partir do projeto Python; modo `--onedir` (pasta com o `.exe`) |
| Build e testes no Windows | GitHub Actions, runner `windows-latest` | - | PyInstaller nao gera executavel de outro sistema; o build e os testes dependentes do Windows precisam rodar no Windows |

## Capacidades Confirmadas

| Requisito | Atendido por |
|---|---|
| FR-001 Selecao de pasta | `QFileDialog.getExistingDirectory` do PySide6, que usa o seletor nativo do Windows; leitura do nivel da pasta com `pathlib.Path.iterdir` |
| FR-002 Identificacao por extensao e categorias | `pathlib.Path.suffix` comparado em minusculas com tabelas de categoria; arquivos ocultos ou de sistema detectados por `os.stat().st_file_attributes` com as constantes `stat.FILE_ATTRIBUTE_HIDDEN` e `stat.FILE_ATTRIBUTE_SYSTEM` da biblioteca padrao |
| FR-003 Simulacao (dry-run) | Camada de planejamento que so calcula a lista de operacoes (arquivo, origem, destino, regra) e nunca chama a movimentacao; NFR-001 garantido por teste que compara a pasta antes e depois |
| FR-004 Organizacao em subpastas | `Path.mkdir(exist_ok=True)` e movimentacao pela camada de execucao, a mesma lista da simulacao |
| FR-005 Barra de progresso | Execucao em thread de trabalho (`QThread` com sinais) atualizando um `QProgressBar` na thread da interface |
| FR-006 Conflito de nome | Destino livre calculado com sufixo ` (n)`; a movimentacao nao sobrescreve (ver Decisoes de Design) |
| FR-007 Falha por arquivo | `PermissionError` e `OSError` capturados por arquivo; falha gravada no historico e execucao segue |
| FR-008 Historico | `sqlite3`: tabela de organizacoes e tabela de operacoes por arquivo, mantidas entre sessoes |
| FR-009 Desfazer a ultima organizacao | Operacoes por arquivo do banco lidas em ordem inversa; `os.rename` de volta ao caminho original e remocao das subpastas de categoria que ficarem vazias com `Path.rmdir` |
| FR-010 Gestao de regras | Tabela de regras no `sqlite3` com campo de posicao (ordem da lista); validacao de destino com `pathlib` |
| FR-011 Aplicacao das regras | Camada de planejamento consulta as regras em ordem de posicao antes das categorias padrao |
| NFR-001 Seguranca dos arquivos | Movimentacao sem sobrescrita e verificacao de que todo destino fica dentro da pasta escolhida (`Path.resolve` e `is_relative_to`) |
| NFR-002 Integridade do historico | Registro da operacao gravado com `commit` imediatamente apos cada movimentacao bem sucedida |

## Lacunas Resolvidas

| Lacuna | Severidade | Resolucao escolhida | Motivo |
|---|---|---|---|
| GAP-001: o PyInstaller nao gera `.exe` a partir de Linux ou macOS | High | Build do executavel e testes que dependem do Windows (atributos de arquivo oculto, arquivo em uso) rodam no runner `windows-latest` do GitHub Actions; o repositorio ja esta no GitHub | Sem um ambiente Windows no build, o requisito de distribuicao como executavel para Windows nao e atendido |
| GAP-002: arquivo em uso por outro programa e atributos do Windows nao se reproduzem em Linux | Medium | Testes unitarios usam mocks e `pytest.mark.skipif` para o que e exclusivo do Windows; o caso real (FR-007) e coberto no runner Windows | Mantem a suite rodando em desenvolvimento fora do Windows sem perder a cobertura no Windows |
| GAP-003: executavel sem assinatura de codigo pode exibir aviso do SmartScreen na primeira execucao (D-003) | Medium | Assinatura de codigo fica fora da v1; a pessoa ve o aviso e escolhe executar mesmo assim | A assinatura exige certificado pago e esta fora do pedido; o risco D-003 do PRD ja e aceito como de distribuicao |
| GAP-004: o PRD nao define requisito de desempenho, responsividade nem escalabilidade | Low | Nenhum numero e presumido; a organizacao roda em thread de trabalho para a interface nao travar, sem meta medida | Decisao da pessoa registrada no PRD (pendencia da auditoria) |

## Custo Operacional Estimado (MVP)

| Componente | Plano/Uso | Custo/mes |
|---|---|---|
| Python, PySide6, pytest, pytest-qt, PyInstaller | Software livre, sem servico | US$ 0 |
| SQLite | Arquivo local, sem servidor | US$ 0 |
| GitHub Actions `windows-latest` | Dentro da franquia gratuita do plano do repositorio | US$ 0 |

**Total estimado: US$ 0/mes** para 1 usuario por maquina no MVP (aplicativo local, sem servidor, sem rede). Uso do runner Windows acima da franquia gratuita nao foi estimado.

## Gotchas Conhecidos

Nenhuma particularidade registrada nas fontes do projeto.

## Decisoes de Design

- **Movimentacao sem sobrescrita:** a movimentacao usa `os.rename`, que no Windows falha com `FileExistsError` se o destino existe, em vez de `os.replace` ou `shutil.move`, que sobrescrevem. Assim o NFR-001 vale mesmo se um arquivo aparecer no destino entre o planejamento e a execucao; nesse caso o sistema recalcula o sufixo ` (n)` e tenta de novo. Organizar dentro da mesma pasta e do mesmo volume torna `os.rename` suficiente.
- **Uma lista de operacoes para simulacao e organizacao:** a simulacao e a organizacao real usam a mesma camada de planejamento; a diferenca e so a etapa de execucao. Isso sustenta M2 (a simulacao lista 100% das operacoes que a organizacao executaria).
- **Historico gravado por arquivo, em ordem:** cada operacao tem um numero de ordem; o desfazer percorre em ordem inversa e usa o nome final gravado (inclusive com sufixo), o que sustenta M3 e o NFR-002.
- **Local do banco:** o arquivo SQLite fica na pasta de dados do aplicativo do usuario (`QStandardPaths.AppDataLocation`), fora da pasta organizada, para nao ser movido nem listado.
- **Empacotamento `--onedir`:** escolhido em vez do arquivo unico (`--onefile`) porque inicia sem extrair para pasta temporaria e costuma gerar menos alertas de antivirus (D-003). O PySide6 e distribuido sob LGPLv3; manter as bibliotecas Qt como arquivos separados facilita cumprir a licenca. A entrega ao usuario e a pasta compactada com o `.exe`.
- **Camadas:** a logica (categorias, regras, planejamento, execucao, historico) fica separada da interface PySide6, para testar tudo com pytest sem abrir janela, exceto os poucos testes de widgets com pytest-qt.
- **Python 3.12:** versao com suporte da stack escolhida e disponivel no runner do GitHub Actions; fixa o ambiente do build.

Retorno: stack
