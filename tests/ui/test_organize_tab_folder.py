import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.models import ScannedFile
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui.main_window import build_tabs
from filepilot.ui.organize_tab import OrganizeTab


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


def test_sem_pasta_mostra_o_convite_e_desabilita_as_acoes(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = _tab(qtbot, conn)

    assert tab.mode == "vazio"
    assert tab.summary.text() == "Escolha uma pasta para começar."
    assert not tab.simulate_button.isEnabled()
    assert not tab.organize_button.isEnabled()
    assert not tab.refresh_button.isEnabled()
    assert tab.choose_button.isEnabled()
    assert tab.table.model.rowCount() == 0


def test_escolher_pasta_com_cinco_arquivos_lista_todos(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf", "b.png", "c.mp4", "d.zip", "e.exe")
    tab = _tab(qtbot, conn)
    _pick(monkeypatch, folder)

    tab.choose_button.click()

    assert tab.mode == "listado"
    assert tab.summary.text() == "5 arquivos na pasta"
    assert tab.table.model.rowCount() == 5
    assert tab.folder == folder
    assert tab.folder_edit.text() == str(folder)
    assert tab.simulate_button.isEnabled()
    assert tab.organize_button.isEnabled()
    assert tab.refresh_button.isEnabled()


def test_em_listado_a_tabela_mostra_a_categoria_sem_destino(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _tab(qtbot, conn)
    _pick(monkeypatch, folder)

    tab.choose_button.click()

    model = tab.table.model
    assert model.data(model.index(0, 2)) == "Documentos"
    assert model.data(model.index(0, 3)) == ""


@pytest.mark.parametrize(
    ("code", "message"),
    [
        ("PASTA_VAZIA", "A pasta escolhida não tem arquivos para organizar."),
        ("PASTA_INVALIDA", "A pasta escolhida não existe ou não é uma pasta."),
        ("PASTA_ILEGIVEL", "Não foi possível ler a pasta escolhida."),
        (
            "PASTA_PROTEGIDA",
            "Esta pasta é protegida e não pode ser organizada. Escolha outra pasta.",
        ),
    ],
)
def test_erros_da_pasta_viram_modo_erro_com_a_mensagem(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    code: str,
    message: str,
) -> None:
    folder = tmp_path / "entrada"
    folder.mkdir()
    chosen = folder
    if code == "PASTA_INVALIDA":
        chosen = tmp_path / "nao-existe"
    elif code == "PASTA_ILEGIVEL":
        (folder / "a.pdf").write_bytes(b"x")

        def unreadable(self: Path) -> Iterator[Path]:
            raise PermissionError("sem acesso")

        monkeypatch.setattr(Path, "iterdir", unreadable)
    elif code == "PASTA_PROTEGIDA":
        monkeypatch.setenv("SystemRoot", str(folder))
    tab = _tab(qtbot, conn)
    _pick(monkeypatch, chosen)

    tab.choose_button.click()

    assert tab.mode == "erro"
    assert tab.summary.text() == message
    assert tab.table.model.rowCount() == 0
    assert not tab.simulate_button.isEnabled()
    assert not tab.organize_button.isEnabled()


def test_erro_deixa_atualizar_habilitado_e_se_recupera_quando_a_pasta_muda(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = tmp_path / "entrada"
    folder.mkdir()
    tab = _tab(qtbot, conn)
    _pick(monkeypatch, folder)
    tab.choose_button.click()
    assert tab.mode == "erro"
    assert tab.refresh_button.isEnabled()

    (folder / "a.pdf").write_bytes(b"x")
    tab.refresh_button.click()

    assert tab.mode == "listado"
    assert tab.summary.text() == "1 arquivos na pasta"


def test_cancelar_o_seletor_mantem_tudo_como_estava(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf", "b.png")
    tab = _tab(qtbot, conn)
    _pick(monkeypatch, folder)
    tab.choose_button.click()
    files_before = list(tab.files)

    _pick(monkeypatch, "")
    tab.choose_button.click()

    assert tab.mode == "listado"
    assert tab.folder == folder
    assert tab.folder_edit.text() == str(folder)
    assert tab.summary.text() == "2 arquivos na pasta"
    assert tab.files == files_before
    assert tab.table.model.rowCount() == 2


def test_cancelar_sem_pasta_continua_em_vazio(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab(qtbot, conn)
    _pick(monkeypatch, "")

    tab.choose_button.click()

    assert tab.mode == "vazio"
    assert tab.folder is None
    assert tab.summary.text() == "Escolha uma pasta para começar."


def test_a_leitura_passa_por_carregando_com_o_rotulo(
    qtbot: QtBot,
    conn: sqlite3.Connection,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "a.pdf")
    tab = _tab(qtbot, conn)
    seen: list[tuple[str, str, bool]] = []
    real_scan = organize_tab_module.scan_folder

    def spy(path: Path) -> list[ScannedFile]:
        seen.append((tab.mode, tab.summary.text(), tab.choose_button.isEnabled()))
        return real_scan(path)

    monkeypatch.setattr(organize_tab_module, "scan_folder", spy)
    _pick(monkeypatch, folder)

    tab.choose_button.click()

    assert seen == [("carregando", "Lendo a pasta...", False)]
    assert tab.mode == "listado"


def test_build_tabs_troca_o_marcador_de_organizar_pela_aba_real(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tabs = build_tabs(conn)
    for _, widget in tabs:
        qtbot.addWidget(widget)

    assert [title for title, _ in tabs] == ["Organizar", "Histórico", "Regras"]
    assert isinstance(tabs[0][1], OrganizeTab)
    assert not isinstance(tabs[1][1], OrganizeTab)
