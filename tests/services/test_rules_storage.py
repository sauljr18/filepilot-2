import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.services import rules as rules_service
from filepilot.services.rules import create_rule, delete_rule, list_rules, update_rule

NOW = "2026-10-11T12:00:00Z"


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "filepilot.db")
    yield connection
    connection.close()


def _stored_extensions(conn: sqlite3.Connection, rule_id: int) -> list[str]:
    rows = conn.execute(
        "SELECT extension FROM rule_extensions WHERE rule_id = ? ORDER BY extension",
        (rule_id,),
    ).fetchall()
    return [row[0] for row in rows]


def _insert_operation_with_rule_name(conn: sqlite3.Connection, rule_name: str) -> None:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, created_at, updated_at) "
        "VALUES (?, ?, ?, ?)",
        ("/pasta", NOW, NOW, NOW),
    )
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, destination_path, "
        "rule_name, status, created_at, updated_at) VALUES (?, 1, ?, ?, ?, 'movido', ?, ?)",
        (cursor.lastrowid, "/pasta/a.pdf", "/pasta/Docs/a.pdf", rule_name, NOW, NOW),
    )
    conn.commit()


def _force_invalid_extension(monkeypatch: pytest.MonkeyPatch) -> None:
    """Faz a validacao deixar passar uma extensao que o CHECK do banco recusa."""
    monkeypatch.setattr(rules_service, "_normalize_extensions", lambda raw: ["x" * 16])


def test_cada_extensao_fica_em_uma_linha_de_rule_extensions(
    conn: sqlite3.Connection,
) -> None:
    rule = create_rule(conn, "Imagens", ["JPG", ".png", "gif"], "Fotos")

    assert _stored_extensions(conn, rule.id) == ["gif", "jpg", "png"]


def test_delete_rule_apaga_as_extensoes_junto(conn: sqlite3.Connection) -> None:
    kept = create_rule(conn, "Mantida", ["pdf"], "Docs")
    removed = create_rule(conn, "Removida", ["jpg", "png"], "Fotos")

    delete_rule(conn, removed.id)

    assert _stored_extensions(conn, removed.id) == []
    assert _stored_extensions(conn, kept.id) == ["pdf"]
    total = conn.execute("SELECT COUNT(*) FROM rule_extensions").fetchone()[0]
    assert total == 1


def test_excluir_regra_nao_altera_o_rule_name_do_historico(
    conn: sqlite3.Connection,
) -> None:
    rule = create_rule(conn, "Documentos", ["pdf"], "Docs")
    _insert_operation_with_rule_name(conn, "Documentos")

    delete_rule(conn, rule.id)

    names = conn.execute("SELECT rule_name FROM operations").fetchall()
    assert [row[0] for row in names] == ["Documentos"]


def test_renomear_regra_nao_altera_o_rule_name_do_historico(
    conn: sqlite3.Connection,
) -> None:
    rule = create_rule(conn, "Documentos", ["pdf"], "Docs")
    _insert_operation_with_rule_name(conn, "Documentos")

    update_rule(conn, rule.id, "Papeis", ["pdf"], "Docs")

    names = conn.execute("SELECT rule_name FROM operations").fetchall()
    assert [row[0] for row in names] == ["Documentos"]


def test_falha_nas_extensoes_desfaz_a_gravacao_da_regra(
    conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    _force_invalid_extension(monkeypatch)

    with pytest.raises(FilePilotError) as info:
        create_rule(conn, "Regra", ["pdf"], "Docs")

    assert info.value.code == "BANCO_INDISPONIVEL"
    assert conn.execute("SELECT COUNT(*) FROM rules").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM rule_extensions").fetchone()[0] == 0
    assert not conn.in_transaction


def test_falha_nas_extensoes_do_update_mantem_a_regra_como_estava(
    conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    rule = create_rule(conn, "Original", ["pdf", "doc"], "Docs")
    _force_invalid_extension(monkeypatch)

    with pytest.raises(FilePilotError) as info:
        update_rule(conn, rule.id, "Alterada", ["pdf"], "Outra")

    assert info.value.code == "BANCO_INDISPONIVEL"
    assert list_rules(conn) == [rule]
    assert _stored_extensions(conn, rule.id) == ["doc", "pdf"]
    assert not conn.in_transaction


def test_conexao_continua_utilizavel_depois_da_falha(
    conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    with monkeypatch.context() as patch:
        patch.setattr(rules_service, "_normalize_extensions", lambda raw: ["x" * 16])
        with pytest.raises(FilePilotError):
            create_rule(conn, "Falha", ["pdf"], "Docs")

    rule = create_rule(conn, "Ok", ["pdf"], "Docs")

    assert rule.position == 1
    assert list_rules(conn) == [rule]


def test_o_servico_usa_consultas_parametrizadas(conn: sqlite3.Connection) -> None:
    name = "x'); DROP TABLE rules; --"

    rule = create_rule(conn, name, ["pdf"], "Docs")

    assert list_rules(conn) == [rule]
    assert rule.name == name
