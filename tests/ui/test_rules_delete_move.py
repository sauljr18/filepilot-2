import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QMessageBox
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.services.rules import create_rule, list_rules
from filepilot.ui import rules_tab as rules_tab_module
from filepilot.ui.rules_tab import RulesTab

Yes = QMessageBox.StandardButton.Yes
No = QMessageBox.StandardButton.No


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "filepilot.db")
    yield connection
    connection.close()


def _tab_with_three(qtbot: QtBot, conn: sqlite3.Connection) -> RulesTab:
    create_rule(conn, "Planilhas", ["xlsx"], "Trabalho")
    create_rule(conn, "Fotos", ["png"], "Imagens")
    create_rule(conn, "Notas", ["txt"], "Textos")
    tab = RulesTab(conn)
    qtbot.addWidget(tab)
    return tab


def _answer(monkeypatch: pytest.MonkeyPatch, button: QMessageBox.StandardButton) -> list[dict[str, str]]:
    """Dublê do QMessageBox.exec: registra a pergunta e responde com `button`."""
    asked: list[dict[str, str]] = []

    def fake_exec(box: QMessageBox) -> QMessageBox.StandardButton:
        yes = box.button(Yes)
        no = box.button(No)
        assert yes is not None and no is not None
        asked.append({"text": box.text(), "yes": yes.text(), "no": no.text()})
        return button

    monkeypatch.setattr(QMessageBox, "exec", fake_exec)
    return asked


def _names(conn: sqlite3.Connection) -> list[tuple[int, str]]:
    return [(rule.position, rule.name) for rule in list_rules(conn)]


def _selected_name(tab: RulesTab) -> str | None:
    rule = tab.selected_rule()
    return rule.name if rule is not None else None


def test_excluir_pergunta_com_o_texto_e_os_botoes_da_spec(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab_with_three(qtbot, conn)
    asked = _answer(monkeypatch, No)
    tab.table.selectRow(1)

    tab.delete_button.click()

    assert asked == [
        {
            "text": 'Excluir a regra "Fotos"? O histórico não será alterado.',
            "yes": "Excluir",
            "no": "Cancelar",
        }
    ]


def test_cancelar_mantem_a_regra_e_a_selecao(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab_with_three(qtbot, conn)
    _answer(monkeypatch, No)
    tab.table.selectRow(1)

    tab.delete_button.click()

    assert _names(conn) == [(1, "Planilhas"), (2, "Fotos"), (3, "Notas")]
    assert _selected_name(tab) == "Fotos"


def test_excluir_chama_delete_rule_e_reordena_sem_lacuna(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab_with_three(qtbot, conn)
    _answer(monkeypatch, Yes)
    tab.table.selectRow(0)

    tab.delete_button.click()

    assert _names(conn) == [(1, "Fotos"), (2, "Notas")]
    model = tab.table.rules_model
    assert [model.index(row, 0).data() for row in range(model.rowCount())] == ["1", "2"]
    assert [model.index(row, 1).data() for row in range(model.rowCount())] == ["Fotos", "Notas"]
    assert tab.selected_rule() is None
    assert tab.delete_button.isEnabled() is False


def test_excluir_a_ultima_regra_mostra_o_convite(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    create_rule(conn, "Fotos", ["png"], "Imagens")
    tab = RulesTab(conn)
    qtbot.addWidget(tab)
    _answer(monkeypatch, Yes)
    tab.table.selectRow(0)

    tab.delete_button.click()

    assert list_rules(conn) == []
    assert tab.mode == "vazio"
    assert tab.message_label.text() == (
        'Nenhuma regra personalizada. Use "Nova regra" para criar a primeira.'
    )


def test_subir_move_a_regra_atualiza_a_prioridade_e_mantem_a_selecao(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = _tab_with_three(qtbot, conn)
    tab.table.selectRow(2)

    tab.up_button.click()

    assert _names(conn) == [(1, "Planilhas"), (2, "Notas"), (3, "Fotos")]
    model = tab.table.rules_model
    assert [model.index(row, 1).data() for row in range(3)] == ["Planilhas", "Notas", "Fotos"]
    assert [model.index(row, 0).data() for row in range(3)] == ["1", "2", "3"]
    assert _selected_name(tab) == "Notas"
    selected = tab.selected_rule()
    assert selected is not None and selected.position == 2


def test_descer_move_a_regra_e_mantem_a_selecao(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = _tab_with_three(qtbot, conn)
    tab.table.selectRow(0)

    tab.down_button.click()

    assert _names(conn) == [(1, "Fotos"), (2, "Planilhas"), (3, "Notas")]
    assert _selected_name(tab) == "Planilhas"
    assert tab.up_button.isEnabled() is True
    assert tab.down_button.isEnabled() is True


def test_ao_chegar_ao_extremo_o_botao_correspondente_desabilita(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = _tab_with_three(qtbot, conn)
    tab.table.selectRow(1)

    tab.up_button.click()

    assert _selected_name(tab) == "Fotos"
    assert tab.up_button.isEnabled() is False
    assert tab.down_button.isEnabled() is True


def test_subir_e_descer_sem_selecao_nao_fazem_nada(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    tab = _tab_with_three(qtbot, conn)

    tab.move_up()
    tab.move_down()
    tab.delete_selected()

    assert _names(conn) == [(1, "Planilhas"), (2, "Fotos"), (3, "Notas")]


def test_erro_do_servico_ao_mover_mostra_a_mensagem_dele(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab_with_three(qtbot, conn)
    tab.table.selectRow(1)

    def failing(connection: sqlite3.Connection, rule_id: int, new_position: int) -> list[object]:
        raise FilePilotError("BANCO_INDISPONIVEL", "Não foi possível acessar o histórico.")

    monkeypatch.setattr(rules_tab_module, "move_rule", failing)

    tab.up_button.click()

    assert tab.mode == "erro"
    assert tab.message_label.text() == "Não foi possível acessar o histórico."


def test_erro_do_servico_ao_excluir_mostra_a_mensagem_dele(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    tab = _tab_with_three(qtbot, conn)
    _answer(monkeypatch, Yes)
    tab.table.selectRow(1)

    def failing(connection: sqlite3.Connection, rule_id: int) -> None:
        raise FilePilotError("REGRA_NAO_ENCONTRADA", "A regra não foi encontrada.")

    monkeypatch.setattr(rules_tab_module, "delete_rule", failing)

    tab.delete_button.click()

    assert tab.mode == "erro"
    assert tab.message_label.text() == "A regra não foi encontrada."
    assert _names(conn) == [(1, "Planilhas"), (2, "Fotos"), (3, "Notas")]
