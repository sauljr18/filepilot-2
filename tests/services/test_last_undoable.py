import sqlite3
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.services.history import last_undoable

NOW = "2026-10-11T12:00:00Z"


def _insert_organization(
    conn: sqlite3.Connection,
    started_at: str,
    status: str = "concluida",
    moved_count: int = 1,
) -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, "
        "moved_count, failed_count, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 0, ?, ?)",
        ("/pasta", started_at, status, moved_count, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    return open_connection(tmp_path / "historico.db")


def test_sem_organizacoes_devolve_none(conn: sqlite3.Connection) -> None:
    assert last_undoable(conn) is None


@pytest.mark.parametrize("status", ["concluida", "interrompida"])
def test_devolve_a_linha_de_concluida_ou_interrompida_com_movidos(
    conn: sqlite3.Connection, status: str
) -> None:
    org_id = _insert_organization(
        conn, "2026-10-11T09:00:00Z", status=status, moved_count=2
    )

    row = last_undoable(conn)

    assert row is not None
    assert (row.id, row.status, row.moved_count) == (org_id, status, 2)


def test_ultima_com_moved_count_1_ainda_e_desfazivel(
    conn: sqlite3.Connection,
) -> None:
    org_id = _insert_organization(conn, "2026-10-11T09:00:00Z", moved_count=1)

    row = last_undoable(conn)

    assert row is not None and row.id == org_id


def test_ultima_com_moved_count_zero_devolve_none(conn: sqlite3.Connection) -> None:
    _insert_organization(conn, "2026-10-11T09:00:00Z", moved_count=0)

    assert last_undoable(conn) is None


def test_ultima_desfeita_devolve_none(conn: sqlite3.Connection) -> None:
    _insert_organization(conn, "2026-10-11T09:00:00Z", status="desfeita")

    assert last_undoable(conn) is None


def test_ultima_em_andamento_devolve_none(conn: sqlite3.Connection) -> None:
    _insert_organization(conn, "2026-10-11T09:00:00Z", status="em_andamento")

    assert last_undoable(conn) is None


def test_nao_ha_retrocesso_quando_a_ultima_nao_e_desfazivel(
    conn: sqlite3.Connection,
) -> None:
    _insert_organization(conn, "2026-10-10T09:00:00Z", moved_count=5)
    _insert_organization(conn, "2026-10-11T09:00:00Z", moved_count=0)

    assert last_undoable(conn) is None


def test_nao_ha_retrocesso_quando_a_ultima_esta_desfeita(
    conn: sqlite3.Connection,
) -> None:
    _insert_organization(conn, "2026-10-10T09:00:00Z", moved_count=5)
    _insert_organization(conn, "2026-10-11T09:00:00Z", status="desfeita")

    assert last_undoable(conn) is None


def test_ultima_e_a_de_maior_started_at_mesmo_inserida_antes(
    conn: sqlite3.Connection,
) -> None:
    recente = _insert_organization(conn, "2026-10-12T09:00:00Z", moved_count=2)
    _insert_organization(conn, "2026-10-10T09:00:00Z", moved_count=7)

    row = last_undoable(conn)

    assert row is not None and row.id == recente


def test_empate_de_started_at_desempata_por_id(conn: sqlite3.Connection) -> None:
    _insert_organization(conn, "2026-10-11T09:00:00Z", moved_count=1)
    maior_id = _insert_organization(
        conn, "2026-10-11T09:00:00Z", status="desfeita", moved_count=1
    )
    # A de maior id e a ultima; ela esta desfeita, entao nao ha o que desfazer.
    assert maior_id > 1
    assert last_undoable(conn) is None


def test_organizacao_em_andamento_vira_interrompida_ao_abrir_o_banco(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "historico.db"
    conn = open_connection(db_path)
    org_id = _insert_organization(
        conn, "2026-10-11T09:00:00Z", status="em_andamento", moved_count=0
    )
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, "
        "destination_path, status, created_at, updated_at) "
        "VALUES (?, 1, '/pasta/a.pdf', '/pasta/Documentos/a.pdf', 'movido', ?, ?)",
        (org_id, NOW, NOW),
    )
    conn.commit()
    assert last_undoable(conn) is None
    conn.close()

    reopened = open_connection(db_path)

    status = reopened.execute(
        "SELECT status FROM organizations WHERE id = ?", (org_id,)
    ).fetchone()[0]
    assert status == "interrompida"
    row = last_undoable(reopened)
    assert row is not None and (row.id, row.status, row.moved_count) == (
        org_id,
        "interrompida",
        1,
    )


def test_banco_fechado_levanta_banco_indisponivel(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "historico.db")
    conn.close()

    with pytest.raises(FilePilotError) as raised:
        last_undoable(conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
