"""Execucao da organizacao com historico por arquivo (SPEC 6.3 e 6.7).

`organize` move os arquivos do plano com `os.rename`, grava cada operacao no
banco com `commit` imediato e nunca sobrescreve nem apaga arquivo. O plano
vem pronto de `build_plan`; aqui so se executa.
"""

import contextlib
import os
import sqlite3
import threading
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import OrganizationResult, Plan, PlannedOperation

# Decisao explicita (filepilot-v1-4): o sufixo ` (n)` e a guarda de pasta sao os
# do planner; importar os helpers evita duplicar a logica.
from filepilot.services.destination_checks import (
    OTHER,
    OUTSIDE,
    check_destination,
    failure_text,
)
from filepilot.services.planner import _existing_names, _free_name, _inside

OPERATION_LOCK = threading.Lock()

_MESSAGES = {
    "ORGANIZACAO_EM_ANDAMENTO": "Aguarde a organização terminar.",
    "BANCO_INDISPONIVEL": "Não foi possível acessar o histórico do FilePilot.",
    "ERRO_INTERNO": "Ocorreu um erro inesperado. Tente de novo.",
}


def _error(code: str) -> FilePilotError:
    return FilePilotError(code, _MESSAGES[code])


def internal_error(exc: BaseException) -> FilePilotError:
    """Erro de contrato para excecao fora do tratamento por arquivo (6.7).

    `FilePilotError` ja e de contrato e volta como esta; o resto vira
    `ERRO_INTERNO`, sem o texto bruto da excecao.
    """
    if isinstance(exc, FilePilotError):
        return exc
    return _error("ERRO_INTERNO")


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def simulate(plan: Plan) -> Plan:
    """Devolve o proprio plano; nao altera disco nem banco (6.3)."""
    return plan


def _move_file(
    folder: Path, operation: PlannedOperation
) -> tuple[Path | None, str | None]:
    """Move um arquivo; devolve o destino final ou o texto da falha (6.3 e 6.7)."""
    source = operation.source_path
    destination = operation.destination_path
    failure = check_destination(folder, destination)
    if failure is not None:
        return None, failure
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return None, failure_text(exc, creating=True)
    while True:
        try:
            # No Windows o os.rename ja recusa destino existente; no resto ele
            # sobrescreveria em silencio, entao a recusa e feita aqui tambem.
            if os.path.lexists(destination):
                raise FileExistsError(str(destination))
            os.rename(source, destination)
            return destination, None
        except FileExistsError:
            free_name = _free_name(source.name, _existing_names(destination.parent))
            if free_name.casefold() == destination.name.casefold():
                return None, OTHER
            destination = destination.with_name(free_name)
            if not _inside(folder, destination):
                return None, OUTSIDE
        except OSError as exc:
            return None, failure_text(exc, creating=False)


def _open_organization(conn: sqlite3.Connection, folder: Path) -> int:
    now = _utc_now()
    try:
        cursor = conn.execute(
            "INSERT INTO organizations (folder_path, started_at, status, "
            "moved_count, failed_count, created_at, updated_at) "
            "VALUES (?, ?, 'em_andamento', 0, 0, ?, ?)",
            (str(folder), now, now, now),
        )
        conn.commit()
    except sqlite3.Error as exc:
        # Ainda nao ha linha confirmada: so desfaz a insercao pendente.
        with contextlib.suppress(sqlite3.Error):
            conn.rollback()
        raise _error("BANCO_INDISPONIVEL") from exc
    if cursor.lastrowid is None:
        raise _error("BANCO_INDISPONIVEL")
    return cursor.lastrowid


def _interrupt_organization(
    conn: sqlite3.Connection, organization_id: int, result: OrganizationResult
) -> None:
    """Marca a organizacao como interrompida (6.3); nunca levanta.

    Se o banco continuar indisponivel a linha fica como esta e a recuperacao
    ao abrir o banco a corrige. O UPDATE leva AND status = em_andamento: so uma
    linha ainda em andamento e marcada, as demais ficam intactas.
    """
    with contextlib.suppress(sqlite3.Error):
        conn.rollback()
        now = _utc_now()
        conn.execute(
            "UPDATE organizations SET finished_at = ?, status = 'interrompida', "
            "moved_count = ?, failed_count = ?, updated_at = ? "
            "WHERE id = ? AND status = 'em_andamento'",
            (now, result.moved_count, result.failed_count, now, organization_id),
        )
        conn.commit()


def _record_operation(
    conn: sqlite3.Connection,
    organization_id: int,
    operation: PlannedOperation,
    destination: Path | None,
    message: str | None,
) -> None:
    now = _utc_now()
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, "
        "destination_path, category, rule_name, status, error_message, "
        "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            organization_id,
            operation.seq,
            str(operation.source_path),
            None if destination is None else str(destination),
            operation.category,
            operation.rule_name,
            "falha" if destination is None else "movido",
            message,
            now,
            now,
        ),
    )
    conn.commit()


def _close_organization(
    conn: sqlite3.Connection, organization_id: int, result: OrganizationResult
) -> None:
    now = _utc_now()
    try:
        conn.execute(
            "UPDATE organizations SET finished_at = ?, status = 'concluida', "
            "moved_count = ?, failed_count = ?, updated_at = ? WHERE id = ?",
            (now, result.moved_count, result.failed_count, now, organization_id),
        )
        conn.commit()
    except sqlite3.Error as exc:
        _interrupt_organization(conn, organization_id, result)
        raise _error("BANCO_INDISPONIVEL") from exc


def _run(
    plan: Plan,
    conn: sqlite3.Connection,
    progress_callback: Callable[[int, int, str], None] | None,
) -> OrganizationResult:
    total = len(plan.operations)
    organization_id = _open_organization(conn, plan.folder)
    result = OrganizationResult(
        organization_id=organization_id, moved_count=0, failed_count=0
    )
    for done, operation in enumerate(plan.operations):
        name = operation.source_path.name
        if progress_callback is not None:
            progress_callback(done, total, name)
        destination, message = _move_file(plan.folder, operation)
        try:
            _record_operation(conn, organization_id, operation, destination, message)
        except sqlite3.Error as exc:
            if destination is not None:
                # Sem registro o desfazer nao acharia o arquivo: devolve ao lugar.
                with contextlib.suppress(OSError):
                    os.rename(destination, operation.source_path)
            _interrupt_organization(conn, organization_id, result)
            raise _error("BANCO_INDISPONIVEL") from exc
        if message is None:
            result.moved_count += 1
        else:
            result.failed_count += 1
            result.failures.append((name, message))
    _close_organization(conn, organization_id, result)
    if progress_callback is not None:
        progress_callback(total, total, "")
    return result


def organize(
    plan: Plan,
    conn: sqlite3.Connection,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> OrganizationResult:
    """Executa o plano e grava o historico (6.3); plano vazio nao grava nada."""
    if plan.is_empty:
        return OrganizationResult(organization_id=0, moved_count=0, failed_count=0)
    if not OPERATION_LOCK.acquire(blocking=False):
        raise _error("ORGANIZACAO_EM_ANDAMENTO")
    try:
        return _run(plan, conn, progress_callback)
    finally:
        OPERATION_LOCK.release()
