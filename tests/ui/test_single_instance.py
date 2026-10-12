import subprocess
import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QLockFile
from pytestqt.qtbot import QtBot

from filepilot import __main__ as app_main
from filepilot.ui.main_window import MainWindow

_HOLD_LOCK = (
    "import sys, time\n"
    "from PySide6.QtCore import QLockFile\n"
    "lock = QLockFile(sys.argv[1])\n"
    "assert lock.tryLock(0)\n"
    "print('locked', flush=True)\n"
    "time.sleep(60)\n"
)


class InfoSpy:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, parent: object, title: str, text: str) -> None:
        self.messages.append(text)


@pytest.fixture
def info_spy(monkeypatch: pytest.MonkeyPatch) -> InfoSpy:
    spy = InfoSpy()
    monkeypatch.setattr(app_main.QMessageBox, "information", spy)
    return spy


def _forbid_window(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("a janela nao deve ser criada")

    monkeypatch.setattr(app_main, "MainWindow", fail)


def test_trava_tomada_mostra_aviso_e_termina_com_zero(
    tmp_path: Path, info_spy: InfoSpy, monkeypatch: pytest.MonkeyPatch
) -> None:
    _forbid_window(monkeypatch)
    other = QLockFile(str(tmp_path / "filepilot.lock"))
    assert other.tryLock(0)
    try:
        result = app_main.open_main_window(tmp_path)
    finally:
        other.unlock()

    assert result == 0
    assert info_spy.messages == ["O FilePilot já está aberto."]


def test_trava_tomada_nao_abre_o_banco(
    tmp_path: Path, info_spy: InfoSpy, monkeypatch: pytest.MonkeyPatch
) -> None:
    _forbid_window(monkeypatch)
    other = QLockFile(str(tmp_path / "filepilot.lock"))
    assert other.tryLock(0)
    try:
        app_main.open_main_window(tmp_path)
    finally:
        other.unlock()

    assert not (tmp_path / "filepilot.db").exists()


def test_pasta_de_dados_inexistente_e_criada_antes_da_trava(
    qtbot: QtBot, tmp_path: Path
) -> None:
    data_dir = tmp_path / "novo" / "FilePilot"

    window = app_main.open_main_window(data_dir)

    assert isinstance(window, MainWindow)
    qtbot.addWidget(window)
    assert (data_dir / "filepilot.lock").exists()
    window.close()


def test_trava_e_liberada_no_close_event(qtbot: QtBot, tmp_path: Path) -> None:
    window = app_main.open_main_window(tmp_path)
    assert isinstance(window, MainWindow)
    qtbot.addWidget(window)
    probe = QLockFile(str(tmp_path / "filepilot.lock"))
    assert not probe.tryLock(0)

    window.close()

    assert probe.tryLock(0)
    probe.unlock()


def test_define_o_tempo_de_trava_velha(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    created: list[QLockFile] = []

    class RecordingLock(QLockFile):
        def __init__(self, path: str) -> None:
            super().__init__(path)
            created.append(self)

    monkeypatch.setattr(app_main, "QLockFile", RecordingLock)

    window = app_main.open_main_window(tmp_path)

    assert isinstance(window, MainWindow)
    qtbot.addWidget(window)
    assert [lock.staleLockTime() for lock in created] == [30_000]
    window.close()


def test_trava_velha_de_processo_que_caiu_e_recuperada(
    qtbot: QtBot, tmp_path: Path
) -> None:
    lock_path = tmp_path / "filepilot.lock"
    holder = subprocess.Popen(
        [sys.executable, "-I", "-c", _HOLD_LOCK, str(lock_path)],
        stdout=subprocess.PIPE,
        text=True,
    )
    try:
        assert holder.stdout is not None
        assert holder.stdout.readline().strip() == "locked"
        holder.kill()
        holder.wait(timeout=10)
    finally:
        if holder.poll() is None:
            holder.kill()
            holder.wait(timeout=10)
        if holder.stdout is not None:
            holder.stdout.close()
    assert lock_path.exists()

    window = app_main.open_main_window(tmp_path)

    assert isinstance(window, MainWindow)
    qtbot.addWidget(window)
    window.close()
