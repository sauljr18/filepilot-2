import sqlite3
from pathlib import Path

import pytest
from PySide6.QtCore import QLockFile
from pytestqt.qtbot import QtBot

from filepilot import __main__ as app_main
from filepilot.domain.errors import FilePilotError
from filepilot.ui import main_window as main_window_module
from filepilot.ui.main_window import MainWindow

DB_ERROR = "Não foi possível acessar o histórico do FilePilot."
CLOSE_BLOCKED = "Aguarde a organização terminar para fechar."


class MessageSpy:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, parent: object, title: str, text: str) -> None:
        self.messages.append(text)


def _locked_window(qtbot: QtBot, tmp_path: Path) -> tuple[MainWindow, QLockFile]:
    lock = QLockFile(str(tmp_path / "filepilot.lock"))
    assert lock.tryLock(0)
    window = MainWindow(tmp_path / "filepilot.db", lock)
    qtbot.addWidget(window)
    return window, lock


def test_fechar_durante_organizacao_e_ignorado_com_aviso(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = MessageSpy()
    monkeypatch.setattr(main_window_module.QMessageBox, "information", spy)
    window, lock = _locked_window(qtbot, tmp_path)
    window.show()
    window.organizing = True

    closed = window.close()

    assert closed is False
    assert window.isVisible()
    assert spy.messages == [CLOSE_BLOCKED]
    assert lock.isLocked()
    assert window.conn.execute("SELECT 1").fetchone() == (1,)
    window.organizing = False
    window.close()


def test_fechar_sem_organizacao_fecha_conexao_e_libera_a_trava(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = MessageSpy()
    monkeypatch.setattr(main_window_module.QMessageBox, "information", spy)
    window, lock = _locked_window(qtbot, tmp_path)
    window.show()

    closed = window.close()

    assert closed is True
    assert spy.messages == []
    assert not lock.isLocked()
    with pytest.raises(sqlite3.ProgrammingError):
        window.conn.execute("SELECT 1")


def test_falha_em_open_connection_mostra_erro_critico_e_sai_com_um(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    critical = MessageSpy()

    def broken(db_path: Path) -> sqlite3.Connection:
        raise FilePilotError("BANCO_INDISPONIVEL", DB_ERROR)

    monkeypatch.setattr(main_window_module, "open_connection", broken)
    monkeypatch.setattr(app_main.QMessageBox, "critical", critical)

    result = app_main.open_main_window(tmp_path)

    assert result == 1
    assert critical.messages == [DB_ERROR]


def test_falha_em_open_connection_libera_a_trava(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def broken(db_path: Path) -> sqlite3.Connection:
        raise FilePilotError("BANCO_INDISPONIVEL", DB_ERROR)

    monkeypatch.setattr(main_window_module, "open_connection", broken)
    monkeypatch.setattr(app_main.QMessageBox, "critical", MessageSpy())
    app_main.open_main_window(tmp_path)

    probe = QLockFile(str(tmp_path / "filepilot.lock"))

    assert probe.tryLock(0)
    probe.unlock()


def test_banco_real_inacessivel_sai_com_um(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    critical = MessageSpy()
    monkeypatch.setattr(app_main.QMessageBox, "critical", critical)
    (tmp_path / "filepilot.db").mkdir()

    result = app_main.open_main_window(tmp_path)

    assert result == 1
    assert critical.messages == [DB_ERROR]


def test_pasta_de_dados_impossivel_de_criar_sai_com_um(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    critical = MessageSpy()
    monkeypatch.setattr(app_main.QMessageBox, "critical", critical)
    blocker = tmp_path / "arquivo"
    blocker.write_text("x", encoding="utf-8")

    result = app_main.open_main_window(blocker / "FilePilot")

    assert result == 1
    assert critical.messages == [DB_ERROR]
