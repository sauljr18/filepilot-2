import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Rule
from filepilot.services.rules import (
    create_rule,
    delete_rule,
    list_rules,
    move_rule,
    update_rule,
)

MSG_POSITION = "Posição inválida."


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "filepilot.db")
    yield connection
    connection.close()


def _four_rules(conn: sqlite3.Connection) -> list[Rule]:
    return [
        create_rule(conn, name, [ext], name)
        for name, ext in (("A", "a"), ("B", "b"), ("C", "c"), ("D", "d"))
    ]


def _names(conn: sqlite3.Connection) -> list[str]:
    return [rule.name for rule in list_rules(conn)]


def _positions(conn: sqlite3.Connection) -> list[int]:
    return [rule.position for rule in list_rules(conn)]


def test_update_rule_altera_nome_extensoes_e_destino_e_mantem_a_position(
    conn: sqlite3.Connection,
) -> None:
    rules = _four_rules(conn)

    updated = update_rule(conn, rules[1].id, " Novo ", ["PDF", ".docx"], "Docs/Novo")

    assert updated == Rule(
        id=rules[1].id,
        name="Novo",
        destination_folder="Docs/Novo",
        position=2,
        extensions=frozenset({"pdf", "docx"}),
    )
    assert list_rules(conn)[1] == updated


def test_update_rule_troca_as_extensoes_antigas(conn: sqlite3.Connection) -> None:
    rule = create_rule(conn, "Regra", ["jpg", "png"], "Fotos")

    update_rule(conn, rule.id, "Regra", ["gif"], "Fotos")

    stored = conn.execute(
        "SELECT extension FROM rule_extensions WHERE rule_id = ?", (rule.id,)
    ).fetchall()
    assert [row[0] for row in stored] == ["gif"]


def test_update_rule_com_id_inexistente_levanta_regra_nao_encontrada(
    conn: sqlite3.Connection,
) -> None:
    _four_rules(conn)

    with pytest.raises(FilePilotError) as info:
        update_rule(conn, 999, "Regra", ["pdf"], "Docs")

    assert info.value.code == "REGRA_NAO_ENCONTRADA"
    assert _names(conn) == ["A", "B", "C", "D"]


def test_update_rule_invalida_nao_altera_a_regra(conn: sqlite3.Connection) -> None:
    rule = create_rule(conn, "Regra", ["pdf"], "Docs")

    with pytest.raises(FilePilotError) as info:
        update_rule(conn, rule.id, "", ["pdf"], "Docs")

    assert info.value.code == "REGRA_INVALIDA"
    assert info.value.fields == {"name": "Informe um nome de até 60 caracteres."}
    assert list_rules(conn) == [rule]


def test_delete_rule_em_quatro_regras_mantem_posicoes_de_1_a_3(
    conn: sqlite3.Connection,
) -> None:
    rules = _four_rules(conn)

    delete_rule(conn, rules[1].id)

    assert _names(conn) == ["A", "C", "D"]
    assert _positions(conn) == [1, 2, 3]


@pytest.mark.parametrize("index", [0, 3])
def test_delete_rule_dos_extremos_mantem_posicoes_sem_lacuna(
    conn: sqlite3.Connection, index: int
) -> None:
    rules = _four_rules(conn)

    delete_rule(conn, rules[index].id)

    assert _positions(conn) == [1, 2, 3]


def test_delete_rule_da_unica_regra_deixa_a_lista_vazia(conn: sqlite3.Connection) -> None:
    rule = create_rule(conn, "Regra", ["pdf"], "Docs")

    delete_rule(conn, rule.id)

    assert list_rules(conn) == []


def test_delete_rule_com_id_inexistente_levanta_regra_nao_encontrada(
    conn: sqlite3.Connection,
) -> None:
    _four_rules(conn)

    with pytest.raises(FilePilotError) as info:
        delete_rule(conn, 999)

    assert info.value.code == "REGRA_NAO_ENCONTRADA"
    assert _positions(conn) == [1, 2, 3, 4]


def test_proxima_regra_criada_apos_exclusao_entra_na_ultima_posicao(
    conn: sqlite3.Connection,
) -> None:
    rules = _four_rules(conn)
    delete_rule(conn, rules[0].id)

    created = create_rule(conn, "E", ["e"], "E")

    assert created.position == 4
    assert _names(conn) == ["B", "C", "D", "E"]


@pytest.mark.parametrize(
    ("index", "new_position", "expected"),
    [
        (0, 4, ["B", "C", "D", "A"]),
        (3, 1, ["D", "A", "B", "C"]),
        (1, 3, ["A", "C", "B", "D"]),
        (2, 1, ["C", "A", "B", "D"]),
        (1, 2, ["A", "B", "C", "D"]),
    ],
)
def test_move_rule_em_quatro_regras_reordena_sem_lacuna(
    conn: sqlite3.Connection, index: int, new_position: int, expected: list[str]
) -> None:
    rules = _four_rules(conn)

    result = move_rule(conn, rules[index].id, new_position)

    assert [rule.name for rule in result] == expected
    assert [rule.position for rule in result] == [1, 2, 3, 4]
    assert result == list_rules(conn)


@pytest.mark.parametrize("new_position", [0, 5, -1])
def test_move_rule_com_posicao_fora_do_intervalo_levanta_regra_invalida(
    conn: sqlite3.Connection, new_position: int
) -> None:
    rules = _four_rules(conn)

    with pytest.raises(FilePilotError) as info:
        move_rule(conn, rules[0].id, new_position)

    assert info.value.code == "REGRA_INVALIDA"
    assert info.value.fields == {"position": MSG_POSITION}
    assert _names(conn) == ["A", "B", "C", "D"]
    assert _positions(conn) == [1, 2, 3, 4]


def test_move_rule_com_id_inexistente_levanta_regra_nao_encontrada(
    conn: sqlite3.Connection,
) -> None:
    _four_rules(conn)

    with pytest.raises(FilePilotError) as info:
        move_rule(conn, 999, 1)

    assert info.value.code == "REGRA_NAO_ENCONTRADA"


def test_move_rule_preserva_extensoes_e_destino(conn: sqlite3.Connection) -> None:
    rules = _four_rules(conn)

    result = move_rule(conn, rules[3].id, 1)

    moved = result[0]
    assert (moved.name, moved.destination_folder, moved.extensions) == (
        "D",
        "D",
        frozenset({"d"}),
    )
