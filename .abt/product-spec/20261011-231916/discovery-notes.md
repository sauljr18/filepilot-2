# Discovery Notes: FilePilot - mypy nas ferramentas de desenvolvimento e plataforma alvo Windows 10 e 11 (64 bits)

**Data:** 2026-10-11
**Condutora:** Dani Descoberta

Modo: so SPEC + itens

## Contexto e Problema

- **Problema central:** a `.abt/SPEC.md` vigente nao registra a checagem de tipos com mypy entre as ferramentas de desenvolvimento (a secao 4 lista so pytest, pytest-qt e PyInstaller), e a plataforma alvo aparece apenas como frase solta na secao 13, sem estar registrada como decisao da especificacao.
- **Situacao atual (sem o produto):** o pedido e uma mudanca num projeto vivo: a SPEC tem 16 secoes, o epico `filepilot-v1` e 13 itens em `.abt/items/filepilot-v1`. A secao 13 ja diz "Windows 10 e 11 em 64 bits", mas nada diz que mypy faz parte das ferramentas de desenvolvimento.
- **Por que agora:** pedido da pessoa que conduz a especificacao: registrar as duas decisoes (mypy junto com pytest; Windows 10 e 11 em 64 bits como plataforma alvo) antes de a implementacao seguir.

## Personas

### Ana (Usuaria domestica)

- **Papel no produto:** usuaria final que organiza a pasta Downloads (persona da SPEC, secao 1).
- **Objetivo principal:** manter a pasta em ordem com poucos cliques e sem medo de perder arquivo.
- **Frustracao atual:** nenhuma causada por esta mudanca; a mudanca e interna (ferramentas de desenvolvimento e registro de plataforma) e nao altera o que ela ve.

### Carlos (Usuario que cria regras)

- **Papel no produto:** usuario final que cria regras para o proprio jeito de guardar arquivos (persona da SPEC, secao 1).
- **Objetivo principal:** organizar os arquivos com regras personalizadas.
- **Frustracao atual:** nenhuma causada por esta mudanca; ela nao altera o que ele ve.

## Funcionalidades Core (v1)

1. Registro do mypy: a SPEC registra o mypy como ferramenta de desenvolvimento, junto com o pytest, na tabela de stack (secao 4) e na lista de dependencias de desenvolvimento do `pyproject.toml`.
2. Registro da plataforma alvo: a SPEC registra como decisao da especificacao que a plataforma alvo e Windows 10 e 11 em 64 bits.

## Contexto Tecnico

### Stack Preferida

| Camada | Tecnologia | Motivo |
|---|---|---|
| Linguagem e backend | Python 3.12 | Inalterada: a do manifesto e da SPEC vigente |
| Interface grafica | PySide6 6.12.0 | Inalterada: a da SPEC vigente |
| Banco de dados | SQLite pelo modulo `sqlite3` | Inalterada: a da SPEC vigente |
| Testes | pytest 9.1.1 e pytest-qt 4.5.0 | Inalterados: os da SPEC vigente |
| Checagem de tipos | mypy (versao a fixar na SPEC; a pessoa nao indicou) | Pedido da pessoa: faz parte das ferramentas de desenvolvimento, junto com pytest |
| Empacotamento | PyInstaller 6.22.3 | Inalterado: o da SPEC vigente |

### Integracoes Externas

Nenhuma integracao externa nova: a mudanca nao acrescenta servico nem API externa.

### Restricoes de Desempenho

Nenhuma restricao de desempenho pedida.

## Escopo v1

### Dentro do Escopo

- Registrar o mypy como ferramenta de desenvolvimento, junto com o pytest, na SPEC.
- Registrar Windows 10 e 11 em 64 bits como plataforma alvo, como decisao da especificacao.

### Fora do Escopo (v1)

- Mudar codigo do produto.
- Anotar tipos no codigo existente.
- Suporte a macOS ou Linux como plataforma alvo.
- Reabrir PRD ou stack.

## Metricas de Sucesso

- Ferramenta registrada: 1 ferramenta nova (mypy) registrada ao lado do pytest na SPEC em 1 execucao desta especificacao (baseline atual: 0).
- Decisao de plataforma registrada: 1 decisao (Windows 10 e 11, 64 bits) registrada na SPEC em 1 execucao desta especificacao (baseline atual: 1 frase solta na secao 13, sem registro como decisao).
- Requisitos do PRD alterados: 0 em 1 execucao desta especificacao (baseline atual: 0).

Retorno: descoberta
Proxima fase: spec
Fases puladas: prd, validacao-prd, stack
