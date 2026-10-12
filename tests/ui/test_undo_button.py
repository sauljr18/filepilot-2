import sqlite3
import threading
from contextlib import closing
from pathlib import Path

import pytest
from PySide6.QtCore import QObject
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.services.undo import UndoResult
from filepilot.ui import main_window as main_window_module
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui import organize_worker as organize_worker_module
from filepilot.ui.main_window import MainWindow
from filepilot.ui.organize_tab import MODE_LISTED, OrganizeTab

NOW = "2026-10-11T12:00:00Z"
DATABASE_UNAVAILABLE = "Não foi possível acessar o histórico do FilePilot."
NOTHING_TO_UNDO = "Não há organização para desfazer."
CLOSE_BLOCKED = "Aguarde a organização terminar para fechar."


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _add_organization(
    conn: sqlite3.Connection,
    status: str = "concluida",
    moved_count: int = 1,
    folder_path: str = "/outra-pasta",
    started_at: str = "2026-10-12T09:00:00Z",
) -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, moved_count, "
        "failed_count, created_at, updated_at) VALUES (?, ?, ?, ?, 0, ?, ?)",
        (folder_path, started_at, status, moved_count, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def _window(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, *names: str
) -> tuple[MainWindow, OrganizeTab, Path]:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
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
    return window, tab, folder


def _organize(qtbot: QtBot, tab: OrganizeTab) -> None:
    with qtbot.waitSignal(tab.organization_finished, timeout=5000):
        tab.organize()


def _undo(qtbot: QtBot, tab: OrganizeTab) -> None:
    with qtbot.waitSignal(
        tab.organizing_changed, timeout=5000, check_params_cb=lambda value: value is False
    ):
        tab.undo_button.click()


@pytest.mark.parametrize(
    ("status", "moved_count", "enabled"),
    [
        ("concluida", 3, True),
        ("interrompida", 1, True),
        ("desfeita", 3, False),
        ("em_andamento", 3, False),
        ("concluida", 0, False),
    ],
)
def test_habilita_so_quando_last_undoable_devolve_uma_organizacao(
    qtbot: QtBot, conn: sqlite3.Connection, status: str, moved_count: int, enabled: bool
) -> None:
    _add_organization(conn, status, moved_count)

    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)

    assert tab.undo_button.text() == "Desfazer última organização"
    assert tab.undo_button.isEnabled() is enabled


def test_sem_historico_o_botao_comeca_desabilitado(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)

    assert not tab.undo_button.isEnabled()


def test_ao_abrir_a_aba_o_botao_e_reavaliado(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)
    assert not tab.undo_button.isEnabled()
    _add_organization(conn)

    tab.show()

    assert tab.undo_button.isEnabled()


def test_banco_ilegivel_deixa_o_botao_desabilitado(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _add_organization(conn)
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)
    assert tab.undo_button.isEnabled()
    conn.execute("DROP TABLE organizations")

    tab.refresh_undo()

    assert not tab.undo_button.isEnabled()


def test_desfazer_restaura_os_arquivos_mostra_o_resumo_e_desabilita_o_botao(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window, tab, folder = _window(qtbot, tmp_path, monkeypatch, "foto.jpg", "nota.pdf")
    assert not tab.undo_button.isEnabled()
    _organize(qtbot, tab)
    assert tab.undo_button.isEnabled()
    assert not (folder / "foto.jpg").exists()

    _undo(qtbot, tab)

    assert (folder / "foto.jpg").exists()
    assert (folder / "nota.pdf").exists()
    assert not (folder / "Imagens").exists()
    assert tab.summary.text() == "Desfeito: 2 arquivos restaurados."
    assert not tab.undo_button.isEnabled()
    assert window.organizing is False
    # A pasta e a atual: foi relida e a lista voltou a ter os dois arquivos.
    assert tab.mode == MODE_LISTED
    assert tab.table.model.rowCount() == 2
    assert tab.organize_button.isEnabled()


def test_a_proxima_organizacao_habilita_o_botao_de_novo(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)
    _undo(qtbot, tab)
    assert not tab.undo_button.isEnabled()

    _organize(qtbot, tab)

    assert tab.undo_button.isEnabled()


def test_nao_restaurados_acrescenta_os_caminhos_ao_resumo(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, folder = _window(qtbot, tmp_path, monkeypatch, "foto.jpg", "nota.pdf")
    _organize(qtbot, tab)
    (folder / "Documentos" / "nota.pdf").unlink()

    _undo(qtbot, tab)

    assert (folder / "foto.jpg").exists()
    assert tab.summary.text() == (
        f"Desfeito: 1 arquivos restaurados. Não restaurados: {folder / 'nota.pdf'}"
    )
    assert not tab.undo_button.isEnabled()


def test_organizacao_de_outra_pasta_nao_rele_a_pasta_atual(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    with closing(open_connection(tmp_path / "db" / "filepilot.db")) as other:
        _add_organization(
            other, folder_path=str(tmp_path / "outra"), started_at="2999-01-01T00:00:00Z"
        )
    tab.refresh_undo()
    assert tab.undo_button.isEnabled()
    reads: list[Path] = []
    real_read = tab._read_folder

    def spy(folder: Path, empty_ok: bool = False) -> object:
        reads.append(folder)
        return real_read(folder, empty_ok)

    monkeypatch.setattr(tab, "_read_folder", spy)

    _undo(qtbot, tab)

    assert reads == []
    assert tab.summary.text() == "Desfeito: 0 arquivos restaurados."
    assert not tab.undo_button.isEnabled()


def test_botao_desabilitado_durante_a_organizacao_e_reavaliado_no_fim(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    window, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    with closing(open_connection(tmp_path / "db" / "filepilot.db")) as other:
        _add_organization(other, started_at="2000-01-01T00:00:00Z")
    tab.refresh_undo()
    assert tab.undo_button.isEnabled()
    release = threading.Event()
    real_organize = organize_worker_module.organize

    def slow(*args: object, **kwargs: object) -> object:
        assert release.wait(5)
        return real_organize(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(organize_worker_module, "organize", slow)

    tab.organize_button.click()

    assert window.organizing is True
    assert not tab.undo_button.isEnabled()
    with qtbot.waitSignal(tab.organization_finished, timeout=5000):
        release.set()
    assert tab.undo_button.isEnabled()


def test_ultima_organizacao_ja_desfeita_mostra_a_mensagem_e_desabilita(
    qtbot: QtBot, conn: sqlite3.Connection, tmp_path: Path
) -> None:
    organization_id = _add_organization(conn)
    tab = OrganizeTab(conn, tmp_path / "db" / "filepilot.db")
    qtbot.addWidget(tab)
    assert tab.undo_button.isEnabled()
    conn.execute("UPDATE organizations SET status = 'desfeita' WHERE id = ?", (organization_id,))
    conn.commit()

    _undo(qtbot, tab)

    assert tab.summary.text() == NOTHING_TO_UNDO
    assert not tab.undo_button.isEnabled()


def test_sem_caminho_do_banco_mostra_banco_indisponivel(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _add_organization(conn)
    tab = OrganizeTab(conn)
    qtbot.addWidget(tab)

    tab.undo_button.click()

    assert tab.summary.text() == DATABASE_UNAVAILABLE
    assert tab.undo_button.isEnabled()


class _MessageSpy:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def __call__(self, parent: QObject, title: str, text: str) -> None:
        self.messages.append(text)


def test_durante_o_desfazer_a_janela_nao_fecha_e_os_botoes_ficam_desabilitados(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    spy = _MessageSpy()
    monkeypatch.setattr(main_window_module.QMessageBox, "information", spy)
    window, tab, _ = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    window.show()
    _organize(qtbot, tab)
    release = threading.Event()
    real_undo = organize_worker_module.undo_last

    def slow(connection: sqlite3.Connection) -> UndoResult:
        assert release.wait(5)
        return real_undo(connection)

    monkeypatch.setattr(organize_worker_module, "undo_last", slow)

    tab.undo_button.click()

    assert window.organizing is True
    assert [
        tab.choose_button.isEnabled(),
        tab.refresh_button.isEnabled(),
        tab.simulate_button.isEnabled(),
        tab.organize_button.isEnabled(),
        tab.undo_button.isEnabled(),
    ] == [False] * 5
    assert window.close() is False
    assert spy.messages == [CLOSE_BLOCKED]
    with qtbot.waitSignal(
        tab.organizing_changed, timeout=5000, check_params_cb=lambda value: value is False
    ):
        release.set()
    assert window.organizing is False
    assert tab.summary.text() == "Desfeito: 1 arquivos restaurados."
    window.close()


def test_falha_inesperada_no_desfazer_mostra_o_texto_generico(
    qtbot: QtBot, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, tab, folder = _window(qtbot, tmp_path, monkeypatch, "foto.jpg")
    _organize(qtbot, tab)

    def boom(connection: sqlite3.Connection) -> UndoResult:
        raise RuntimeError("RAW-INTERNAL-DETAIL")

    monkeypatch.setattr(organize_worker_module, "undo_last", boom)

    _undo(qtbot, tab)

    assert "RAW-INTERNAL-DETAIL" not in tab.summary.text()
    assert tab.summary.text() == "Ocorreu um erro inesperado. Tente de novo."
    assert not (folder / "foto.jpg").exists()
