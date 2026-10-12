import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.services.rules import create_rule
from filepilot.ui import rules_tab as rules_tab_module
from filepilot.ui.main_window import build_tabs
from filepilot.ui.rule_editor_dialog import RuleEditorDialog
from filepilot.ui.rules_tab import RulesTab

EMPTY = 'Nenhuma regra personalizada. Use "Nova regra" para criar a primeira.'


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "filepilot.db")
    yield connection
    connection.close()


def _tab(qtbot: QtBot, conn: sqlite3.Connection) -> RulesTab:
    tab = RulesTab(conn)
    qtbot.addWidget(tab)
    return tab


def _cell(tab: RulesTab, row: int, column: int) -> str:
    model = tab.table.rules_model
    return str(model.index(row, column).data(Qt.ItemDataRole.DisplayRole))


def _three_rules(conn: sqlite3.Connection) -> None:
    create_rule(conn, "Planilhas", ["xlsx", "csv"], "Trabalho/Planilhas")
    create_rule(conn, "Fotos", ["png"], "Imagens")
    create_rule(conn, "Notas", ["txt", "md"], "Textos")


def test_lista_mostra_as_colunas_e_as_regras_por_prioridade(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _three_rules(conn)

    tab = _tab(qtbot, conn)

    model = tab.table.rules_model
    headers = [
        model.headerData(column, Qt.Orientation.Horizontal)
        for column in range(model.columnCount())
    ]
    assert headers == ["Prioridade", "Nome", "Extensões", "Subpasta"]
    assert tab.mode == "listado"
    assert [_cell(tab, row, 0) for row in range(3)] == ["1", "2", "3"]
    assert [_cell(tab, row, 1) for row in range(3)] == ["Planilhas", "Fotos", "Notas"]
    assert _cell(tab, 0, 2) == "csv, xlsx"
    assert _cell(tab, 2, 2) == "md, txt"
    assert _cell(tab, 0, 3) == "Trabalho/Planilhas"


def test_sem_regras_mostra_o_convite_para_criar_a_primeira(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = _tab(qtbot, conn)

    assert tab.mode == "vazio"
    assert tab.message_label.text() == EMPTY
    assert tab.table.rules_model.rowCount() == 0
    assert tab.edit_button.isEnabled() is False


def test_durante_a_leitura_mostra_carregando(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab(qtbot, conn)
    seen: list[tuple[str, str]] = []

    def spy(connection: sqlite3.Connection) -> list[object]:
        seen.append((tab.mode, tab.message_label.text()))
        return []

    monkeypatch.setattr(rules_tab_module, "list_rules", spy)

    tab.reload()

    assert seen == [("carregando", "Carregando regras...")]
    assert tab.mode == "vazio"


def test_erro_do_servico_mostra_a_mensagem_dele(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab(qtbot, conn)

    def failing(connection: sqlite3.Connection) -> list[object]:
        raise FilePilotError("BANCO_INDISPONIVEL", "Não foi possível acessar o histórico.")

    monkeypatch.setattr(rules_tab_module, "list_rules", failing)

    tab.reload()

    assert tab.mode == "erro"
    assert tab.message_label.text() == "Não foi possível acessar o histórico."
    assert tab.table.rules_model.rowCount() == 0


def _enabled(tab: RulesTab) -> dict[str, bool]:
    return {
        "editar": tab.edit_button.isEnabled(),
        "excluir": tab.delete_button.isEnabled(),
        "subir": tab.up_button.isEnabled(),
        "descer": tab.down_button.isEnabled(),
    }


def test_botoes_dependem_da_selecao_e_da_posicao(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    _three_rules(conn)
    tab = _tab(qtbot, conn)

    assert tab.new_button.isEnabled() is True
    assert _enabled(tab) == {
        "editar": False,
        "excluir": False,
        "subir": False,
        "descer": False,
    }

    tab.table.selectRow(0)
    assert _enabled(tab) == {"editar": True, "excluir": True, "subir": False, "descer": True}

    tab.table.selectRow(1)
    assert _enabled(tab) == {"editar": True, "excluir": True, "subir": True, "descer": True}

    tab.table.selectRow(2)
    assert _enabled(tab) == {"editar": True, "excluir": True, "subir": True, "descer": False}


def test_regra_unica_nao_sobe_nem_desce(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    create_rule(conn, "Fotos", ["png"], "Imagens")
    tab = _tab(qtbot, conn)

    tab.table.selectRow(0)

    assert _enabled(tab) == {"editar": True, "excluir": True, "subir": False, "descer": False}


def test_reload_mantem_a_regra_selecionada(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    _three_rules(conn)
    tab = _tab(qtbot, conn)
    tab.table.selectRow(1)

    tab.reload()

    selected = tab.selected_rule()
    assert selected is not None
    assert selected.name == "Fotos"


def test_reload_pega_regras_criadas_depois(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    tab = _tab(qtbot, conn)
    assert tab.mode == "vazio"

    create_rule(conn, "Fotos", ["png"], "Imagens")
    tab.reload()

    assert tab.mode == "listado"
    assert _cell(tab, 0, 1) == "Fotos"


def test_build_tabs_troca_o_marcador_de_regras_pela_aba_real(
    conn: sqlite3.Connection, qtbot: QtBot
) -> None:
    built = build_tabs(conn)
    for _, widget in built:
        qtbot.addWidget(widget)

    assert isinstance(built[2][1], RulesTab)
    assert built[2][0] == "Regras"


def test_salvar_no_dialogo_recarrega_e_seleciona_a_regra(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    _three_rules(conn)
    tab = _tab(qtbot, conn)

    def fill_and_save(dialog: RuleEditorDialog) -> int:
        dialog.name_edit.setText("Planos")
        dialog.extensions_edit.setText("pdf")
        dialog.destination_edit.setText("Documentos")
        dialog.save_button.click()
        return 0

    monkeypatch.setattr(RuleEditorDialog, "exec", fill_and_save)

    tab.new_button.click()

    selected = tab.selected_rule()
    assert selected is not None
    assert selected.name == "Planos"
    assert selected.position == 4
    assert _cell(tab, 3, 1) == "Planos"


def test_editar_abre_o_dialogo_com_a_regra_selecionada(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    _three_rules(conn)
    tab = _tab(qtbot, conn)
    tab.table.selectRow(1)
    opened: list[tuple[str, str, str]] = []

    def inspect_and_rename(dialog: RuleEditorDialog) -> int:
        opened.append(
            (
                dialog.name_edit.text(),
                dialog.extensions_edit.text(),
                dialog.destination_edit.text(),
            )
        )
        dialog.name_edit.setText("Imagens")
        dialog.save_button.click()
        return 0

    monkeypatch.setattr(RuleEditorDialog, "exec", inspect_and_rename)

    tab.edit_button.click()

    assert opened == [("Fotos", "png", "Imagens")]
    selected = tab.selected_rule()
    assert selected is not None
    assert (selected.name, selected.position) == ("Imagens", 2)
