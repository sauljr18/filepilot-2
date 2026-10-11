"""Migracoes do banco SQLite (SPEC 5 e 13).

Cada migracao e uma tupla `(version, statements)`. Migracoes futuras so
acrescentam itens a `MIGRATIONS`, em ordem crescente de `version`.
"""

import sqlite3
from datetime import UTC, datetime

_MIGRATION_0001_INITIAL: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER NOT NULL,
        applied_at TEXT NOT NULL,
        PRIMARY KEY (version)
    )
    """,
    """
    CREATE TABLE organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        folder_path TEXT NOT NULL,
        started_at TEXT NOT NULL,
        finished_at TEXT,
        status TEXT NOT NULL DEFAULT 'em_andamento',
        moved_count INTEGER NOT NULL DEFAULT 0,
        failed_count INTEGER NOT NULL DEFAULT 0,
        undone_at TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        CHECK (status IN ('em_andamento','concluida','interrompida','desfeita')),
        CHECK (moved_count >= 0 AND failed_count >= 0)
    )
    """,
    """
    CREATE INDEX idx_organizations_started_at ON organizations (started_at)
    """,
    """
    CREATE TABLE operations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        seq INTEGER NOT NULL,
        source_path TEXT NOT NULL,
        destination_path TEXT,
        category TEXT,
        rule_name TEXT,
        status TEXT NOT NULL,
        error_message TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (organization_id) REFERENCES organizations (id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        UNIQUE (organization_id, seq),
        CHECK (status IN ('movido','falha','restaurado','nao_restaurado')),
        CHECK (status = 'falha' OR destination_path IS NOT NULL)
    )
    """,
    """
    CREATE INDEX idx_operations_organization_seq
        ON operations (organization_id, seq)
    """,
    """
    CREATE TABLE rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        destination_folder TEXT NOT NULL,
        position INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        UNIQUE (position),
        CHECK (length(name) BETWEEN 1 AND 60),
        CHECK (length(destination_folder) >= 1)
    )
    """,
    """
    CREATE TABLE rule_extensions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id INTEGER NOT NULL,
        extension TEXT NOT NULL,
        FOREIGN KEY (rule_id) REFERENCES rules (id)
            ON DELETE CASCADE ON UPDATE CASCADE,
        UNIQUE (rule_id, extension),
        CHECK (length(extension) BETWEEN 1 AND 15)
    )
    """,
    """
    CREATE INDEX idx_rule_extensions_extension ON rule_extensions (extension)
    """,
)

MIGRATIONS: list[tuple[int, tuple[str, ...]]] = [
    (1, _MIGRATION_0001_INITIAL),
]


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _applied_versions(conn: sqlite3.Connection) -> set[int]:
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type = 'table' "
        "AND name = 'schema_migrations'"
    ).fetchone()
    if exists is None:
        return set()
    rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    return {row[0] for row in rows}


def apply_migrations(conn: sqlite3.Connection) -> None:
    """Aplica, em ordem de version, as migracoes ainda nao registradas.

    Cada migracao roda em uma transacao unica junto com o seu registro em
    `schema_migrations`: ou entra inteira ou nao entra.
    """
    applied = _applied_versions(conn)
    for version, statements in sorted(MIGRATIONS):
        if version in applied:
            continue
        conn.execute("BEGIN")
        try:
            for statement in statements:
                conn.execute(statement)
            conn.execute(
                "INSERT INTO schema_migrations (version, applied_at) VALUES (?, ?)",
                (version, _utc_now()),
            )
        except BaseException:
            conn.rollback()
            raise
        conn.commit()
