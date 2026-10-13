import sqlite3
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from filepilot.domain.errors import FilePilotError
from filepilot.services.undo import UndoResult
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui import organize_worker as organize_worker_module
from filepilot.ui.main_window import MainWindow
from filepilot.ui.organize_tab import OrganizeTab

INVALID_MESSAGE = "A pasta escolhida não existe ou não é uma pasta."
GENERIC_MESSAGE = "Ocorreu um erro inesperado. Tente de novo."


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


def test_laco_no_desfazer_mostra_a_mensagem_de_contrato_e_mantem_o_botao(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)

    def loop(connection: sqlite3.Connection) -> UndoResult:
        raise FilePilotError("PASTA_INVALIDA", INVALID_MESSAGE)

    monkeypatch.setattr(organize_worker_module, "undo_last", loop)

    _undo(qtbot, tab)

    assert tab.summary.text() == INVALID_MESSAGE
    assert tab.summary.text() != GENERIC_MESSAGE
    assert tab.undo_button.isEnabled()
    assert window.organizing is False
