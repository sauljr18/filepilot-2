import sqlite3
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui.organize_tab import OrganizeTab

_original_resolve = Path.resolve


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _tab(qtbot: QtBot, conn: sqlite3.Connection) -> OrganizeTab:
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)
    return tab


def _pick(monkeypatch: pytest.MonkeyPatch, chosen: Path | str) -> None:
    """Troca o seletor de pasta por um dublê que devolve `chosen`."""
    monkeypatch.setattr(
        organize_tab_module.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(chosen),
    )


def _folder_with(tmp_path: Path, *names: str) -> Path:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
    return folder


def _fail_resolve_for(target: Path, error: Exception) -> Callable[..., Path]:
    def fake_resolve(self: Path, strict: bool = False) -> Path:
        if self == target:
            raise error
        return _original_resolve(self, strict=strict)

    return fake_resolve


def test_laco_no_destino_do_plano_leva_a_aba_ao_modo_erro(
    qtbot: QtBot, conn: sqlite3.Connection, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    _pick(monkeypatch, folder)
    target = folder / "Documentos" / "a.pdf"
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(target, RuntimeError("Symlink loop")))
    tab = _tab(qtbot, conn)

    tab.choose_folder()

    assert tab.mode == "erro"
    assert tab.summary.text() == "A pasta escolhida não existe ou não é uma pasta."
