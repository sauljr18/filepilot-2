import subprocess
import sys

import pytest

import filepilot
from filepilot import __main__ as app_main


def _forbidden(*args: object) -> object:
    raise AssertionError("caminho da interface chamado com --version")


class FakeApplication:
    created = 0

    def __init__(self, argv: list[str]) -> None:
        type(self).created += 1

    def setApplicationName(self, name: str) -> None:
        pass


class FakeOpenMainWindow:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, data_dir: object) -> int:
        self.calls += 1
        return 0


def _forbid_interface(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(app_main, "QApplication", _forbidden)
    monkeypatch.setattr(app_main, "default_data_dir", _forbidden)
    monkeypatch.setattr(app_main, "open_main_window", _forbidden)


def test_version_em_subprocesso_imprime_a_versao() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "filepilot", "--version"],
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert completed.returncode == 0
    assert completed.stdout == filepilot.__version__ + "\n"
    assert completed.stderr == ""


def test_version_em_processo_nao_abre_a_interface(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["filepilot", "--version"])
    _forbid_interface(monkeypatch)

    assert app_main.main() == 0
    assert capsys.readouterr().out == filepilot.__version__ + "\n"


@pytest.mark.parametrize(
    "argv", [["filepilot"], ["filepilot", "--version", "x"]], ids=["sem", "extra"]
)
def test_outros_argumentos_seguem_o_caminho_de_hoje(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
) -> None:
    monkeypatch.setattr(sys, "argv", argv)
    monkeypatch.setattr(FakeApplication, "created", 0)
    monkeypatch.setattr(app_main, "QApplication", FakeApplication)
    open_window = FakeOpenMainWindow()
    monkeypatch.setattr(app_main, "open_main_window", open_window)

    assert app_main.main() == 0
    assert FakeApplication.created == 1
    assert open_window.calls == 1
    assert capsys.readouterr().out == ""


def test_version_sem_saida_padrao_devolve_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sys, "argv", ["filepilot", "--version"])
    monkeypatch.setattr(sys, "stdout", None)
    _forbid_interface(monkeypatch)

    assert app_main.main() == 0
