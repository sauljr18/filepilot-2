import sqlite3
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import QThread
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import OrganizationResult, Plan
from filepilot.services import organizer as organizer_module
from filepilot.services.planner import build_plan
from filepilot.services.scanner import scan_folder
from filepilot.ui import organize_tab as organize_tab_module
from filepilot.ui import organize_worker as organize_worker_module
from filepilot.ui.organize_tab import MODE_LISTED, OrganizeTab
from filepilot.ui.organize_worker import OrganizeWorker, run_in_thread

RAW_TEXT = "RAW-INTERNAL-DETAIL"


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "db" / "filepilot.db"


@pytest.fixture
def conn(db_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(db_path)
    yield connection
    connection.close()


def _folder_with(tmp_path: Path, *names: str) -> Path:
    folder = tmp_path / "entrada"
    folder.mkdir()
    for name in names:
        (folder / name).write_bytes(b"x")
    return folder


def _plan(folder: Path) -> Plan:
    return build_plan(folder, scan_folder(folder), [])


def _names(folder: Path) -> list[str]:
    return sorted(item.name for item in folder.iterdir() if item.is_file())


def test_worker_emite_progresso_e_resultado_em_outra_thread(
    qtbot: QtBot, tmp_path: Path, db_path: Path, conn: sqlite3.Connection
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg", "nota.pdf")
    worker = OrganizeWorker(_plan(folder), db_path)
    progress: list[tuple[int, int, str]] = []
    worker.progress.connect(lambda *args: progress.append(args))

    with qtbot.waitSignal(worker.finished, timeout=5000) as blocker:
        thread = run_in_thread(worker)
    thread.wait()

    result = blocker.args[0]
    assert isinstance(result, OrganizationResult)
    assert (result.moved_count, result.failed_count) == (2, 0)
    assert progress[0][:2] == (0, 2)
    assert progress[-1] == (2, 2, "")
    assert _names(folder) == []


def test_worker_nao_roda_na_thread_da_interface(
    qtbot: QtBot,
    tmp_path: Path,
    db_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg")
    threads: list[QThread] = []
    real_organize = organize_worker_module.organize

    def spy(
        plan: Plan,
        conn: sqlite3.Connection,
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> OrganizationResult:
        threads.append(QThread.currentThread())
        return real_organize(plan, conn, progress_callback)

    monkeypatch.setattr(organize_worker_module, "organize", spy)
    worker = OrganizeWorker(_plan(folder), db_path)
    with qtbot.waitSignal(worker.finished, timeout=5000):
        thread = run_in_thread(worker)
    thread.wait()

    assert len(threads) == 1
    assert threads[0] is not QThread.currentThread()


def test_worker_converte_excecao_inesperada_em_erro_interno(
    qtbot: QtBot,
    tmp_path: Path,
    db_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(*args: object, **kwargs: object) -> OrganizationResult:
        raise RuntimeError(RAW_TEXT)

    monkeypatch.setattr(organize_worker_module, "organize", boom)
    folder = _folder_with(tmp_path, "foto.jpg")
    worker = OrganizeWorker(_plan(folder), db_path)
    with qtbot.waitSignal(worker.failed, timeout=5000) as blocker:
        thread = run_in_thread(worker)
    thread.wait()

    code, message = blocker.args
    assert code == "ERRO_INTERNO"
    assert message == "Ocorreu um erro inesperado. Tente de novo."
    assert RAW_TEXT not in message


def test_worker_repassa_erro_de_contrato(
    qtbot: QtBot,
    tmp_path: Path,
    db_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def busy(*args: object, **kwargs: object) -> OrganizationResult:
        raise FilePilotError("ORGANIZACAO_EM_ANDAMENTO", "Aguarde a organização terminar.")

    monkeypatch.setattr(organize_worker_module, "organize", busy)
    folder = _folder_with(tmp_path, "foto.jpg")
    worker = OrganizeWorker(_plan(folder), db_path)
    with qtbot.waitSignal(worker.failed, timeout=5000) as blocker:
        thread = run_in_thread(worker)
    thread.wait()

    assert blocker.args == ["ORGANIZACAO_EM_ANDAMENTO", "Aguarde a organização terminar."]


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


def test_organizar_mostra_a_barra_e_o_resumo_final(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg", "nota.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    assert not tab.progress.isVisibleTo(tab)

    with qtbot.waitSignal(tab.organization_finished, timeout=5000) as blocker:
        tab.organize_button.click()

    assert tab.progress.isVisibleTo(tab)
    assert (tab.progress.minimum(), tab.progress.maximum()) == (0, 2)
    assert tab.progress.value() == 2
    assert tab.progress.format() == "%v de %m arquivos"
    assert tab.progress.text() == "2 de 2 arquivos"
    assert tab.summary.text() == "Concluído: 2 movidos, 0 falhas."
    assert tab.mode == MODE_LISTED
    assert _names(folder) == []
    organization_id = blocker.args[0]
    row = conn.execute(
        "SELECT moved_count, failed_count, status FROM organizations WHERE id = ?",
        (organization_id,),
    ).fetchone()
    assert row == (2, 0, "concluida")


def test_depois_de_organizar_a_pasta_e_relida(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg", "sem-categoria.zzz")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)

    with qtbot.waitSignal(tab.organization_finished, timeout=5000):
        tab.organize_button.click()

    assert [file.name for file in tab.files] == ["sem-categoria.zzz"]
    assert tab.mode == MODE_LISTED
    assert tab.organize_button.isEnabled() is False
    assert tab.choose_button.isEnabled()
    assert tab.refresh_button.isEnabled()


def test_resumo_conta_as_falhas_por_arquivo(
    qtbot: QtBot,
    tmp_path: Path,
    conn: sqlite3.Connection,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    folder = _folder_with(tmp_path, "foto.jpg", "nota.pdf")
    tab = _open_tab(qtbot, conn, monkeypatch, folder)
    real_rename = organizer_module.os.rename

    def rename(source: str | Path, destination: str | Path) -> None:
        if Path(source).name == "foto.jpg":
            raise PermissionError(RAW_TEXT)
        real_rename(source, destination)

    monkeypatch.setattr(organizer_module.os, "rename", rename)

    with qtbot.waitSignal(tab.organization_finished, timeout=5000) as blocker:
        tab.organize_button.click()

    assert tab.summary.text() == "Concluído: 1 movidos, 1 falhas."
    assert [file.name for file in tab.files] == ["foto.jpg"]
    row = conn.execute(
        "SELECT moved_count, failed_count FROM organizations WHERE id = ?",
        (blocker.args[0],),
    ).fetchone()
    assert row == (1, 1)
