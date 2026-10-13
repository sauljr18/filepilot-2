import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QLockFile
from PySide6.QtWidgets import QApplication, QMessageBox
from pytestqt.qtbot import QtBot

from filepilot import __main__ as app_main
from filepilot.db.connection import open_connection
from filepilot.ui.organize_tab import OrganizeTab

UNEXPECTED_DIALOG = "caixa de dialogo inesperada"


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


class _LockedByOther:
    """QLockFile falso: a trava esta com outra instancia."""

    def __init__(self, path: str) -> None:
        pass

    def setStaleLockTime(self, ms: int) -> None:
        pass

    def tryLock(self, timeout: int = 0) -> bool:
        return False

    def error(self) -> QLockFile.LockError:
        return QLockFile.LockError.LockFailedError

    def unlock(self) -> None:
        pass


class _Spy:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, parent: object, title: str, text: str) -> None:
        self.messages.append(text)


def test_caixa_de_dialogo_real_levanta_em_vez_de_bloquear(qapp: QApplication) -> None:
    with pytest.raises(AssertionError, match=UNEXPECTED_DIALOG):
        QMessageBox.critical(None, "t", "x")


@pytest.mark.parametrize("name", ["information", "warning", "critical", "question"])
def test_os_quatro_dialogos_modais_estao_proibidos(
    qapp: QApplication, name: str
) -> None:
    with pytest.raises(AssertionError, match=rf"{UNEXPECTED_DIALOG} \({name}\): t: x"):
        getattr(QMessageBox, name)(None, "t", "x")


def test_open_main_window_sem_espiao_levanta(
    qapp: QApplication, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(app_main, "QLockFile", _LockedByOther)

    with pytest.raises(AssertionError, match=UNEXPECTED_DIALOG):
        app_main.open_main_window(tmp_path)


def test_on_failed_sem_espiao_levanta(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)

    with pytest.raises(AssertionError, match=UNEXPECTED_DIALOG):
        tab._on_failed("ERRO_INTERNO", "x")


def test_espiao_com_monkeypatch_recebe_a_chamada_e_nao_levanta(
    qapp: QApplication, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = _Spy()
    monkeypatch.setattr(QMessageBox, "critical", spy)

    QMessageBox.critical(None, "t", "x")

    assert spy.messages == ["x"]
