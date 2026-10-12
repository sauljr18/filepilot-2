import sqlite3
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Plan, ScannedFile
from filepilot.services import undo
from filepilot.services.history import last_undoable
from filepilot.services.organizer import OPERATION_LOCK, organize
from filepilot.services.planner import build_plan
from filepilot.services.undo import undo_last

_real_record_status = undo._record_status


def _scanned(folder: Path, name: str) -> ScannedFile:
    path = folder / name
    path.write_bytes(name.encode())
    extension = name.rpartition(".")[2].lower()
    return ScannedFile(path=path, name=name, extension=extension, size_bytes=1)


def _plan(folder: Path, names: list[str]) -> Plan:
    return build_plan(folder, [_scanned(folder, name) for name in names], [])


def _statuses(conn: sqlite3.Connection, organization_id: int) -> dict[str, str]:
    rows = conn.execute(
        "SELECT source_path, status FROM operations WHERE organization_id = ?",
        (organization_id,),
    ).fetchall()
    return {Path(row[0]).name: row[1] for row in rows}


def _update_without_commit(
    conn: sqlite3.Connection, operation_id: int, status: str, message: str | None
) -> None:
    conn.execute(
        "UPDATE operations SET status = ?, error_message = ? WHERE id = ?",
        (status, message, operation_id),
    )


def _fail_after_update(
    conn: sqlite3.Connection, operation_id: int, status: str, message: str | None
) -> None:
    _update_without_commit(conn, operation_id, status, message)
    raise sqlite3.OperationalError("disco cheio")


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    return open_connection(tmp_path / "historico.db")


@pytest.fixture
def folder(tmp_path: Path) -> Path:
    chosen = tmp_path / "escolhida"
    chosen.mkdir()
    return chosen


def test_falha_com_update_sem_commit_nao_deixa_transacao_aberta(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["a.pdf"]), conn)
    monkeypatch.setattr(undo, "_record_status", _fail_after_update)

    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert conn.in_transaction is False
    assert (folder / "Documentos" / "a.pdf").is_file()
    assert not (folder / "a.pdf").exists()
    assert _statuses(conn, organized.organization_id)["a.pdf"] == "movido"
    assert OPERATION_LOCK.acquire(blocking=False)
    OPERATION_LOCK.release()


def test_segundo_desfazer_restaura_o_arquivo_da_falha(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["a.pdf"]), conn)
    monkeypatch.setattr(undo, "_record_status", _fail_after_update)
    with pytest.raises(FilePilotError):
        undo_last(conn)
    monkeypatch.undo()

    result = undo_last(conn)

    assert result.restored_count == 1
    assert (folder / "a.pdf").is_file()
    assert not (folder / "Documentos" / "a.pdf").exists()
    assert _statuses(conn, organized.organization_id)["a.pdf"] == "restaurado"
    assert last_undoable(conn) is None


def test_falha_so_na_segunda_gravacao_restaura_os_tres_no_segundo_desfazer(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["a.pdf", "b.png", "c.mp4"]), conn)
    calls: list[int] = []

    def fail_on_second(
        db: sqlite3.Connection, operation_id: int, status: str, message: str | None
    ) -> None:
        calls.append(operation_id)
        if len(calls) == 2:
            _fail_after_update(db, operation_id, status, message)
        _real_record_status(db, operation_id, status, message)

    monkeypatch.setattr(undo, "_record_status", fail_on_second)
    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)
    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert conn.in_transaction is False
    monkeypatch.undo()

    undo_last(conn)

    for name in ("a.pdf", "b.png", "c.mp4"):
        assert (folder / name).is_file()
    assert set(_statuses(conn, organized.organization_id).values()) == {"restaurado"}
    assert last_undoable(conn) is None


def test_falha_no_update_final_da_organizacao_permite_novo_desfazer(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organize(_plan(folder, ["a.pdf", "b.png"]), conn)
    conn.execute(
        "CREATE TRIGGER bloqueia_desfeita BEFORE UPDATE ON organizations "
        "WHEN NEW.status = 'desfeita' BEGIN SELECT RAISE(ABORT, 'falha'); END"
    )

    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert conn.in_transaction is False
    assert (folder / "a.pdf").is_file()
    assert (folder / "b.png").is_file()
    conn.execute("DROP TRIGGER bloqueia_desfeita")

    result = undo_last(conn)

    assert result.restored_count == 0
    assert last_undoable(conn) is None


def test_conexao_fechada_na_falha_devolve_o_arquivo_sem_trocar_o_erro(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organize(_plan(folder, ["a.pdf"]), conn)

    def close_and_fail(
        db: sqlite3.Connection, operation_id: int, status: str, message: str | None
    ) -> None:
        db.close()
        raise sqlite3.OperationalError("banco morto")

    monkeypatch.setattr(undo, "_record_status", close_and_fail)

    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert (folder / "Documentos" / "a.pdf").is_file()
    assert not (folder / "a.pdf").exists()
