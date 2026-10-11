"""Abertura da conexao SQLite do FilePilot (SPEC 5.1)."""

import sqlite3
from pathlib import Path

from filepilot.db.migrations import apply_migrations
from filepilot.domain.errors import FilePilotError

_BANCO_INDISPONIVEL = "Não foi possível acessar o histórico do FilePilot."


def open_connection(db_path: Path) -> sqlite3.Connection:
    """Abre o banco, ativa as chaves estrangeiras e aplica as migracoes.

    Cria a pasta pai quando ela falta. Qualquer `sqlite3.Error` ou `OSError`
    de abertura sobe como `FilePilotError("BANCO_INDISPONIVEL", ...)`.
    """
    conn: sqlite3.Connection | None = None
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        apply_migrations(conn)
    except (sqlite3.Error, OSError) as exc:
        if conn is not None:
            conn.close()
        raise FilePilotError("BANCO_INDISPONIVEL", _BANCO_INDISPONIVEL) from exc
    return conn
