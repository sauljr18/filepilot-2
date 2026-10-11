import sqlite3
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.db.migrations import MIGRATIONS, apply_migrations
from filepilot.domain.errors import FilePilotError

NOW = "2026-10-11T12:00:00Z"


def _insert_organization(conn: sqlite3.Connection) -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, created_at, updated_at) "
        "VALUES (?, ?, ?, ?)",
        ("/pasta", NOW, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def _insert_operation(
    conn: sqlite3.Connection,
    organization_id: int,
    seq: int = 1,
    status: str = "movido",
    destination_path: str | None = "/pasta/Documentos/a.pdf",
) -> None:
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, "
        "destination_path, status, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (organization_id, seq, "/pasta/a.pdf", destination_path, status, NOW, NOW),
    )


def test_open_connection_cria_a_pasta_pai(tmp_path: Path) -> None:
    db_path = tmp_path / "dados" / "FilePilot" / "filepilot.db"
    conn = open_connection(db_path)
    conn.close()
    assert db_path.is_file()


def test_open_connection_ativa_foreign_keys(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    assert conn.execute("PRAGMA foreign_keys").fetchone() == (1,)
    conn.close()


def test_migracao_cria_tabelas_e_indices(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    tabelas = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    }
    indices = {
        row[0]
        for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'index'")
    }
    conn.close()
    assert {
        "schema_migrations",
        "organizations",
        "operations",
        "rules",
        "rule_extensions",
    } <= tabelas
    assert {
        "idx_organizations_started_at",
        "idx_operations_organization_seq",
        "idx_rule_extensions_extension",
    } <= indices


def test_abrir_duas_vezes_mantem_uma_linha_em_schema_migrations(
    tmp_path: Path,
) -> None:
    db_path = tmp_path / "filepilot.db"
    open_connection(db_path).close()
    conn = open_connection(db_path)
    linhas = conn.execute("SELECT version FROM schema_migrations").fetchall()
    conn.close()
    assert linhas == [(1,)]


def test_apply_migrations_e_idempotente_na_mesma_conexao(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    apply_migrations(conn)
    total = conn.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()
    conn.close()
    assert total == (len(MIGRATIONS),)


def test_schema_migrations_grava_applied_at_em_utc_iso(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    (applied_at,) = conn.execute("SELECT applied_at FROM schema_migrations").fetchone()
    conn.close()
    assert len(applied_at) == 20
    assert applied_at.endswith("Z")
    assert applied_at[10] == "T"


def test_operations_rejeita_status_invalido(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    organization_id = _insert_organization(conn)
    with pytest.raises(sqlite3.IntegrityError):
        _insert_operation(conn, organization_id, status="desconhecido")
    conn.close()


@pytest.mark.parametrize(
    "status", ["movido", "falha", "restaurado", "nao_restaurado"]
)
def test_operations_aceita_os_quatro_status(tmp_path: Path, status: str) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    organization_id = _insert_organization(conn)
    destino = None if status == "falha" else "/pasta/Documentos/a.pdf"
    _insert_operation(conn, organization_id, status=status, destination_path=destino)
    conn.close()


def test_operations_sem_destino_so_na_falha(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    organization_id = _insert_organization(conn)
    with pytest.raises(sqlite3.IntegrityError):
        _insert_operation(conn, organization_id, status="movido", destination_path=None)
    conn.close()


def test_excluir_organizacao_apaga_as_operacoes(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    organization_id = _insert_organization(conn)
    _insert_operation(conn, organization_id, seq=1)
    _insert_operation(conn, organization_id, seq=2)
    conn.commit()
    conn.execute("DELETE FROM organizations WHERE id = ?", (organization_id,))
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM operations").fetchone()
    conn.close()
    assert total == (0,)


def test_operations_exige_organizacao_existente(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    with pytest.raises(sqlite3.IntegrityError):
        _insert_operation(conn, organization_id=999)
    conn.close()


def test_organizations_rejeita_status_invalido(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO organizations (folder_path, started_at, status, "
            "created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            ("/pasta", NOW, "invalido", NOW, NOW),
        )
    conn.close()


def test_organizations_status_padrao_e_em_andamento(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    organization_id = _insert_organization(conn)
    (status,) = conn.execute(
        "SELECT status FROM organizations WHERE id = ?", (organization_id,)
    ).fetchone()
    conn.close()
    assert status == "em_andamento"


def test_excluir_regra_apaga_as_extensoes(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    cursor = conn.execute(
        "INSERT INTO rules (name, destination_folder, position, created_at, "
        "updated_at) VALUES (?, ?, ?, ?, ?)",
        ("Fotos", "Fotos", 1, NOW, NOW),
    )
    rule_id = cursor.lastrowid
    conn.execute(
        "INSERT INTO rule_extensions (rule_id, extension) VALUES (?, ?)",
        (rule_id, "raw"),
    )
    conn.commit()
    conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
    conn.commit()
    total = conn.execute("SELECT COUNT(*) FROM rule_extensions").fetchone()
    conn.close()
    assert total == (0,)


def test_rules_posicao_e_unica(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "filepilot.db")
    sql = (
        "INSERT INTO rules (name, destination_folder, position, created_at, "
        "updated_at) VALUES (?, ?, ?, ?, ?)"
    )
    conn.execute(sql, ("A", "A", 1, NOW, NOW))
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(sql, ("B", "B", 1, NOW, NOW))
    conn.close()


def test_open_connection_banco_inacessivel_levanta_banco_indisponivel(
    tmp_path: Path,
) -> None:
    with pytest.raises(FilePilotError) as info:
        open_connection(tmp_path)
    assert info.value.code == "BANCO_INDISPONIVEL"
