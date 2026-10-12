import sqlite3
from pathlib import Path

from PySide6.QtWidgets import QTabWidget, QWidget
from pytestqt.qtbot import QtBot

from filepilot.ui.main_window import MainWindow, build_tabs


class ReloadSpy(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.reloads = 0

    def reload(self) -> None:
        self.reloads += 1


def _make_window(qtbot: QtBot, tmp_path: Path) -> MainWindow:
    window = MainWindow(tmp_path / "filepilot.db")
    qtbot.addWidget(window)
    return window


def test_janela_tem_titulo_e_tres_abas_em_ordem(qtbot: QtBot, tmp_path: Path) -> None:
    window = _make_window(qtbot, tmp_path)

    tabs = window.centralWidget()
    assert window.windowTitle() == "FilePilot"
    assert isinstance(tabs, QTabWidget)
    assert [tabs.tabText(i) for i in range(tabs.count())] == [
        "Organizar",
        "Histórico",
        "Regras",
    ]


def test_organizing_comeca_falso_e_conn_esta_aberta(
    qtbot: QtBot, tmp_path: Path
) -> None:
    window = _make_window(qtbot, tmp_path)

    assert window.organizing is False
    assert (tmp_path / "filepilot.db").exists()
    assert window.conn.execute("SELECT COUNT(*) FROM organizations").fetchone() == (0,)


def test_build_tabs_devolve_tres_marcadores_na_ordem(tmp_path: Path) -> None:
    conn = sqlite3.connect(tmp_path / "x.db")
    try:
        built = build_tabs(conn)
    finally:
        conn.close()

    assert [title for title, _ in built] == ["Organizar", "Histórico", "Regras"]
    assert all(isinstance(widget, QWidget) for _, widget in built)


def test_trocar_para_historico_e_regras_recarrega_a_aba(
    qtbot: QtBot, tmp_path: Path
) -> None:
    window = _make_window(qtbot, tmp_path)
    tabs = window.tabs
    spies = [ReloadSpy() for _ in range(3)]
    while tabs.count():
        tabs.removeTab(0)
    for title, spy in zip(("Organizar", "Histórico", "Regras"), spies, strict=True):
        tabs.addTab(spy, title)

    tabs.setCurrentIndex(1)
    tabs.setCurrentIndex(2)

    assert [spy.reloads for spy in spies] == [0, 1, 1]


def test_voltar_para_organizar_nao_recarrega(qtbot: QtBot, tmp_path: Path) -> None:
    window = _make_window(qtbot, tmp_path)
    tabs = window.tabs
    spies = [ReloadSpy() for _ in range(3)]
    while tabs.count():
        tabs.removeTab(0)
    for title, spy in zip(("Organizar", "Histórico", "Regras"), spies, strict=True):
        tabs.addTab(spy, title)
    tabs.setCurrentIndex(1)

    tabs.setCurrentIndex(0)

    assert [spy.reloads for spy in spies] == [0, 1, 0]
