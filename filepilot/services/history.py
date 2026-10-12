"""Historico de organizacoes (SPEC 6.4).

Leitura pura do banco: lista as organizacoes, devolve as operacoes de uma
delas e diz qual e a ultima desfazivel. Nada aqui altera disco ou banco.
"""

import sqlite3
from dataclasses import dataclass, field

from filepilot.domain.errors import FilePilotError

_DEFAULT_PAGE_SIZE = 50
_MAX_PAGE_SIZE = 200
_UNDOABLE_STATUSES = ("concluida", "interrompida")
_BANCO_INDISPONIVEL = "Não foi possível acessar o histórico do FilePilot."


@dataclass(frozen=True)
class OrganizationRow:
    """Linha de `organizations`, com os nomes de coluna de 5.3."""

    id: int
    started_at: str
    folder_path: str
    moved_count: int
    failed_count: int
    status: str


@dataclass(frozen=True)
class OperationRow:
    """Linha de `operations`, com os nomes de coluna de 5.3."""

    seq: int
    source_path: str
    destination_path: str | None
    category: str | None
    rule_name: str | None
    status: str
    error_message: str | None


@dataclass
class OrganizationPage:
    """Pagina do historico (6.4)."""

    items: list[OrganizationRow] = field(default_factory=list)
    page: int = 1
    page_size: int = _DEFAULT_PAGE_SIZE
    total: int = 0


def _banco_indisponivel() -> FilePilotError:
    return FilePilotError("BANCO_INDISPONIVEL", _BANCO_INDISPONIVEL)


def _organization_row(row: tuple[int, str, str, int, int, str]) -> OrganizationRow:
    return OrganizationRow(
        id=row[0],
        started_at=row[1],
        folder_path=row[2],
        moved_count=row[3],
        failed_count=row[4],
        status=row[5],
    )


_ORGANIZATION_COLUMNS = "id, started_at, folder_path, moved_count, failed_count, status"


def list_organizations(
    conn: sqlite3.Connection,
    page: int = 1,
    page_size: int = _DEFAULT_PAGE_SIZE,
) -> OrganizationPage:
    """Lista as organizacoes da mais recente para a mais antiga (6.4).

    `page` menor que 1 vira 1 e `page_size` fora de 1 a 200 vira 50. O desempate
    de `started_at` e por `id` decrescente.
    """
    if page < 1:
        page = 1
    if not 1 <= page_size <= _MAX_PAGE_SIZE:
        page_size = _DEFAULT_PAGE_SIZE
    try:
        total = conn.execute("SELECT COUNT(*) FROM organizations").fetchone()[0]
        rows = conn.execute(
            f"SELECT {_ORGANIZATION_COLUMNS} FROM organizations "
            "ORDER BY started_at DESC, id DESC LIMIT ? OFFSET ?",
            (page_size, (page - 1) * page_size),
        ).fetchall()
    except sqlite3.Error as exc:
        raise _banco_indisponivel() from exc
    return OrganizationPage(
        items=[_organization_row(row) for row in rows],
        page=page,
        page_size=page_size,
        total=total,
    )


def get_organization_detail(
    conn: sqlite3.Connection, organization_id: int
) -> list[OperationRow]:
    """Operacoes de uma organizacao por `seq` crescente; vazio se nao existe."""
    try:
        rows = conn.execute(
            "SELECT seq, source_path, destination_path, category, rule_name, "
            "status, error_message FROM operations "
            "WHERE organization_id = ? ORDER BY seq",
            (organization_id,),
        ).fetchall()
    except sqlite3.Error as exc:
        raise _banco_indisponivel() from exc
    return [
        OperationRow(
            seq=row[0],
            source_path=row[1],
            destination_path=row[2],
            category=row[3],
            rule_name=row[4],
            status=row[5],
            error_message=row[6],
        )
        for row in rows
    ]


def last_undoable(conn: sqlite3.Connection) -> OrganizationRow | None:
    """Ultima organizacao, so se for desfazivel (6.4); senao `None`.

    A ultima e a de maior `started_at`, com desempate por `id`. Nao ha
    retrocesso: se ela nao e desfazivel, nenhuma anterior e devolvida.
    """
    try:
        row = conn.execute(
            f"SELECT {_ORGANIZATION_COLUMNS} FROM organizations "
            "ORDER BY started_at DESC, id DESC LIMIT 1"
        ).fetchone()
    except sqlite3.Error as exc:
        raise _banco_indisponivel() from exc
    if row is None:
        return None
    last = _organization_row(row)
    if last.status in _UNDOABLE_STATUSES and last.moved_count >= 1:
        return last
    return None
