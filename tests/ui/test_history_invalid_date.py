import errno
import sqlite3
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.ui import history_tab as history_tab_module
from filepilot.ui.history_tab import HistoryTab, format_local_time

NOW = "2026-10-11T12:00:00Z"
INVALID_DATE = "0001-01-01T00:00:00Z"
VALID_DATE = "2026-10-12T09:30:00Z"


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "db" / "filepilot.db")
    yield connection
    connection.close()


def _add_organization(
    conn: sqlite3.Connection,
    started_at: str,
    folder_path: str = "/pasta",
    status: str = "concluida",
    moved_count: int = 1,
    failed_count: int = 0,
) -> int:
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, "
        "moved_count, failed_count, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (folder_path, started_at, status, moved_count, failed_count, NOW, NOW),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


class _FailingMoment:
    def replace(self, **_: Any) -> "_FailingMoment":
        return self

    def astimezone(self) -> None:
        raise OSError(errno.EINVAL, "Invalid argument")


class _FailingDatetime:
    @staticmethod
    def strptime(_value: str, _format: str) -> _FailingMoment:
        return _FailingMoment()


def test_data_no_ano_1_aparece_como_esta() -> None:
    assert format_local_time(INVALID_DATE) == INVALID_DATE


def test_oserror_na_conversao_devolve_a_data_como_esta(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(history_tab_module, "datetime", _FailingDatetime)

    assert format_local_time(VALID_DATE) == VALID_DATE


def test_pagina_com_data_invalida_carrega_as_duas_organizacoes(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _add_organization(conn, INVALID_DATE, "/invalida")
    _add_organization(conn, VALID_DATE, "/valida")

    tab = HistoryTab(conn)
    qtbot.addWidget(tab)
    tab.reload()

    model = tab.organization_model
    assert model.rowCount() == 2
    assert model.index(0, 0).data(Qt.ItemDataRole.DisplayRole) == format_local_time(VALID_DATE)
    assert model.index(1, 0).data(Qt.ItemDataRole.DisplayRole) == INVALID_DATE
    assert tab.status_label.text() == ""
    assert tab.retry_button.isHidden()


def test_data_valida_e_texto_ilegivel_continuam_iguais() -> None:
    local = format_local_time(VALID_DATE)

    assert local != VALID_DATE
    assert len(local) == len("12/10/2026 09:30")
    assert format_local_time("ontem") == "ontem"
