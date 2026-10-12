"""Abertura da conexao SQLite do FilePilot (SPEC 5.1)."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from filepilot.db.migrations import apply_migrations
from filepilot.domain.errors import FilePilotError

_BANCO_INDISPONIVEL = "Não foi possível acessar o histórico do FilePilot."


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _recover_interrupted(conn: sqlite3.Connection) -> None:
    """Marca como interrompida toda organizacao que ficou em andamento (5.3).

    As contagens sao recalculadas de `operations`, porque `organizations`
    so as grava no fechamento; sem isso a linha recuperada ficaria com
    `moved_count` 0 e o desfazer a recusaria. Premissa: nenhuma organizacao
    esta em curso quando o banco e aberto (conexao unica, SPEC 7.1).
    """
    now = _utc_now()
    conn.execute(
        "UPDATE organizations SET status = 'interrompida', finished_at = ?, "
        "updated_at = ?, "
        "moved_count = (SELECT COUNT(*) FROM operations o "
        "WHERE o.organization_id = organizations.id AND o.status = ?), "
        "failed_count = (SELECT COUNT(*) FROM operations o "
        "WHERE o.organization_id = organizations.id AND o.status = ?) "
        "WHERE status = 'em_andamento'",
        (now, now, "movido", "falha"),
    )
    conn.commit()


def open_connection(db_path: Path) -> sqlite3.Connection:
    """Abre o banco, ativa as chaves estrangeiras e aplica as migracoes.

    Cria a pasta pai quando ela falta e recupera organizacoes que ficaram
    em andamento (5.3). Qualquer `sqlite3.Error` ou `OSError`
    de abertura sobe como `FilePilotError("BANCO_INDISPONIVEL", ...)`.
    """
    conn: sqlite3.Connection | None = None
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        apply_migrations(conn)
        _recover_interrupted(conn)
    except (sqlite3.Error, OSError) as exc:
        if conn is not None:
            conn.close()
        raise FilePilotError("BANCO_INDISPONIVEL", _BANCO_INDISPONIVEL) from exc
    return conn
