"""Janela principal do FilePilot (SPEC 7.1)."""

import sqlite3
from pathlib import Path
from typing import Protocol, runtime_checkable

from PySide6.QtCore import QLockFile
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QMainWindow, QMessageBox, QTabWidget, QWidget

from filepilot.db.connection import open_connection

WINDOW_TITLE = "FilePilot"
TAB_TITLES = ("Organizar", "Histórico", "Regras")
_CLOSE_BLOCKED = "Aguarde a organização terminar para fechar."
# Indices das abas que recarregam os dados ao receberem o foco (7.1).
_RELOAD_ON_FOCUS = (1, 2)


@runtime_checkable
class Reloadable(Protocol):
    """Aba que sabe recarregar os proprios dados."""

    def reload(self) -> None: ...


class PlaceholderTab(QWidget):
    """Marcador de posicao: os itens seguintes trocam cada um pela aba real."""

    def reload(self) -> None:
        """Sem dados a recarregar."""


def build_tabs(conn: sqlite3.Connection) -> list[tuple[str, QWidget]]:
    """Cria as abas na ordem Organizar, Histórico e Regras.

    Os itens filepilot-v1-9, filepilot-v1-11 e filepilot-v1-12 trocam cada
    marcador pela aba real, que recebe a mesma conexao da janela.
    """
    del conn  # as abas reais vao usa-la; os marcadores nao
    return [(title, PlaceholderTab()) for title in TAB_TITLES]


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
        for title, tab in build_tabs(self.conn):
            self.tabs.addTab(tab, title)
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

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
