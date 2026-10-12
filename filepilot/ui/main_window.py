"""Janela principal do FilePilot (SPEC 7.1)."""

import sqlite3
from functools import partial
from pathlib import Path
from typing import Protocol, runtime_checkable

from PySide6.QtCore import QLockFile
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget, QWidget

from filepilot.db.connection import open_connection
from filepilot.ui.history_tab import HistoryTab
from filepilot.ui.organize_tab import OrganizeTab
from filepilot.ui.rules_tab import RulesTab

WINDOW_TITLE = "FilePilot"
TAB_TITLES = ("Organizar", "Histórico", "Regras")
_CLOSE_BLOCKED = "Aguarde a organização terminar para fechar."
# Indices das abas que recarregam os dados ao receberem o foco (7.1).
_RELOAD_ON_FOCUS = (1, 2)


@runtime_checkable
class Reloadable(Protocol):
    """Aba que sabe recarregar os proprios dados."""

    def reload(self) -> None: ...


def build_tabs(
    conn: sqlite3.Connection, db_path: Path | None = None
) -> list[tuple[str, QWidget]]:
    """Cria as abas na ordem Organizar, Histórico e Regras.

    As tres abas sao reais e recebem a mesma conexao da janela; a Organizar
    recebe tambem o `db_path`, para o worker abrir a propria conexao.
    """
    organize, history, rules = TAB_TITLES
    return [
        (organize, OrganizeTab(conn, db_path)),
        (history, HistoryTab(conn)),
        (rules, RulesTab(conn)),
    ]


class MainWindow(QMainWindow):
    """`QTabWidget` com as abas do aplicativo, dona da conexao e da trava."""

    def __init__(self, db_path: Path, lock: QLockFile | None = None) -> None:
        super().__init__()
        self.db_path = db_path
        self.organizing = False
        self._lock = lock
        # Falha de abertura sobe como FilePilotError; quem cria a janela a trata.
        self.conn = open_connection(db_path)
        self.setWindowTitle(WINDOW_TITLE)
        self.tabs = QTabWidget()
        organize_tab: OrganizeTab | None = None
        history_tab: HistoryTab | None = None
        for title, tab in build_tabs(self.conn, db_path):
            self.tabs.addTab(tab, title)
            if isinstance(tab, OrganizeTab):
                organize_tab = tab
                tab.organizing_changed.connect(self._set_organizing)
            elif isinstance(tab, HistoryTab):
                history_tab = tab
        if organize_tab is not None and history_tab is not None:
            organize_tab.organization_finished.connect(history_tab.on_organization_finished)
            organize_tab.details_requested.connect(partial(self._open_history, history_tab))
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

    def _set_organizing(self, organizing: bool) -> None:
        self.organizing = organizing

    def _open_history(self, history_tab: HistoryTab, organization_id: int) -> None:
        """Abre a aba Histórico na organizacao pedida ("Ver detalhes", 7.2)."""
        self.tabs.setCurrentWidget(history_tab)
        history_tab.show_organization(organization_id)

    def _on_tab_changed(self, index: int) -> None:
        if index not in _RELOAD_ON_FOCUS:
            return
        tab = self.tabs.widget(index)
        if isinstance(tab, Reloadable):
            tab.reload()

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802 - nome do Qt
        if self.organizing:
            QMessageBox.information(self, WINDOW_TITLE, _CLOSE_BLOCKED)
            event.ignore()
            return
        self.conn.close()
        if self._lock is not None:
            self._lock.unlock()
        event.accept()
