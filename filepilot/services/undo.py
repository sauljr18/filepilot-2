"""Desfazer a ultima organizacao (SPEC 6.5).

`undo_last` devolve os arquivos ao caminho e ao nome originais, nunca
sobrescreve nada e so remove pastas vazias, com `Path.rmdir`.
"""

import contextlib
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from filepilot.domain.errors import FilePilotError
from filepilot.services.history import last_undoable
from filepilot.services.organizer import OPERATION_LOCK

_MESSAGES = {
    "NADA_PARA_DESFAZER": "Não há organização para desfazer.",
    "ORGANIZACAO_EM_ANDAMENTO": "Aguarde a organização terminar.",
    "BANCO_INDISPONIVEL": "Não foi possível acessar o histórico do FilePilot.",
}
_DESTINATION_MISSING = "arquivo não está mais no destino"
_SOURCE_OCCUPIED = "caminho original ocupado"
_SOURCE_OUTSIDE = "caminho original fora da pasta escolhida"


@dataclass
class UndoResult:
    """Resultado do desfazer (6.5)."""

    organization_id: int
    restored_count: int
    not_restored: list[tuple[str, str]] = field(default_factory=list)
    removed_folders: list[str] = field(default_factory=list)


def _error(code: str) -> FilePilotError:
    return FilePilotError(code, _MESSAGES[code])


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _is_inside(folder: Path, path: Path) -> bool:
    return path.resolve().is_relative_to(folder.resolve())


def _restore_file(folder: Path, source: Path, destination: Path) -> str | None:
    """Devolve o arquivo ao lugar; `None` se restaurou, senao o motivo (6.5)."""
    # A guarda nao tem parametro para desliga-la (NFR-001).
    if not _is_inside(folder, source):
        return _SOURCE_OUTSIDE
    if not os.path.lexists(destination):
        return _DESTINATION_MISSING
    if os.path.lexists(source):
        return _SOURCE_OCCUPIED
    try:
        os.rename(destination, source)
    except OSError as exc:
        return str(exc)
    return None


def _record_status(
    conn: sqlite3.Connection,
    operation_id: int,
    status: str,
    message: str | None,
) -> None:
    conn.execute(
        "UPDATE operations SET status = ?, error_message = ?, updated_at = ? "
        "WHERE id = ?",
        (status, message, _utc_now(), operation_id),
    )
    conn.commit()


def _remove_empty_folders(folder: Path, destinations: list[Path]) -> list[str]:
    """Remove as pastas de destino vazias, subindo ate a pasta escolhida (6.5).

    `rmdir` so apaga pasta vazia: nenhum arquivo pode se perder aqui. A pasta
    escolhida nunca e removida.
    """
    removed: list[str] = []
    seen: set[Path] = set()
    for destination in destinations:
        current = destination.parent
        if current in seen:
            continue
        seen.add(current)
        while current.resolve() != folder.resolve() and _is_inside(folder, current):
            try:
                current.rmdir()
            except OSError:
                break
            removed.append(str(current))
            current = current.parent
    return removed


def _run(conn: sqlite3.Connection, organization_id: int, folder: Path) -> UndoResult:
    rows = conn.execute(
        "SELECT id, source_path, destination_path FROM operations "
        "WHERE organization_id = ? AND status = 'movido' ORDER BY seq DESC",
        (organization_id,),
    ).fetchall()
    result = UndoResult(organization_id=organization_id, restored_count=0)
    destinations: list[Path] = []
    for operation_id, source_text, destination_text in rows:
        source = Path(source_text)
        destination = Path(destination_text)
        destinations.append(destination)
        reason = _restore_file(folder, source, destination)
        status = "restaurado" if reason is None else "nao_restaurado"
        try:
            _record_status(conn, operation_id, status, reason)
        except sqlite3.Error as exc:
            if reason is None:
                # Sem registro o arquivo ficaria "movido" fora do destino.
                with contextlib.suppress(OSError):
                    os.rename(source, destination)
            raise _error("BANCO_INDISPONIVEL") from exc
        if reason is None:
            result.restored_count += 1
        else:
            result.not_restored.append((source_text, reason))
    result.removed_folders = _remove_empty_folders(folder, destinations)
    now = _utc_now()
    conn.execute(
        "UPDATE organizations SET status = 'desfeita', undone_at = ?, "
        "updated_at = ? WHERE id = ?",
        (now, now, organization_id),
    )
    conn.commit()
    return result


def undo_last(conn: sqlite3.Connection) -> UndoResult:
    """Desfaz a ultima organizacao desfazivel (6.5).

    Levanta `ORGANIZACAO_EM_ANDAMENTO` durante uma organizacao,
    `NADA_PARA_DESFAZER` sem organizacao desfazivel e `BANCO_INDISPONIVEL`
    em falha do banco.
    """
    if not OPERATION_LOCK.acquire(blocking=False):
        raise _error("ORGANIZACAO_EM_ANDAMENTO")
    try:
        last = last_undoable(conn)
        if last is None:
            raise _error("NADA_PARA_DESFAZER")
        try:
            return _run(conn, last.id, Path(last.folder_path))
        except sqlite3.Error as exc:
            raise _error("BANCO_INDISPONIVEL") from exc
    finally:
        OPERATION_LOCK.release()
