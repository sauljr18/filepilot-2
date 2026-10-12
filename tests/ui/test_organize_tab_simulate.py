import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.services.rules import create_rule, delete_rule
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui.organize_tab import OrganizeTab


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _open_tab(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
    folder: Path,
) -> OrganizeTab:
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)
    monkeypatch.setattr(
        organize_tab_module.QFileDialog,
        "getExistingDirectory",
        lambda *args, **kwargs: str(folder),
    )
    tab.choose_button.click()
    return tab


def _folder_with(tmp_path: Path, *names: str) -> Path:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
    return folder


def _tree(folder: Path) -> list[tuple[str, bool, int]]:
    return sorted(
        (str(item.relative_to(folder)), item.is_dir(), item.stat().st_size if item.is_file() else 0)
        for item in folder.rglob("*")
    )


def _cell(tab: OrganizeTab, row: int, column: int) -> str:
    model = tab.table.model
    return str(model.data(model.index(row, column)))


def test_simular_mostra_o_plano_e_nao_altera_a_pasta(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "fatura.pdf", "foto.png", "setup.exe")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    before = _tree(folder)

    tab.simulate_button.click()

    assert tab.mode == "simulado"
    assert tab.summary.text() == "Simulação: 2 operações. Nenhum arquivo foi alterado."
    assert _cell(tab, 0, 3) == str(Path("Documentos") / "fatura.pdf")
    assert _tree(folder) == before
    assert tab.organize_button.isEnabled()


def test_simular_nao_grava_no_historico(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "fatura.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)

    tab.simulate_button.click()

    assert conn.execute("SELECT COUNT(*) FROM organizations").fetchone() == (0,)
    assert conn.execute("SELECT COUNT(*) FROM operations").fetchone() == (0,)


def test_simular_usa_a_regra_criada_depois_da_escolha_da_pasta(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "contrato.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    assert _cell(tab, 0, 2) == "Documentos"
    create_rule(conn, "Contratos", ["pdf"], "Juridico")

    tab.simulate_button.click()

    assert _cell(tab, 0, 2) == "Regra personalizada"
    assert _cell(tab, 0, 4) == "Contratos"
    assert _cell(tab, 0, 3) == str(Path("Juridico") / "contrato.pdf")


def test_simular_usa_a_regra_excluida_depois_da_escolha_da_pasta(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    rule = create_rule(conn, "Contratos", ["pdf"], "Juridico")
    folder = _folder_with(tmp_path, "contrato.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    assert _cell(tab, 0, 2) == "Regra personalizada"
    delete_rule(conn, rule.id)

    tab.simulate_button.click()

    assert _cell(tab, 0, 2) == "Documentos"
    assert _cell(tab, 0, 4) == ""


def test_simular_ve_arquivo_novo_na_pasta(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    (folder / "b.png").write_bytes(b"x")

    tab.simulate_button.click()

    assert tab.table.model.rowCount() == 2
    assert tab.summary.text() == "Simulação: 2 operações. Nenhum arquivo foi alterado."


def test_plano_vazio_mostra_o_aviso_e_desabilita_organizar(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "setup.exe", "dados.bin")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    assert tab.summary.text() == "2 arquivos na pasta"
    assert not tab.organize_button.isEnabled()

    tab.simulate_button.click()

    assert tab.mode == "simulado"
    assert tab.summary.text() == "Não há operações para executar."
    assert not tab.organize_button.isEnabled()
    assert tab.simulate_button.isEnabled()


def test_simular_com_erro_na_pasta_vai_para_o_modo_erro(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    (folder / "a.pdf").unlink()

    tab.simulate_button.click()

    assert tab.mode == "erro"
    assert tab.summary.text() == "A pasta escolhida não tem arquivos para organizar."
    assert not tab.simulate_button.isEnabled()
    assert not tab.organize_button.isEnabled()


def test_atualizar_descarta_a_simulacao_e_le_a_pasta_de_novo(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    tab.simulate_button.click()
    assert tab.mode == "simulado"
    assert _cell(tab, 0, 3) == str(Path("Documentos") / "a.pdf")
    (folder / "b.png").write_bytes(b"x")

    tab.refresh_button.click()

    assert tab.mode == "listado"
    assert tab.summary.text() == "2 arquivos na pasta"
    assert tab.table.model.rowCount() == 2
    assert _cell(tab, 0, 3) == ""
    assert tab.plan is not None and len(tab.plan.operations) == 2


def test_atualizar_recalcula_o_plano_com_as_regras_atuais(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "contrato.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    create_rule(conn, "Contratos", ["pdf"], "Juridico")

    tab.refresh_button.click()

    assert _cell(tab, 0, 2) == "Regra personalizada"
    assert _cell(tab, 0, 4) == "Contratos"


def test_atualizar_so_fica_habilitado_com_pasta_escolhida(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)
    assert not tab.refresh_button.isEnabled()
    folder = _folder_with(tmp_path, "a.pdf")

    tab = _open_tab(qtbot, conn, monkeypatch, folder)

    assert tab.refresh_button.isEnabled()
    tab.mode = "organizando"
    tab._update_buttons()
    assert not tab.refresh_button.isEnabled()
    assert not tab.choose_button.isEnabled()
