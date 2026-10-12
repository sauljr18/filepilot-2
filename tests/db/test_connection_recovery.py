import sqlite3
from pathlib import Path

import pytest

from filepilot.db import connection
from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError

NOW = "2026-10-11T12:00:00Z"

# Condicao de last_undoable (6.4); history.py ainda nao existe (filepilot-v1-7).
_UNDOABLE = (
    "SELECT id FROM organizations "
    "WHERE status IN ('concluida','interrompida') AND moved_count >= 1"
)


def _insert_organization(
    conn: sqlite3.Connection,
    status: str = "em_andamento",
    moved_count: int = 0,
    failed_count: int = 0,
    finished_at: str | None = None,
) -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, finished_at, status, "
        "moved_count, failed_count, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        ("/pasta", NOW, finished_at, status, moved_count, failed_count, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def _insert_operation(
    conn: sqlite3.Connection, organization_id: int, seq: int, status: str
) -> None:
    destination = None if status == "falha" else f"/pasta/Documentos/{seq}.pdf"
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, "
        "destination_path, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (organization_id, seq, f"/pasta/{seq}.pdf", destination, status, NOW, NOW),
    )
    conn.commit()


def _rows(conn: sqlite3.Connection) -> list[tuple[int, str, int, int, str | None]]:
    return conn.execute(
        "SELECT id, status, moved_count, failed_count, finished_at "
        "FROM organizations ORDER BY id"
    ).fetchall()


def test_organizacao_em_andamento_vira_interrompida_com_as_contagens_gravadas(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "filepilot.db"
    conn = open_connection(db_path)
    organization_id = _insert_organization(conn)
    _insert_operation(conn, organization_id, 1, "movido")
    _insert_operation(conn, organization_id, 2, "falha")
    _insert_operation(conn, organization_id, 3, "movido")
    conn.close()

    conn = open_connection(db_path)

    (row,) = conn.execute(
        "SELECT status, moved_count, failed_count, finished_at, updated_at "
        "FROM organizations"
    ).fetchall()
    assert row[:3] == ("interrompida", 2, 1)
    assert row[3] is not None and row[3].endswith("Z") and len(row[3]) == 20
    assert row[4] == row[3]
    assert conn.execute(_UNDOABLE).fetchall() == [(organization_id,)]
    conn.close()


def test_organizacao_sem_operacoes_gravadas_fica_interrompida_e_nao_desfazivel(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "filepilot.db"
    conn = open_connection(db_path)
    _insert_organization(conn)
    conn.close()

    conn = open_connection(db_path)

    ((_, status, moved, failed, finished_at),) = _rows(conn)
    assert (status, moved, failed) == ("interrompida", 0, 0)
    assert finished_at is not None
    assert conn.execute(_UNDOABLE).fetchall() == []
    conn.close()


def test_outros_status_ficam_identicos(tmp_path: Path) -> None:
    db_path = tmp_path / "filepilot.db"
    conn = open_connection(db_path)
    _insert_organization(conn, "concluida", 3, 1, "2026-10-11T12:30:00Z")
    _insert_organization(conn, "interrompida", 1, 0, "2026-10-11T12:40:00Z")
    _insert_organization(conn, "desfeita", 2, 2, "2026-10-11T12:50:00Z")
    before = _rows(conn)
    conn.close()

    conn = open_connection(db_path)

    assert _rows(conn) == before
    conn.close()


def test_banco_novo_ou_sem_em_andamento_abre_sem_alterar_linhas(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "filepilot.db"
    conn = open_connection(db_path)
    assert _rows(conn) == []
    _insert_organization(conn, "concluida", 1, 0, "2026-10-11T12:30:00Z")
    before = _rows(conn)
    updated_before = conn.execute("SELECT updated_at FROM organizations").fetchall()
    conn.close()

    conn = open_connection(db_path)

    assert _rows(conn) == before
    assert conn.execute("SELECT updated_at FROM organizations").fetchall() == (
        updated_before
    )
    conn.close()


def test_falha_na_recuperacao_levanta_banco_indisponivel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_recover(conn: sqlite3.Connection) -> None:
        raise sqlite3.OperationalError("banco indisponivel")

    monkeypatch.setattr(connection, "_recover_interrupted", fake_recover)

    with pytest.raises(FilePilotError) as raised:
        open_connection(tmp_path / "filepilot.db")

    assert raised.value.code == "BANCO_INDISPONIVEL"
