import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.ui import history_tab as history_tab_module
from filepilot.ui.history_tab import PAGE_SIZE, HistoryTab, format_local_time
from filepilot.ui.main_window import MainWindow
from filepilot.ui.organize_tab import OrganizeTab

NOW = "2026-10-11T12:00:00Z"
DATABASE_UNAVAILABLE = "Não foi possível acessar o histórico do FilePilot."


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _add_organization(
    conn: sqlite3.Connection,
    started_at: str,
    folder_path: str = "/pasta",
    status: str = "concluida",
    moved_count: int = 1,
    failed_count: int = 0,
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


def _add_operation(
    conn: sqlite3.Connection,
    organization_id: int,
    seq: int,
    status: str = "movido",
    destination_path: str | None = "/pasta/Documentos/a.pdf",
    error_message: str | None = None,
) -> None:
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, "
        "destination_path, status, error_message, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            organization_id,
            seq,
            f"/pasta/a{seq}.pdf",
            destination_path,
            status,
            error_message,
            NOW,
            NOW,
        ),
    )
    conn.commit()


def _rows(model: object) -> list[list[str]]:
    rows = model.rowCount()  # type: ignore[attr-defined]
    columns = model.columnCount()  # type: ignore[attr-defined]
    return [
        [model.index(row, column).data(Qt.ItemDataRole.DisplayRole) for column in range(columns)]  # type: ignore[attr-defined]
        for row in range(rows)
    ]


def _tab(qtbot: QtBot, conn: sqlite3.Connection) -> HistoryTab:
    tab = HistoryTab(conn)
    qtbot.addWidget(tab)
    tab.reload()
    return tab


def test_lista_da_mais_recente_para_a_mais_antiga_com_as_colunas(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _add_organization(conn, "2026-10-10T08:00:00Z", "/antiga", "interrompida", 2, 1)
    _add_organization(conn, "2026-10-12T09:30:00Z", "/recente", "concluida", 5, 0)
    _add_organization(conn, "2026-10-11T10:00:00Z", "/meio", "desfeita", 3, 0)

    tab = _tab(qtbot, conn)

    assert [tab.organization_model.headerData(i, Qt.Orientation.Horizontal) for i in range(5)] == [
        "Data e hora",
        "Pasta",
        "Movidos",
        "Falhas",
        "Situação",
    ]
    assert _rows(tab.organization_model) == [
        [format_local_time("2026-10-12T09:30:00Z"), "/recente", "5", "0", "Concluída"],
        [format_local_time("2026-10-11T10:00:00Z"), "/meio", "3", "0", "Desfeita"],
        [format_local_time("2026-10-10T08:00:00Z"), "/antiga", "2", "1", "Interrompida"],
    ]


def test_situacao_em_andamento_e_data_no_horario_local(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _add_organization(conn, "2026-10-12T09:30:00Z", status="em_andamento", moved_count=0)

    tab = _tab(qtbot, conn)

    local = datetime(2026, 10, 12, 9, 30, tzinfo=UTC).astimezone()
    row = _rows(tab.organization_model)[0]
    assert row[0] == local.strftime("%d/%m/%Y %H:%M")
    assert len(row[0]) == len("12/10/2026 09:30")
    assert row[4] == "Em andamento"


def test_data_ilegivel_aparece_como_esta() -> None:
    assert format_local_time("ontem") == "ontem"


def test_selecionar_mostra_as_operacoes_da_organizacao(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    organization_id = _add_organization(conn, "2026-10-12T09:30:00Z", failed_count=2)
    _add_operation(conn, organization_id, 1, "movido", "/pasta/Documentos/a1.pdf")
    _add_operation(conn, organization_id, 2, "falha", None, "O arquivo está em uso.")
    _add_operation(conn, organization_id, 3, "restaurado", "/pasta/Imagens/a3.pdf")
    _add_operation(conn, organization_id, 4, "nao_restaurado", "/pasta/Imagens/a4.pdf")
    tab = _tab(qtbot, conn)

    tab.organization_view.selectRow(0)

    assert tab.selected_id == organization_id
    assert [tab.operation_model.headerData(i, Qt.Orientation.Horizontal) for i in range(5)] == [
        "Arquivo",
        "Origem",
        "Destino final",
        "Situação",
        "Detalhe",
    ]
    assert _rows(tab.operation_model) == [
        ["a1.pdf", "/pasta/a1.pdf", "/pasta/Documentos/a1.pdf", "Movido", ""],
        ["a2.pdf", "/pasta/a2.pdf", "", "Falha", "O arquivo está em uso."],
        ["a3.pdf", "/pasta/a3.pdf", "/pasta/Imagens/a3.pdf", "Restaurado", ""],
        ["a4.pdf", "/pasta/a4.pdf", "/pasta/Imagens/a4.pdf", "Não restaurado", ""],
    ]
    assert tab.detail_label.isHidden()
    assert not tab.operation_view.isHidden()


def test_sem_selecao_o_painel_direito_pede_para_selecionar(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _add_organization(conn, "2026-10-12T09:30:00Z")

    tab = _tab(qtbot, conn)

    assert tab.selected_id is None
    assert tab.detail_label.text() == "Selecione uma organização."
    assert not tab.detail_label.isHidden()
    assert tab.operation_view.isHidden()


def test_limpar_a_selecao_volta_a_mensagem(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    organization_id = _add_organization(conn, "2026-10-12T09:30:00Z")
    _add_operation(conn, organization_id, 1)
    tab = _tab(qtbot, conn)
    tab.organization_view.selectRow(0)

    tab.organization_view.clearSelection()

    assert tab.selected_id is None
    assert tab.detail_label.text() == "Selecione uma organização."
    assert _rows(tab.operation_model) == []


def test_historico_vazio_mostra_a_mensagem(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    tab = _tab(qtbot, conn)

    assert tab.status_label.text() == "Nenhuma organização registrada ainda."
    assert _rows(tab.organization_model) == []
    assert tab.retry_button.isHidden()
    assert not tab.previous_button.isEnabled()
    assert not tab.next_button.isEnabled()


def test_falha_de_leitura_mostra_a_mensagem_e_tentar_de_novo(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    _add_organization(conn, "2026-10-12T09:30:00Z")
    real = history_tab_module.list_organizations

    def broken(*args: object, **kwargs: object) -> None:
        raise FilePilotError("BANCO_INDISPONIVEL", DATABASE_UNAVAILABLE)

    monkeypatch.setattr(history_tab_module, "list_organizations", broken)
    tab = HistoryTab(conn)
    qtbot.addWidget(tab)

    tab.reload()

    assert tab.status_label.text() == DATABASE_UNAVAILABLE
    assert not tab.retry_button.isHidden()
    assert tab.retry_button.text() == "Tentar de novo"
    assert _rows(tab.organization_model) == []

    monkeypatch.setattr(history_tab_module, "list_organizations", real)
    tab.retry_button.click()

    assert tab.status_label.text() == ""
    assert tab.retry_button.isHidden()
    assert len(_rows(tab.organization_model)) == 1


def test_anterior_desabilitado_na_pagina_1_e_proxima_pelo_total(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    for minute in range(PAGE_SIZE):
        _add_organization(conn, f"2026-10-12T09:{minute:02d}:00Z")

    tab = _tab(qtbot, conn)

    assert tab.page == 1
    assert len(_rows(tab.organization_model)) == PAGE_SIZE
    assert not tab.previous_button.isEnabled()
    # page * 50 >= total (50 >= 50): nao ha segunda pagina.
    assert not tab.next_button.isEnabled()


def test_proxima_e_anterior_trocam_de_pagina(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    for minute in range(PAGE_SIZE):
        _add_organization(conn, f"2026-10-12T09:{minute:02d}:00Z")
    oldest = _add_organization(conn, "2026-10-01T08:00:00Z", folder_path="/a-mais-antiga")
    tab = _tab(qtbot, conn)
    assert tab.next_button.isEnabled()

    tab.next_button.click()

    assert tab.page == 2
    assert [row[1] for row in _rows(tab.organization_model)] == ["/a-mais-antiga"]
    assert tab.previous_button.isEnabled()
    assert not tab.next_button.isEnabled()
    tab.organization_view.selectRow(0)
    assert tab.selected_id == oldest

    tab.previous_button.click()

    assert tab.page == 1
    assert len(_rows(tab.organization_model)) == PAGE_SIZE
    assert not tab.previous_button.isEnabled()
    assert tab.selected_id is None


def test_reload_mantem_a_pagina_e_a_selecao(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    organization_id = _add_organization(conn, "2026-10-12T09:30:00Z")
    _add_operation(conn, organization_id, 1)
    tab = _tab(qtbot, conn)
    tab.organization_view.selectRow(0)

    tab.reload()

    assert tab.selected_id == organization_id
    assert len(_rows(tab.operation_model)) == 1


def test_organizacao_terminada_recarrega_a_pagina_1(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    for minute in range(PAGE_SIZE):
        _add_organization(conn, f"2026-10-12T09:{minute:02d}:00Z")
    _add_organization(conn, "2026-10-01T08:00:00Z")
    tab = _tab(qtbot, conn)
    tab.next_button.click()
    assert tab.page == 2
    new_id = _add_organization(conn, "2026-10-12T11:00:00Z", folder_path="/nova")

    tab.on_organization_finished(new_id)

    assert tab.page == 1
    assert _rows(tab.organization_model)[0][1] == "/nova"


def test_janela_liga_organization_finished_ao_historico(
    qtbot: QtBot, tmp_path: Path
) -> None:
    window = MainWindow(tmp_path / "filepilot.db")
    qtbot.addWidget(window)
    organize = window.tabs.widget(0)
    history = window.tabs.widget(1)
    assert isinstance(organize, OrganizeTab)
    assert isinstance(history, HistoryTab)
    new_id = _add_organization(window.conn, "2026-10-12T11:00:00Z", folder_path="/nova")

    organize.organization_finished.emit(new_id)

    assert [row[1] for row in _rows(history.organization_model)] == ["/nova"]


def test_a_aba_nao_consulta_o_banco_por_conta_propria() -> None:
    source = Path(history_tab_module.__file__).read_text(encoding="utf-8")

    # `sqlite3` entra so na anotacao de tipo da conexao; a consulta e do servico.
    assert ".execute(" not in source
    assert "SELECT " not in source
