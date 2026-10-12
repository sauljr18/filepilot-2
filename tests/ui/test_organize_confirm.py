import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.services.rules import create_rule
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui.organize_tab import MODE_LISTED, MODE_SIMULATED, OrganizeTab

CHANGED = (
    "A pasta mudou desde a simulação. "
    "Confira a nova simulação e clique em Organizar de novo."
)
NO_OPERATIONS = "Não há operações para executar."


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _folder_with(tmp_path: Path, *names: str) -> Path:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
    return folder


def _open_tab(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
    folder: Path,
) -> OrganizeTab:
    # A fixture `conn` abre o banco em `tmp_path/db`; a pasta fica em `tmp_path`.
    tab = OrganizeTab(conn, folder.parent / "db" / "filepilot.db")
    qtbot.addWidget(tab)
    monkeypatch.setattr(
        organize_tab_module.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(folder),
    )
    tab.choose_button.click()
    return tab


def _names(folder: Path) -> list[str]:
    return sorted(item.name for item in folder.iterdir() if item.is_file())


def _organize(qtbot: QtBot, tab: OrganizeTab) -> int:
    with qtbot.waitSignal(tab.organization_finished, timeout=5000) as blocker:
        tab.organize_button.click()
    return int(blocker.args[0])


def test_pasta_mudou_depois_da_simulacao_nao_move_nada(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    tab.simulate_button.click()
    (folder / "nota.pdf").write_bytes(b"x")

    tab.organize_button.click()

    assert _names(folder) == ["foto.jpg", "nota.pdf"]
    assert tab.mode == MODE_SIMULATED
    assert tab.summary.text() == CHANGED
    assert tab.table.model.rowCount() == 2
    assert tab._thread is None
    assert conn.execute("SELECT COUNT(*) FROM organizations").fetchone() == (0,)


def test_depois_do_aviso_a_pessoa_organiza_de_novo(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    tab.simulate_button.click()
    (folder / "nota.pdf").write_bytes(b"x")
    tab.organize_button.click()
    assert tab.summary.text() == CHANGED

    _organize(qtbot, tab)

    assert _names(folder) == []
    assert tab.summary.text() == "Concluído: 2 movidos, 0 falhas."


def test_regra_alterada_depois_da_simulacao_tambem_e_mudanca(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "contrato.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    tab.simulate_button.click()
    create_rule(conn, "Contratos", ["pdf"], "Juridico")

    tab.organize_button.click()

    assert _names(folder) == ["contrato.pdf"]
    assert tab.summary.text() == CHANGED
    assert tab.mode == MODE_SIMULATED


def test_simulacao_igual_ao_plano_novo_executa(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg", "nota.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    tab.simulate_button.click()
    assert tab.mode == MODE_SIMULATED

    _organize(qtbot, tab)

    assert _names(folder) == []
    assert tab.mode == MODE_LISTED


def test_sem_simulacao_le_a_pasta_e_move_o_arquivo_novo(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    (folder / "nota.pdf").write_bytes(b"x")

    _organize(qtbot, tab)

    assert tab.summary.text() == "Concluído: 2 movidos, 0 falhas."
    assert _names(folder) == []
    moved = conn.execute("SELECT COUNT(*) FROM operations").fetchone()
    assert moved == (2,)


def test_plano_recalculado_vazio_depois_da_simulacao_nao_executa(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg", "sem-categoria.zzz")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    tab.simulate_button.click()
    (folder / "foto.jpg").unlink()

    tab.organize_button.click()

    assert tab.summary.text() == NO_OPERATIONS
    assert tab.organize_button.isEnabled() is False
    assert tab._thread is None
    assert conn.execute("SELECT COUNT(*) FROM organizations").fetchone() == (0,)


def test_plano_recalculado_vazio_sem_simulacao_nao_executa(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg", "sem-categoria.zzz")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    (folder / "foto.jpg").unlink()

    tab.organize_button.click()

    assert tab.mode == MODE_LISTED
    assert tab.summary.text() == NO_OPERATIONS
    assert tab.organize_button.isEnabled() is False
    assert tab._thread is None
    assert _names(folder) == ["sem-categoria.zzz"]
