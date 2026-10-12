import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.services.rules import create_rule, list_rules

MSG_NAME = "Informe um nome de até 60 caracteres."
MSG_EXTENSIONS = "Informe ao menos uma extensão (letras e números, até 15)."
MSG_DESTINATION = "Informe uma subpasta válida dentro da pasta escolhida."


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "filepilot.db")
    yield connection
    connection.close()


def _invalid_fields(
    conn: sqlite3.Connection, name: str, extensions: list[str], destination: str
) -> dict[str, str]:
    with pytest.raises(FilePilotError) as info:
        create_rule(conn, name, extensions, destination)
    assert info.value.code == "REGRA_INVALIDA"
    assert info.value.fields is not None
    return info.value.fields


def test_extensoes_sao_normalizadas_e_a_regra_entra_na_ultima_posicao(
    conn: sqlite3.Connection,
) -> None:
    create_rule(conn, "Primeira", ["jpg"], "Fotos")

    rule = create_rule(conn, "Planilhas", ["PDF", ".xlsx"], "Trabalho")

    assert rule.extensions == frozenset({"pdf", "xlsx"})
    assert rule.position == 2
    stored = conn.execute(
        "SELECT extension FROM rule_extensions WHERE rule_id = ? ORDER BY extension",
        (rule.id,),
    ).fetchall()
    assert [row[0] for row in stored] == ["pdf", "xlsx"]


def test_list_rules_devolve_por_position_crescente(conn: sqlite3.Connection) -> None:
    first = create_rule(conn, "Zebra", ["z"], "Z")
    second = create_rule(conn, "Abelha", ["a"], "A")
    third = create_rule(conn, "Macaco", ["m"], "M")

    rules = list_rules(conn)

    assert [rule.id for rule in rules] == [first.id, second.id, third.id]
    assert [rule.position for rule in rules] == [1, 2, 3]
    assert rules[1].extensions == frozenset({"a"})


def test_list_rules_sem_regras_devolve_lista_vazia(conn: sqlite3.Connection) -> None:
    assert list_rules(conn) == []


def test_nome_vazio_ou_so_com_espacos_e_invalido(conn: sqlite3.Connection) -> None:
    assert _invalid_fields(conn, "", ["pdf"], "Docs") == {"name": MSG_NAME}
    assert _invalid_fields(conn, "   ", ["pdf"], "Docs") == {"name": MSG_NAME}


def test_nome_aceita_60_caracteres_e_recusa_61(conn: sqlite3.Connection) -> None:
    rule = create_rule(conn, "a" * 60, ["pdf"], "Docs")
    assert len(rule.name) == 60

    assert _invalid_fields(conn, "a" * 61, ["pdf"], "Docs") == {"name": MSG_NAME}


def test_nome_tem_as_pontas_aparadas(conn: sqlite3.Connection) -> None:
    rule = create_rule(conn, "  Fotos  ", ["jpg"], "Fotos")

    assert rule.name == "Fotos"


@pytest.mark.parametrize("extensions", [["a-b"], [""], [], ["a b"], ["a" * 16], ["pdf", "x.y"]])
def test_extensao_invalida_ou_ausente_levanta_regra_invalida(
    conn: sqlite3.Connection, extensions: list[str]
) -> None:
    assert _invalid_fields(conn, "Regra", extensions, "Docs") == {
        "extensions": MSG_EXTENSIONS
    }


def test_extensao_com_15_caracteres_e_valida(conn: sqlite3.Connection) -> None:
    rule = create_rule(conn, "Regra", ["a" * 15], "Docs")

    assert rule.extensions == frozenset({"a" * 15})


@pytest.mark.parametrize(
    "destination",
    [
        "..\\x",
        ".",
        "a//b",
        "CON",
        "a:b",
        "C:\\x",
        "",
        "/abs",
        "\\\\servidor\\x",
        "a/",
        "a/../b",
        "nome.",
        "nome ",
        "a/lpt1",
        "com9",
        'a"b',
        "a<b",
        "a>b",
        "a|b",
        "a?b",
        "a*b",
    ],
)
def test_destino_invalido_levanta_regra_invalida(
    conn: sqlite3.Connection, destination: str
) -> None:
    assert _invalid_fields(conn, "Regra", ["pdf"], destination) == {
        "destination_folder": MSG_DESTINATION
    }


def test_todos_os_campos_invalidos_vem_juntos_em_fields(conn: sqlite3.Connection) -> None:
    fields = _invalid_fields(conn, "", [], "..")

    assert fields == {
        "name": MSG_NAME,
        "extensions": MSG_EXTENSIONS,
        "destination_folder": MSG_DESTINATION,
    }
    assert list_rules(conn) == []


def test_regra_invalida_nao_grava_nada(conn: sqlite3.Connection) -> None:
    _invalid_fields(conn, "Regra", ["a-b"], "Docs")

    assert list_rules(conn) == []


@pytest.mark.parametrize("destination", ["Trabalho/Planilhas", "Fotos\\2026", "Docs"])
def test_destino_com_varios_segmentos_e_valido_e_fica_como_informado(
    conn: sqlite3.Connection, destination: str
) -> None:
    rule = create_rule(conn, "Regra", ["xlsx"], destination)

    assert rule.destination_folder == destination
    assert list_rules(conn)[0].destination_folder == destination


def test_extensao_repetida_na_mesma_regra_e_unida(conn: sqlite3.Connection) -> None:
    rule = create_rule(conn, "Regra", ["PDF", ".pdf", "pdf"], "Docs")

    assert rule.extensions == frozenset({"pdf"})
    count = conn.execute(
        "SELECT COUNT(*) FROM rule_extensions WHERE rule_id = ?", (rule.id,)
    ).fetchone()[0]
    assert count == 1


def test_extensao_ja_usada_em_outra_regra_e_permitida(conn: sqlite3.Connection) -> None:
    first = create_rule(conn, "Documentos", ["pdf"], "Docs")

    second = create_rule(conn, "Contratos", ["pdf"], "Contratos")

    assert first.extensions == second.extensions == frozenset({"pdf"})
    assert [rule.position for rule in list_rules(conn)] == [1, 2]


def test_banco_fechado_levanta_banco_indisponivel(tmp_path: Path) -> None:
    connection = open_connection(tmp_path / "filepilot.db")
    connection.close()

    with pytest.raises(FilePilotError) as info:
        list_rules(connection)

    assert info.value.code == "BANCO_INDISPONIVEL"
