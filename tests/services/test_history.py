import sqlite3
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.services.history import (
    get_organization_detail,
    list_organizations,
)

NOW = "2026-10-11T12:00:00Z"


def _insert_organization(
    conn: sqlite3.Connection,
    started_at: str,
    status: str = "concluida",
    moved_count: int = 1,
    failed_count: int = 0,
    folder_path: str = "/pasta",
) -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, "
        "moved_count, failed_count, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (folder_path, started_at, status, moved_count, failed_count, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def _insert_operation(
    conn: sqlite3.Connection,
    organization_id: int,
    seq: int,
    status: str = "movido",
    destination_path: str | None = "/pasta/Documentos/a.pdf",
    error_message: str | None = None,
) -> None:
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, "
        "destination_path, category, rule_name, status, error_message, "
        "created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            organization_id,
            seq,
            f"/pasta/a{seq}.pdf",
            destination_path,
            "documentos",
            None,
            status,
            error_message,
            NOW,
            NOW,
        ),
    )
    conn.commit()


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    return open_connection(tmp_path / "historico.db")


def test_sem_registros_devolve_pagina_vazia(conn: sqlite3.Connection) -> None:
    page = list_organizations(conn)

    assert (page.items, page.total, page.page, page.page_size) == ([], 0, 1, 50)


def test_ordena_por_started_at_decrescente_com_desempate_por_id(
    conn: sqlite3.Connection,
) -> None:
    antiga = _insert_organization(conn, "2026-10-10T08:00:00Z")
    empate_a = _insert_organization(conn, "2026-10-11T09:00:00Z")
    empate_b = _insert_organization(conn, "2026-10-11T09:00:00Z")
    recente = _insert_organization(conn, "2026-10-12T07:00:00Z")

    page = list_organizations(conn)

    assert [row.id for row in page.items] == [recente, empate_b, empate_a, antiga]
    assert page.total == 4


def test_linha_traz_os_campos_do_banco(conn: sqlite3.Connection) -> None:
    org_id = _insert_organization(
        conn,
        "2026-10-11T09:00:00Z",
        status="interrompida",
        moved_count=3,
        failed_count=2,
        folder_path="/escolhida",
    )

    row = list_organizations(conn).items[0]

    assert (
        row.id,
        row.started_at,
        row.folder_path,
        row.moved_count,
        row.failed_count,
        row.status,
    ) == (org_id, "2026-10-11T09:00:00Z", "/escolhida", 3, 2, "interrompida")


def test_pagina_em_50_por_padrao(conn: sqlite3.Connection) -> None:
    for number in range(55):
        _insert_organization(conn, f"2026-10-11T10:{number:02d}:00Z")

    first = list_organizations(conn)
    second = list_organizations(conn, page=2)

    assert (len(first.items), first.total) == (50, 55)
    assert (len(second.items), second.page, second.total) == (5, 2, 55)
    assert {row.id for row in first.items}.isdisjoint(row.id for row in second.items)


def test_page_menor_que_1_vira_1(conn: sqlite3.Connection) -> None:
    _insert_organization(conn, "2026-10-11T09:00:00Z")

    assert list_organizations(conn, page=0).page == 1
    assert list_organizations(conn, page=-3).page == 1


@pytest.mark.parametrize("size", [0, -1, 201, 1000])
def test_page_size_fora_de_1_a_200_vira_50(
    conn: sqlite3.Connection, size: int
) -> None:
    assert list_organizations(conn, page_size=size).page_size == 50


@pytest.mark.parametrize("size", [1, 200])
def test_page_size_nos_limites_e_mantido(conn: sqlite3.Connection, size: int) -> None:
    assert list_organizations(conn, page_size=size).page_size == size


def test_page_size_pequeno_limita_os_itens(conn: sqlite3.Connection) -> None:
    for number in range(3):
        _insert_organization(conn, f"2026-10-11T10:0{number}:00Z")

    page = list_organizations(conn, page=2, page_size=2)

    assert (len(page.items), page.total) == (1, 3)


def test_detalhe_ordena_por_seq_crescente(conn: sqlite3.Connection) -> None:
    org_id = _insert_organization(conn, "2026-10-11T09:00:00Z")
    for seq in (3, 1, 2):
        _insert_operation(conn, org_id, seq)

    detail = get_organization_detail(conn, org_id)

    assert [op.seq for op in detail] == [1, 2, 3]


def test_detalhe_traz_os_campos_da_operacao(conn: sqlite3.Connection) -> None:
    org_id = _insert_organization(conn, "2026-10-11T09:00:00Z")
    _insert_operation(conn, org_id, 1)
    _insert_operation(
        conn,
        org_id,
        2,
        status="falha",
        destination_path=None,
        error_message="sem permissão",
    )

    ok, failed = get_organization_detail(conn, org_id)

    assert (ok.source_path, ok.destination_path, ok.status) == (
        "/pasta/a1.pdf",
        "/pasta/Documentos/a.pdf",
        "movido",
    )
    assert (ok.category, ok.rule_name, ok.error_message) == ("documentos", None, None)
    assert (failed.status, failed.destination_path, failed.error_message) == (
        "falha",
        None,
        "sem permissão",
    )


def test_detalhe_so_devolve_as_operacoes_da_organizacao(
    conn: sqlite3.Connection,
) -> None:
    first = _insert_organization(conn, "2026-10-11T09:00:00Z")
    second = _insert_organization(conn, "2026-10-11T10:00:00Z")
    _insert_operation(conn, first, 1)
    _insert_operation(conn, second, 1)
    _insert_operation(conn, second, 2)

    assert len(get_organization_detail(conn, first)) == 1
    assert len(get_organization_detail(conn, second)) == 2


def test_detalhe_de_organizacao_inexistente_e_lista_vazia(
    conn: sqlite3.Connection,
) -> None:
    assert get_organization_detail(conn, 999) == []


def test_banco_fechado_levanta_banco_indisponivel(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "historico.db")
    conn.close()

    with pytest.raises(FilePilotError) as listing:
        list_organizations(conn)
    with pytest.raises(FilePilotError) as detail:
        get_organization_detail(conn, 1)

    assert listing.value.code == "BANCO_INDISPONIVEL"
    assert detail.value.code == "BANCO_INDISPONIVEL"
