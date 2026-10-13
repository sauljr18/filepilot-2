import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import OrganizationResult, Plan
from filepilot.services.history import OperationRow
from filepilot.ui import history_tab as history_tab_module
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui import organize_worker as organize_worker_module
from filepilot.ui.history_tab import PAGE_SIZE, HistoryTab
from filepilot.ui.main_window import MainWindow
from filepilot.ui.organize_tab import OrganizeTab

NOW = "2026-10-11T12:00:00Z"
DATABASE_UNAVAILABLE = "Não foi possível acessar o histórico do FilePilot."


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _add_organization(conn: sqlite3.Connection, started_at: str, folder_path: str = "/pasta") -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, moved_count, "
        "failed_count, created_at, updated_at) VALUES (?, ?, 'concluida', 1, 0, ?, ?)",
        (folder_path, started_at, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def _add_operation(conn: sqlite3.Connection, organization_id: int, seq: int) -> None:
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, destination_path, "
        "status, created_at, updated_at) VALUES (?, ?, ?, ?, 'movido', ?, ?)",
        (organization_id, seq, f"/pasta/a{seq}.pdf", f"/pasta/Documentos/a{seq}.pdf", NOW, NOW),
    )
    conn.commit()


def _tab(qtbot: QtBot, conn: sqlite3.Connection) -> HistoryTab:
    tab = HistoryTab(conn)
    qtbot.addWidget(tab)
    tab.reload()
    return tab


def test_enquanto_o_detalhe_carrega_mostra_carregando_detalhes(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    organization_id = _add_organization(conn, "2026-10-12T09:30:00Z")
    _add_operation(conn, organization_id, 1)
    tab = _tab(qtbot, conn)
    real = history_tab_module.get_organization_detail
    seen: list[tuple[str, bool, bool]] = []

    def spy(connection: sqlite3.Connection, selected: int) -> list[OperationRow]:
        seen.append(
            (tab.detail_label.text(), tab.detail_label.isHidden(), tab.operation_view.isHidden())
        )
        return real(connection, selected)

    monkeypatch.setattr(history_tab_module, "get_organization_detail", spy)

    tab.organization_view.selectRow(0)

    assert seen == [("Carregando detalhes...", False, True)]
    assert tab.detail_label.isHidden()
    assert tab.operation_model.rowCount() == 1


def test_organizacao_sem_operacoes_mostra_nenhum_arquivo(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _add_organization(conn, "2026-10-12T09:30:00Z")
    tab = _tab(qtbot, conn)

    tab.organization_view.selectRow(0)

    assert tab.detail_label.text() == "Nenhum arquivo nesta organização."
    assert not tab.detail_label.isHidden()
    assert tab.operation_view.isHidden()


def test_erro_ao_ler_o_detalhe_mostra_a_mensagem_do_banco(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    organization_id = _add_organization(conn, "2026-10-12T09:30:00Z")
    _add_operation(conn, organization_id, 1)
    tab = _tab(qtbot, conn)
    real = history_tab_module.get_organization_detail

    def broken(connection: sqlite3.Connection, selected: int) -> list[OperationRow]:
        raise FilePilotError("BANCO_INDISPONIVEL", DATABASE_UNAVAILABLE)

    monkeypatch.setattr(history_tab_module, "get_organization_detail", broken)
    tab.organization_view.selectRow(0)

    assert tab.detail_label.text() == DATABASE_UNAVAILABLE
    assert not tab.retry_button.isHidden()

    monkeypatch.setattr(history_tab_module, "get_organization_detail", real)
    tab.retry_button.click()

    assert tab.retry_button.isHidden()
    assert tab.operation_model.rowCount() == 1
    assert tab.selected_id == organization_id


def test_show_organization_carrega_a_pagina_seleciona_a_linha_e_mostra_os_detalhes(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    for minute in range(PAGE_SIZE):
        _add_organization(conn, f"2026-10-12T09:{minute:02d}:00Z")
    oldest = _add_organization(conn, "2026-10-01T08:00:00Z", folder_path="/a-mais-antiga")
    _add_operation(conn, oldest, 1)
    _add_operation(conn, oldest, 2)
    tab = _tab(qtbot, conn)
    assert tab.page == 1

    tab.show_organization(oldest)

    assert tab.page == 2
    assert tab.selected_id == oldest
    selected = tab.organization_view.selectionModel().selectedRows()
    assert [index.row() for index in selected] == [0]
    assert tab.organization_model.index(0, 1).data(Qt.ItemDataRole.DisplayRole) == "/a-mais-antiga"
    assert tab.operation_model.rowCount() == 2
    assert tab.detail_label.isHidden()


def test_show_organization_na_pagina_1_volta_do_painel_vazio(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    older = _add_organization(conn, "2026-10-11T09:00:00Z")
    newest = _add_organization(conn, "2026-10-12T09:00:00Z")
    _add_operation(conn, older, 1)
    tab = _tab(qtbot, conn)

    tab.show_organization(older)

    assert tab.page == 1
    assert tab.selected_id == older
    assert tab.selected_id != newest
    assert tab.operation_model.rowCount() == 1


def test_show_organization_inexistente_deixa_a_pagina_1_sem_selecao(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    for minute in range(PAGE_SIZE + 1):
        _add_organization(conn, f"2026-10-12T09:{minute:02d}:00Z")
    tab = _tab(qtbot, conn)

    tab.show_organization(99999)

    assert tab.page == 1
    assert tab.selected_id is None
    assert tab.detail_label.text() == "Selecione uma organização."


def test_show_organization_com_banco_falhando_mostra_o_erro(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    organization_id = _add_organization(conn, "2026-10-12T09:30:00Z")
    tab = _tab(qtbot, conn)

    def broken(*args: object, **kwargs: object) -> None:
        raise FilePilotError("BANCO_INDISPONIVEL", DATABASE_UNAVAILABLE)

    monkeypatch.setattr(history_tab_module, "list_organizations", broken)

    tab.show_organization(organization_id)

    assert tab.status_label.text() == DATABASE_UNAVAILABLE
    assert not tab.retry_button.isHidden()


# -- botao "Ver detalhes" da aba Organizar ------------------------------------


class _Failures:
    """Faz o `organize` real devolver `failed_count` escolhido pelo teste."""

    def __init__(self, monkeypatch: pytest.MonkeyPatch, failed_count: int) -> None:
        self.failed_count = failed_count
        real = organize_worker_module.organize

        def organize(plan: Plan, connection: sqlite3.Connection, callback: object = None) -> object:
            result = real(plan, connection, callback)  # type: ignore[arg-type]
            return OrganizationResult(
                organization_id=result.organization_id,
                moved_count=result.moved_count,
                failed_count=self.failed_count,
            )

        monkeypatch.setattr(organize_worker_module, "organize", organize)


def _window(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *names: str
) -> tuple[MainWindow, OrganizeTab, HistoryTab, Path]:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
    window = MainWindow(tmp_path / "db" / "filepilot.db")
    qtbot.addWidget(window)
    organize = window.tabs.widget(0)
    history = window.tabs.widget(1)
    assert isinstance(organize, OrganizeTab)
    assert isinstance(history, HistoryTab)
    monkeypatch.setattr(
        organize_tab_module.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(folder),
    )
    organize.choose_button.click()
    return window, organize, history, folder


def _organize(qtbot: QtBot, tab: OrganizeTab) -> None:
    with qtbot.waitSignal(tab.organization_finished, timeout=5000):
        tab.organize_button.click()


def test_ver_detalhes_comeca_escondido(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")

    assert tab.details_button.text() == "Ver detalhes"
    assert tab.details_button.isHidden()


def test_ver_detalhes_so_aparece_com_falhas(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failures = _Failures(monkeypatch, failed_count=0)
    _, tab, _, folder = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    assert tab.details_button.isHidden()

    (folder / "nota.pdf").write_bytes(b"x")
    tab.refresh()
    failures.failed_count = 2
    _organize(qtbot, tab)

    assert not tab.details_button.isHidden()
    assert tab.summary.text() == "Concluído: 1 movidos, 2 falhas."


@pytest.mark.parametrize("action", ["refresh", "choose"])
def test_ver_detalhes_some_ao_atualizar_ou_escolher_outra_pasta(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, action: str
) -> None:
    failures = _Failures(monkeypatch, failed_count=2)
    _, tab, _, folder = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    assert not tab.details_button.isHidden()
    (folder / "nota.pdf").write_bytes(b"x")
    failures.failed_count = 0

    if action == "refresh":
        tab.refresh_button.click()
    else:
        tab.choose_button.click()

    assert tab.details_button.isHidden()


def test_ver_detalhes_some_assim_que_uma_nova_organizacao_comeca(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    failures = _Failures(monkeypatch, failed_count=2)
    _, tab, _, folder = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    assert not tab.details_button.isHidden()
    (folder / "nota.pdf").write_bytes(b"x")
    failures.failed_count = 0

    with qtbot.waitSignal(tab.organization_finished, timeout=5000):
        # Depois de organizar tudo o botao fica desabilitado: chama o metodo dele.
        tab.organize()
        assert tab.details_button.isHidden()

    assert tab.details_button.isHidden()


def test_ver_detalhes_abre_o_historico_com_a_organizacao_selecionada(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _Failures(monkeypatch, failed_count=1)
    window, tab, history, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg", "nota.pdf")
    _organize(qtbot, tab)
    assert window.tabs.currentWidget() is tab

    tab.details_button.click()

    assert window.tabs.currentWidget() is history
    assert history.selected_id is not None
    assert history.operation_model.rowCount() == 2
    assert history.detail_label.isHidden()
