import errno
import os
import sqlite3
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Plan, ScannedFile
from filepilot.services.history import last_undoable
from filepilot.services.organizer import OPERATION_LOCK, organize
from filepilot.services.planner import build_plan
from filepilot.services.undo import undo_last

INVALID_MESSAGE = "A pasta escolhida não existe ou não é uma pasta."
NOW = "2026-10-11T12:00:00Z"

_original_resolve = Path.resolve


def _fail_resolve_for(target: Path, error: Exception) -> Callable[..., Path]:
    def fake_resolve(self: Path, strict: bool = False) -> Path:
        if self == target:
            raise error
        return _original_resolve(self, strict=strict)

    return fake_resolve


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        if sys.platform == "win32" and os.environ.get("GITHUB_ACTIONS") == "true":
            pytest.fail("o sistema recusou criar o link simbolico")
        pytest.skip("o sistema recusou criar o link simbolico")


def _scanned(folder: Path, name: str, content: bytes | None = None) -> ScannedFile:
    path = folder / name
    path.write_bytes(name.encode() if content is None else content)
    extension = name.rpartition(".")[2].lower()
    return ScannedFile(path=path, name=name, extension=extension, size_bytes=1)


def _plan(folder: Path, names: list[str]) -> Plan:
    return build_plan(folder, [_scanned(folder, name) for name in names], [])


def _tree(folder: Path) -> list[tuple[str, bool]]:
    return sorted(
        (str(path.relative_to(folder)), path.is_symlink()) for path in folder.rglob("*")
    )


def _statuses(conn: sqlite3.Connection, organization_id: int) -> dict[str, tuple[str, str | None]]:
    rows = conn.execute(
        "SELECT source_path, status, error_message FROM operations "
        "WHERE organization_id = ?",
        (organization_id,),
    ).fetchall()
    return {Path(row[0]).name: (row[1], row[2]) for row in rows}


def _source_of(conn: sqlite3.Connection, organization_id: int, seq: int) -> Path:
    row = conn.execute(
        "SELECT source_path FROM operations WHERE organization_id = ? AND seq = ?",
        (organization_id, seq),
    ).fetchone()
    return Path(row[0])


def _lock_is_free() -> bool:
    acquired = OPERATION_LOCK.acquire(blocking=False)
    if acquired:
        OPERATION_LOCK.release()
    return acquired


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    return open_connection(tmp_path / "historico.db")


@pytest.fixture
def folder(tmp_path: Path) -> Path:
    chosen = tmp_path / "escolhida"
    chosen.mkdir()
    return chosen


def test_laco_no_caminho_original_levantado_como_runtime_error_vira_pasta_invalida(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["fatura.pdf"]), conn)
    source = _source_of(conn, organized.organization_id, 1)
    monkeypatch.setattr(
        Path, "resolve", _fail_resolve_for(source, RuntimeError("Symlink loop"))
    )

    with pytest.raises(FilePilotError) as excinfo:
        undo_last(conn)

    assert excinfo.value.code == "PASTA_INVALIDA"
    assert excinfo.value.message == INVALID_MESSAGE
    assert "Symlink loop" not in excinfo.value.message
    assert isinstance(excinfo.value.__cause__, RuntimeError)
    assert _statuses(conn, organized.organization_id)["fatura.pdf"][0] == "movido"
    assert (folder / "Documentos" / "fatura.pdf").is_file()
    assert not source.exists()
    assert _lock_is_free()


def test_laco_levantado_como_eloop_vira_pasta_invalida(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["fatura.pdf"]), conn)
    source = _source_of(conn, organized.organization_id, 1)
    error = OSError(errno.ELOOP, "Too many levels of symbolic links")
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(source, error))

    with pytest.raises(FilePilotError) as excinfo:
        undo_last(conn)

    assert excinfo.value.code == "PASTA_INVALIDA"
    assert excinfo.value.message == INVALID_MESSAGE
    assert excinfo.value.__cause__ is error
    assert _statuses(conn, organized.organization_id)["fatura.pdf"][0] == "movido"
    assert _lock_is_free()


def test_acesso_negado_na_resolucao_continua_oserror(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["fatura.pdf"]), conn)
    source = _source_of(conn, organized.organization_id, 1)
    error = OSError(errno.EACCES, "Permission denied")
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(source, error))

    with pytest.raises(OSError) as excinfo:
        undo_last(conn)

    assert not isinstance(excinfo.value, FilePilotError)
    assert excinfo.value is error
    assert _statuses(conn, organized.organization_id)["fatura.pdf"][0] == "movido"
    assert _lock_is_free()


def test_laco_real_na_pasta_escolhida_deixa_a_arvore_intacta(
    tmp_path: Path, conn: sqlite3.Connection
) -> None:
    loop = tmp_path / "laco"
    _symlink(loop, loop)
    destination_folder = tmp_path / "destino"
    destination_folder.mkdir()
    destination = destination_folder / "a.pdf"
    destination.write_bytes(b"a.pdf")
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, moved_count, "
        "failed_count, created_at, updated_at) VALUES (?, ?, 'concluida', 1, 0, ?, ?)",
        (str(loop), NOW, NOW, NOW),
    )
    organization_id = cursor.lastrowid
    assert organization_id is not None
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, destination_path, "
        "status, created_at, updated_at) VALUES (?, 1, ?, ?, 'movido', ?, ?)",
        (organization_id, str(loop / "a.pdf"), str(destination), NOW, NOW),
    )
    conn.commit()
    before = _tree(tmp_path)

    with pytest.raises(FilePilotError) as excinfo:
        undo_last(conn)

    assert excinfo.value.code == "PASTA_INVALIDA"
    assert excinfo.value.message == INVALID_MESSAGE
    assert _tree(tmp_path) == before
    assert destination.read_bytes() == b"a.pdf"
    assert _statuses(conn, organization_id)["a.pdf"][0] == "movido"
    assert _lock_is_free()


def test_falha_no_meio_preserva_o_restaurado_e_o_segundo_desfazer_conclui(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["fatura.pdf", "foto.png"]), conn)
    organization_id = organized.organization_id
    first = _source_of(conn, organization_id, 1)
    second = _source_of(conn, organization_id, 2)
    monkeypatch.setattr(
        Path, "resolve", _fail_resolve_for(first, RuntimeError("Symlink loop"))
    )

    with pytest.raises(FilePilotError) as excinfo:
        undo_last(conn)

    assert excinfo.value.code == "PASTA_INVALIDA"
    statuses = _statuses(conn, organization_id)
    assert statuses[second.name][0] == "restaurado"
    assert statuses[first.name][0] == "movido"
    assert second.is_file()
    assert not first.exists()
    assert last_undoable(conn) is not None
    assert conn.in_transaction is False
    assert _lock_is_free()

    monkeypatch.undo()
    result = undo_last(conn)

    assert result.restored_count == 1
    assert first.is_file()
    assert second.is_file()
    assert last_undoable(conn) is None


def test_laco_so_na_limpeza_nao_levanta_erro_e_fecha_a_organizacao(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["fatura.pdf", "nota.pdf"]), conn)
    assert (folder / "Documentos").is_dir()
    monkeypatch.setattr(
        Path,
        "resolve",
        _fail_resolve_for(folder / "Documentos", RuntimeError("Symlink loop")),
    )

    result = undo_last(conn)

    assert result.restored_count == 2
    assert result.removed_folders == []
    assert (folder / "Documentos").is_dir()
    assert (folder / "fatura.pdf").is_file()
    assert last_undoable(conn) is None
    status = conn.execute(
        "SELECT status FROM organizations WHERE id = ?", (organized.organization_id,)
    ).fetchone()[0]
    assert status == "desfeita"
    assert _lock_is_free()
