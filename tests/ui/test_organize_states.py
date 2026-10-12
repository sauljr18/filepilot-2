import sqlite3
import threading
from collections.abc import Callable
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import OrganizationResult, Plan
from filepilot.ui import main_window as main_window_module
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui import organize_worker as organize_worker_module
from filepilot.ui.main_window import MainWindow
from filepilot.ui.organize_tab import MODE_ERROR, MODE_LISTED, MODE_ORGANIZING, OrganizeTab

RAW_TEXT = "RAW-INTERNAL-DETAIL"
UNEXPECTED = "Ocorreu um erro inesperado. Tente de novo."
CLOSE_BLOCKED = "Aguarde a organização terminar para fechar."


class MessageSpy:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, parent: object, title: str, text: str) -> None:
        self.messages.append(text)


def _window(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, folder: Path
) -> tuple[MainWindow, OrganizeTab]:
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
    return window, tab


def _folder_with(tmp_path: Path, *names: str) -> Path:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
    return folder


def _buttons(tab: OrganizeTab) -> list[bool]:
    return [
        tab.simulate_button.isEnabled(),
        tab.organize_button.isEnabled(),
        tab.refresh_button.isEnabled(),
        tab.choose_button.isEnabled(),
    ]


def _fail_with(monkeypatch: pytest.MonkeyPatch, error: Exception) -> None:
    def failing(*args: object, **kwargs: object) -> OrganizationResult:
        raise error

    monkeypatch.setattr(organize_worker_module, "organize", failing)


def _organize_until_back(qtbot: QtBot, window: MainWindow, tab: OrganizeTab) -> None:
    with qtbot.waitSignal(
        tab.organizing_changed, timeout=5000, check_params_cb=lambda value: value is False
    ):
        tab.organize_button.click()
    assert window.organizing is False


def test_durante_a_organizacao_os_botoes_ficam_desabilitados_e_a_janela_bloqueia(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = MessageSpy()
    monkeypatch.setattr(main_window_module.QMessageBox, "information", spy)
    folder = _folder_with(tmp_path, "foto.jpg")
    window, tab = _window(qtbot, tmp_path, monkeypatch, folder)
    window.show()
    assert window.organizing is False
    assert _buttons(tab) == [True, True, True, True]
    release = threading.Event()
    real_organize = organize_worker_module.organize

    def slow(
        plan: Plan,
        conn: sqlite3.Connection,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> OrganizationResult:
        assert release.wait(5)
        # Chega arquivo novo no meio: depois de organizar sobra uma operacao.
        (folder / "nota.pdf").write_bytes(b"x")
        return real_organize(plan, conn, progress_callback)

    monkeypatch.setattr(organize_worker_module, "organize", slow)

    tab.organize_button.click()

    assert tab.mode == MODE_ORGANIZING
    assert window.organizing is True
    assert _buttons(tab) == [False, False, False, False]
    assert window.close() is False
    assert spy.messages == [CLOSE_BLOCKED]
    assert window.isVisible()

    with qtbot.waitSignal(tab.organization_finished, timeout=5000):
        release.set()

    assert window.organizing is False
    assert tab.mode == MODE_LISTED
    assert _buttons(tab) == [True, True, True, True]
    window.close()


def test_falha_de_contrato_mostra_a_mensagem_e_vai_para_erro(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = MessageSpy()
    monkeypatch.setattr(organize_tab_module.QMessageBox, "critical", spy)
    folder = _folder_with(tmp_path, "foto.jpg")
    window, tab = _window(qtbot, tmp_path, monkeypatch, folder)
    window.show()
    message = "Não foi possível acessar o histórico do FilePilot."
    _fail_with(monkeypatch, FilePilotError("BANCO_INDISPONIVEL", message))

    _organize_until_back(qtbot, window, tab)

    assert spy.messages == [message]
    assert tab.mode == MODE_ERROR
    assert tab.summary.text() == message
    assert window.isVisible()
    assert tab.refresh_button.isEnabled()
    assert tab.choose_button.isEnabled()
    assert tab.simulate_button.isEnabled() is False
    assert tab.organize_button.isEnabled() is False
    window.close()


def test_excecao_inesperada_mostra_o_texto_generico_e_a_janela_continua_aberta(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = MessageSpy()
    monkeypatch.setattr(organize_tab_module.QMessageBox, "critical", spy)
    folder = _folder_with(tmp_path, "foto.jpg")
    window, tab = _window(qtbot, tmp_path, monkeypatch, folder)
    window.show()
    _fail_with(monkeypatch, RuntimeError(RAW_TEXT))

    _organize_until_back(qtbot, window, tab)

    assert spy.messages == [UNEXPECTED]
    assert RAW_TEXT not in spy.messages[0]
    assert RAW_TEXT not in tab.summary.text()
    assert tab.mode == MODE_ERROR
    assert window.isVisible()
    window.close()


def test_depois_do_erro_atualizar_volta_a_listar_a_pasta(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = MessageSpy()
    monkeypatch.setattr(organize_tab_module.QMessageBox, "critical", spy)
    folder = _folder_with(tmp_path, "foto.jpg")
    window, tab = _window(qtbot, tmp_path, monkeypatch, folder)
    _fail_with(monkeypatch, RuntimeError(RAW_TEXT))
    _organize_until_back(qtbot, window, tab)

    tab.refresh_button.click()

    assert tab.mode == MODE_LISTED
    assert tab.organize_button.isEnabled()
    window.close()


def test_aba_sem_caminho_do_banco_mostra_banco_indisponivel_e_nao_organiza(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = MessageSpy()
    monkeypatch.setattr(organize_tab_module.QMessageBox, "critical", spy)
    folder = _folder_with(tmp_path, "foto.jpg")
    conn = open_connection(tmp_path / "db" / "filepilot.db")
    try:
        tab = OrganizeTab(conn)
        qtbot.addWidget(tab)
        monkeypatch.setattr(
            organize_tab_module.QFileDialog,
            "getExistingDirectory",
            lambda *args, **kwargs: str(folder),
        )
        tab.choose_button.click()

        tab.organize_button.click()

        message = "Não foi possível acessar o histórico do FilePilot."
        assert spy.messages == [message]
        assert tab.mode == MODE_ERROR
        assert tab.summary.text() == message
        assert tab._thread is None
        assert (folder / "foto.jpg").exists()
        assert conn.execute("SELECT COUNT(*) FROM organizations").fetchone() == (0,)
    finally:
        conn.close()
