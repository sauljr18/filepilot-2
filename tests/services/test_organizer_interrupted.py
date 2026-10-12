import sqlite3
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import OrganizationResult, Plan, ScannedFile
from filepilot.services import organizer
from filepilot.services.organizer import OPERATION_LOCK, _interrupt_organization, organize
from filepilot.services.planner import build_plan

# Condicao de last_undoable (6.4); history.py ainda nao existe (filepilot-v1-7).
_UNDOABLE = (
    "SELECT id FROM organizations "
    "WHERE status IN ('concluida','interrompida') AND moved_count >= 1"
)


def _scanned(folder: Path, name: str) -> ScannedFile:
    path = folder / name
    path.write_bytes(name.encode())
    extension = name.rpartition(".")[2].lower()
    return ScannedFile(path=path, name=name, extension=extension, size_bytes=1)


def _plan(folder: Path, names: list[str]) -> Plan:
    return build_plan(folder, [_scanned(folder, name) for name in names], [])


def _fail_record_on(
    monkeypatch: pytest.MonkeyPatch, conn: sqlite3.Connection, failing_seq: int
) -> None:
    real_record = organizer._record_operation

    def fake_record(
        conn_: sqlite3.Connection,
        organization_id: int,
        operation: organizer.PlannedOperation,
        destination: Path | None,
        message: str | None,
    ) -> None:
        if operation.seq == failing_seq:
            # Deixa uma transacao aberta, como uma falha no meio da gravacao.
            conn_.execute(
                "INSERT INTO operations (organization_id, seq, source_path, "
                "status, created_at, updated_at) VALUES (?, ?, 'x', 'falha', 'x', 'x')",
                (organization_id, operation.seq),
            )
            raise sqlite3.OperationalError("disco cheio")
        real_record(conn_, organization_id, operation, destination, message)

    monkeypatch.setattr(organizer, "_record_operation", fake_record)


def _organization_row(conn: sqlite3.Connection) -> tuple[str, int, int, str | None]:
    row = conn.execute(
        "SELECT status, moved_count, failed_count, finished_at FROM organizations"
    ).fetchone()
    assert isinstance(row, tuple)
    return row


def test_falha_na_segunda_gravacao_deixa_a_organizacao_interrompida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf", "c.pdf"])
    conn = open_connection(tmp_path / "historico.db")
    _fail_record_on(monkeypatch, conn, failing_seq=2)

    with pytest.raises(FilePilotError) as raised:
        organize(plan, conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    status, moved, failed, finished_at = _organization_row(conn)
    assert (status, moved, failed) == ("interrompida", 1, 0)
    assert finished_at is not None
    assert conn.in_transaction is False
    assert (folder / "b.pdf").is_file()
    assert (folder / "c.pdf").is_file()
    assert (folder / "Documentos" / "a.pdf").is_file()
    (operations,) = conn.execute("SELECT COUNT(*) FROM operations").fetchone()
    assert operations == 1
    assert conn.execute(_UNDOABLE).fetchall() != []


def test_falha_na_primeira_gravacao_nao_e_desfazivel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf"])
    conn = open_connection(tmp_path / "historico.db")
    _fail_record_on(monkeypatch, conn, failing_seq=1)

    with pytest.raises(FilePilotError):
        organize(plan, conn)

    status, moved, failed, finished_at = _organization_row(conn)
    assert (status, moved, failed) == ("interrompida", 0, 0)
    assert finished_at is not None
    assert (folder / "a.pdf").is_file()
    assert (folder / "b.pdf").is_file()
    assert conn.execute(_UNDOABLE).fetchall() == []


def test_falha_no_update_de_fechamento_deixa_as_contagens_finais(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf", "c.pdf"])
    conn = open_connection(tmp_path / "historico.db")
    conn.execute(
        "CREATE TRIGGER falha_no_fechamento BEFORE UPDATE ON organizations "
        "WHEN NEW.status = 'concluida' BEGIN SELECT RAISE(ABORT, 'falha'); END"
    )
    conn.commit()

    with pytest.raises(FilePilotError) as raised:
        organize(plan, conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    status, moved, failed, finished_at = _organization_row(conn)
    assert (status, moved, failed) == ("interrompida", 3, 0)
    assert finished_at is not None
    assert conn.in_transaction is False
    assert conn.execute(_UNDOABLE).fetchall() != []


def test_helper_nao_altera_linha_que_nao_esta_em_andamento(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "historico.db")
    conn.execute(
        "INSERT INTO organizations (folder_path, started_at, finished_at, status, "
        "moved_count, failed_count, created_at, updated_at) "
        "VALUES ('/p', 't', 'fim', 'concluida', 2, 1, 't', 't')"
    )
    conn.commit()
    result = OrganizationResult(organization_id=1, moved_count=9, failed_count=9)

    _interrupt_organization(conn, 1, result)

    assert _organization_row(conn) == ("concluida", 2, 1, "fim")


def test_banco_inteiramente_indisponivel_nao_propaga_erro_do_helper(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf"])
    conn = open_connection(tmp_path / "historico.db")

    def fake_record(*_args: object) -> None:
        conn.close()
        raise sqlite3.OperationalError("banco indisponivel")

    monkeypatch.setattr(organizer, "_record_operation", fake_record)

    with pytest.raises(FilePilotError) as raised:
        organize(plan, conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert (folder / "a.pdf").is_file()
    assert (folder / "b.pdf").is_file()
    assert OPERATION_LOCK.acquire(blocking=False) is True
    OPERATION_LOCK.release()


def test_falha_ao_abrir_a_organizacao_nao_deixa_transacao_aberta(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf"])
    conn = open_connection(tmp_path / "historico.db")
    conn.execute("DROP TABLE operations")
    conn.execute("DROP TABLE organizations")
    conn.commit()

    with pytest.raises(FilePilotError) as raised:
        organize(plan, conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert conn.in_transaction is False
    assert (folder / "a.pdf").is_file()


@pytest.mark.parametrize("failing_seq", [1, 2])
def test_trava_e_liberada_depois_de_qualquer_falha(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failing_seq: int
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf"])
    conn = open_connection(tmp_path / "historico.db")
    _fail_record_on(monkeypatch, conn, failing_seq=failing_seq)

    with pytest.raises(FilePilotError):
        organize(plan, conn)

    assert OPERATION_LOCK.acquire(blocking=False) is True
    OPERATION_LOCK.release()
