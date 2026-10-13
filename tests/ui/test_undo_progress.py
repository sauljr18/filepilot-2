import sqlite3
import threading
from collections.abc import Iterator
from contextlib import closing
from pathlib import Path

import pytest
from PySide6.QtCore import QObject
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.services.undo import UndoResult
from filepilot.ui import main_window as main_window_module
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui import organize_worker as organize_worker_module
from filepilot.ui.main_window import MainWindow
from filepilot.ui.organize_tab import OrganizeTab

NOW = "2026-10-11T12:00:00Z"


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _add_organization(
    conn: sqlite3.Connection,
    status: str = "concluida",
    moved_count: int = 1,
    folder_path: str = "/outra-pasta",
    started_at: str = "2026-10-12T09:00:00Z",
) -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, moved_count, "
        "failed_count, created_at, updated_at) VALUES (?, ?, ?, ?, 0, ?, ?)",
        (folder_path, started_at, status, moved_count, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def _window(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *names: str
) -> tuple[MainWindow, OrganizeTab, Path]:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
    window = MainWindow(tmp_path / "db" / "filepilot.db")
    qtbot.addWidget(window)
    tab = window.tabs.widget(0)
    assert isinstance(tab, OrganizeTab)
    monkeypatch.setattr(
        organize_tab_module.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(folder),
    )
    tab.choose_button.click()
    return window, tab, folder


def _organize(qtbot: QtBot, tab: OrganizeTab) -> None:
    with qtbot.waitSignal(tab.organization_finished, timeout=5000):
        tab.organize()


def _undo(qtbot: QtBot, tab: OrganizeTab) -> None:
    with qtbot.waitSignal(
        tab.organizing_changed, timeout=5000, check_params_cb=lambda value: value is False
    ):
        tab.undo_button.click()


class _MessageSpy:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, parent: QObject, title: str, text: str) -> None:
        self.messages.append(text)


def test_depois_de_organizar_a_barra_esta_cheia_e_depois_de_desfazer_esta_escondida(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg", "nota.pdf")

    _organize(qtbot, tab)

    assert tab.progress.isHidden() is False
    assert tab.progress.value() == tab.progress.maximum()

    _undo(qtbot, tab)

    assert tab.progress.isHidden() is True


def test_durante_o_desfazer_a_barra_ja_esta_escondida(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = _MessageSpy()
    monkeypatch.setattr(main_window_module.QMessageBox, "information", spy)
    window, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    window.show()
    _organize(qtbot, tab)
    assert tab.progress.isHidden() is False
    release = threading.Event()
    real_undo = organize_worker_module.undo_last

    def slow(connection: sqlite3.Connection) -> UndoResult:
        assert release.wait(5)
        return real_undo(connection)

    monkeypatch.setattr(organize_worker_module, "undo_last", slow)

    tab.undo_button.click()

    assert window.organizing is True
    assert tab.progress.isHidden() is True
    with qtbot.waitSignal(
        tab.organizing_changed, timeout=5000, check_params_cb=lambda value: value is False
    ):
        release.set()
    assert tab.progress.isHidden() is True
    window.close()


def test_falha_inesperada_no_desfazer_deixa_a_barra_escondida(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    assert tab.progress.isHidden() is False

    def boom(connection: sqlite3.Connection) -> UndoResult:
        raise RuntimeError("RAW-INTERNAL-DETAIL")

    monkeypatch.setattr(organize_worker_module, "undo_last", boom)

    _undo(qtbot, tab)

    assert tab.summary.text() == "Ocorreu um erro inesperado. Tente de novo."
    assert tab.progress.isHidden() is True


def test_organizacao_de_outra_pasta_tambem_esconde_a_barra(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    assert tab.progress.isHidden() is False
    with closing(open_connection(tmp_path / "db" / "filepilot.db")) as other:
        _add_organization(
            other, folder_path=str(tmp_path / "outra"), started_at="2999-01-01T00:00:00Z"
        )
    tab.refresh_undo()
    assert tab.undo_button.isEnabled()

    _undo(qtbot, tab)

    assert tab.progress.isHidden() is True


def test_sem_organizacao_desfazivel_a_barra_continua_visivel(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    assert tab.progress.isHidden() is False
    tab._undoable = None

    tab.undo()

    assert tab.progress.isHidden() is False


def test_organizar_de_novo_depois_do_desfazer_mostra_a_barra_de_novo(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    _undo(qtbot, tab)
    assert tab.progress.isHidden() is True

    _organize(qtbot, tab)

    assert tab.progress.isHidden() is False
    assert tab.progress.value() == tab.progress.maximum()
