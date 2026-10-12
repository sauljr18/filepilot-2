import sqlite3
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.models import ScannedFile
from filepilot.services import scanner
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui.organize_tab import OrganizeTab

UNREADABLE_MESSAGE = "Não foi possível ler a pasta escolhida."

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


def _fail_scan(monkeypatch: pytest.MonkeyPatch, error: OSError) -> None:
    def failing(path: Path) -> list[ScannedFile]:
        raise error

    monkeypatch.setattr(organize_tab_module, "scan_folder", failing)


def _fail_resolve_for(target: Path, error: Exception) -> Callable[..., Path]:
    def fake_resolve(self: Path, strict: bool = False) -> Path:
        if self == target:
            raise error
        return _original_resolve(self, strict=strict)

    return fake_resolve


def _assert_read_error_state(tab: OrganizeTab) -> None:
    assert tab.mode == "erro"
    assert tab.summary.text() == UNREADABLE_MESSAGE
    assert tab.table.model.rowCount() == 0
    assert tab.files == []
    assert tab.plan is None
    assert not tab.simulate_button.isEnabled()
    assert not tab.organize_button.isEnabled()
    assert tab.choose_button.isEnabled()
    assert tab.refresh_button.isEnabled()


def test_oserror_na_leitura_da_pasta_leva_a_aba_ao_estado_de_erro(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _tab(qtbot, conn)
    _fail_scan(monkeypatch, PermissionError("acesso negado"))
    _pick(monkeypatch, folder)

    tab.choose_folder()

    _assert_read_error_state(tab)


def test_a_mensagem_de_erro_nao_traz_o_texto_bruto_da_excecao(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _tab(qtbot, conn)
    _fail_scan(monkeypatch, PermissionError("acesso negado"))
    _pick(monkeypatch, folder)

    tab.choose_folder()

    assert "acesso negado" not in tab.summary.text()


def test_simular_com_oserror_depois_de_listar_leva_ao_estado_de_erro(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf", "b.png")
    tab = _tab(qtbot, conn)
    _pick(monkeypatch, folder)
    tab.choose_folder()
    assert tab.mode == "listado"
    _fail_scan(monkeypatch, OSError("falha do sistema"))

    tab.simulate()

    _assert_read_error_state(tab)


def test_atualizar_depois_do_erro_recupera_a_aba(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf", "b.png")
    tab = _tab(qtbot, conn)
    real_scan = organize_tab_module.scan_folder
    _fail_scan(monkeypatch, PermissionError("acesso negado"))
    _pick(monkeypatch, folder)
    tab.choose_folder()
    assert tab.mode == "erro"
    monkeypatch.setattr(organize_tab_module, "scan_folder", real_scan)

    tab.refresh()

    assert tab.mode == "listado"
    assert tab.summary.text() == "2 arquivos na pasta"
    assert len(tab.files) == 2


def test_permission_error_do_resolve_sem_trocar_o_servico_leva_a_erro(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _tab(qtbot, conn)
    monkeypatch.setattr(
        Path, "resolve", _fail_resolve_for(folder, PermissionError("acesso negado"))
    )
    _pick(monkeypatch, folder)

    tab.choose_folder()

    _assert_read_error_state(tab)


def test_o_texto_da_interface_e_o_de_pasta_ilegivel_do_scanner() -> None:
    assert organize_tab_module._UNREADABLE == scanner._MESSAGES["PASTA_ILEGIVEL"]
