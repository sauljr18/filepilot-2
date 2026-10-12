import sys
from pathlib import Path

import pytest
from PySide6.QtCore import QLockFile

from filepilot import __main__ as app_main

_LOCK_UNAVAILABLE = (
    "Não foi possível verificar se o FilePilot já está aberto. "
    "Confira se você tem permissão para usar a pasta de dados do aplicativo."
)
_ALREADY_OPEN = "O FilePilot já está aberto."


class MessageSpy:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, parent: object, title: str, text: str) -> None:
        self.messages.append(text)


@pytest.fixture
def info_spy(monkeypatch: pytest.MonkeyPatch) -> MessageSpy:
    spy = MessageSpy()
    monkeypatch.setattr(app_main.QMessageBox, "information", spy)
    return spy


@pytest.fixture
def critical_spy(monkeypatch: pytest.MonkeyPatch) -> MessageSpy:
    spy = MessageSpy()
    monkeypatch.setattr(app_main.QMessageBox, "critical", spy)
    return spy


def _forbid_window(monkeypatch: pytest.MonkeyPatch) -> None:
    def fail(*args: object, **kwargs: object) -> None:
        raise AssertionError("a janela nao deve ser criada")

    monkeypatch.setattr(app_main, "MainWindow", fail)


def _fake_lock(
    monkeypatch: pytest.MonkeyPatch, error: QLockFile.LockError
) -> list[str]:
    calls: list[str] = []

    class FakeLock:
        def __init__(self, path: str) -> None:
            calls.append("init")

        def setStaleLockTime(self, ms: int) -> None:
            calls.append("setStaleLockTime")

        def tryLock(self, timeout: int = 0) -> bool:
            calls.append("tryLock")
            return False

        def error(self) -> QLockFile.LockError:
            calls.append("error")
            return error

        def unlock(self) -> None:
            calls.append("unlock")

    monkeypatch.setattr(app_main, "QLockFile", FakeLock)
    return calls


@pytest.mark.parametrize(
    "error",
    [QLockFile.LockError.PermissionError, QLockFile.LockError.UnknownError],
)
def test_falha_que_nao_e_outra_instancia_vira_erro_de_acesso(
    tmp_path: Path,
    info_spy: MessageSpy,
    critical_spy: MessageSpy,
    monkeypatch: pytest.MonkeyPatch,
    error: QLockFile.LockError,
) -> None:
    _forbid_window(monkeypatch)
    calls = _fake_lock(monkeypatch, error)

    result = app_main.open_main_window(tmp_path)

    assert result == 1
    assert critical_spy.messages == [_LOCK_UNAVAILABLE]
    assert info_spy.messages == []
    assert calls.count("error") == 1
    assert "unlock" not in calls
    assert not (tmp_path / "filepilot.db").exists()


def test_lock_failed_error_continua_avisando_que_ja_esta_aberto(
    tmp_path: Path,
    info_spy: MessageSpy,
    critical_spy: MessageSpy,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _forbid_window(monkeypatch)
    calls = _fake_lock(monkeypatch, QLockFile.LockError.LockFailedError)

    result = app_main.open_main_window(tmp_path)

    assert result == 0
    assert info_spy.messages == [_ALREADY_OPEN]
    assert critical_spy.messages == []
    assert "unlock" not in calls
    assert not (tmp_path / "filepilot.db").exists()


@pytest.mark.skipif(sys.platform == "win32", reason="chmod nao vale no Windows")
def test_pasta_sem_permissao_de_escrita_vira_erro_de_acesso(
    tmp_path: Path,
    info_spy: MessageSpy,
    critical_spy: MessageSpy,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _forbid_window(monkeypatch)
    tmp_path.chmod(0o500)
    try:
        probe = QLockFile(str(tmp_path / "filepilot.lock"))
        if probe.tryLock(0):
            probe.unlock()
            pytest.skip("a permissao da pasta e ignorada neste ambiente")

        result = app_main.open_main_window(tmp_path)
    finally:
        tmp_path.chmod(0o700)

    assert result == 1
    assert critical_spy.messages == [_LOCK_UNAVAILABLE]
    assert info_spy.messages == []
    assert not (tmp_path / "filepilot.db").exists()
