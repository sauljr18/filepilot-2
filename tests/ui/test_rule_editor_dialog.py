import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest
from PySide6.QtWidgets import QDialog, QMessageBox
from pytestqt.qtbot import QtBot

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Rule
from filepilot.services.rules import create_rule, list_rules
from filepilot.ui import rule_editor_dialog as dialog_module
from filepilot.ui.rule_editor_dialog import RuleEditorDialog

MSG_NAME = "Informe um nome de até 60 caracteres."
MSG_EXTENSIONS = "Informe ao menos uma extensão (letras e números, até 15)."
MSG_DESTINATION = "Informe uma subpasta válida dentro da pasta escolhida."


@pytest.fixture
def conn(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    connection = open_connection(tmp_path / "filepilot.db")
    yield connection
    connection.close()


def _dialog(
    qtbot: QtBot, conn: sqlite3.Connection, rule: Rule | None = None
) -> RuleEditorDialog:
    dialog = RuleEditorDialog(conn, rule)
    qtbot.addWidget(dialog)
    return dialog


def _fill(dialog: RuleEditorDialog, name: str, extensions: str, destination: str) -> None:
    dialog.name_edit.setText(name)
    dialog.extensions_edit.setText(extensions)
    dialog.destination_edit.setText(destination)


def test_dialogo_tem_os_tres_campos_e_os_dois_botoes(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    dialog = _dialog(qtbot, conn)

    assert dialog.name_edit.placeholderText() == "Planilhas do trabalho"
    assert dialog.extensions_edit.placeholderText() == "xlsx, csv"
    assert dialog.destination_edit.placeholderText() == "Trabalho/Planilhas"
    assert dialog.save_button.text() == "Salvar"
    assert dialog.cancel_button.text() == "Cancelar"
    assert dialog.windowTitle() == "Nova regra"
    assert all(label.isHidden() for label in dialog.error_labels.values())


def test_salvar_regra_valida_cria_emite_saved_e_fecha(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    dialog = _dialog(qtbot, conn)
    _fill(dialog, "  Planilhas  ", ".XLSX, csv", "Trabalho/Planilhas")

    with qtbot.waitSignal(dialog.saved) as saved:
        dialog.save_button.click()

    rules = list_rules(conn)
    assert len(rules) == 1
    assert saved.args == [rules[0].id]
    assert dialog.result() == QDialog.DialogCode.Accepted
    assert dialog.name_edit.text() == "Planilhas"
    assert dialog.extensions_edit.text() == "csv, xlsx"


def test_salvar_em_edicao_chama_update_e_mantem_a_posicao(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    create_rule(conn, "Fotos", ["png"], "Imagens")
    second = create_rule(conn, "Notas", ["txt"], "Textos")
    dialog = _dialog(qtbot, conn, second)
    assert dialog.windowTitle() == "Editar regra"
    assert dialog.name_edit.text() == "Notas"
    _fill(dialog, "Anotacoes", "txt, md", "Docs")

    with qtbot.waitSignal(dialog.saved) as saved:
        dialog.save_button.click()

    assert saved.args == [second.id]
    updated = list_rules(conn)[1]
    assert (updated.name, updated.position, updated.destination_folder) == (
        "Anotacoes",
        2,
        "Docs",
    )
    assert updated.extensions == frozenset({"txt", "md"})


def test_regra_invalida_mostra_a_mensagem_exata_por_campo_e_nao_fecha(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    dialog = _dialog(qtbot, conn)
    _fill(dialog, "", "", "..")

    dialog.save_button.click()

    labels = dialog.error_labels
    assert labels["name"].text() == MSG_NAME
    assert labels["extensions"].text() == MSG_EXTENSIONS
    assert labels["destination_folder"].text() == MSG_DESTINATION
    assert all(not label.isHidden() for label in labels.values())
    assert all("red" in label.styleSheet() for label in labels.values())
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert list_rules(conn) == []


def test_so_o_campo_com_erro_mostra_mensagem(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    dialog = _dialog(qtbot, conn)
    _fill(dialog, "Planilhas", "xlsx!", "Trabalho")

    dialog.save_button.click()

    labels = dialog.error_labels
    assert labels["extensions"].text() == MSG_EXTENSIONS
    assert labels["name"].isHidden()
    assert labels["destination_folder"].isHidden()


def test_corrigir_e_salvar_de_novo_limpa_as_mensagens(
    qtbot: QtBot, conn: sqlite3.Connection
) -> None:
    dialog = _dialog(qtbot, conn)
    _fill(dialog, "", "xlsx", "Trabalho")
    dialog.save_button.click()
    assert not dialog.error_labels["name"].isHidden()

    dialog.name_edit.setText("Planilhas")
    dialog.save_button.click()

    assert all(label.isHidden() for label in dialog.error_labels.values())
    assert dialog.result() == QDialog.DialogCode.Accepted


def test_durante_a_gravacao_o_botao_vira_salvando_e_fica_desabilitado(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    dialog = _dialog(qtbot, conn)
    _fill(dialog, "Planilhas", "xlsx", "Trabalho")
    seen: list[tuple[str, bool]] = []
    real_create = dialog_module.create_rule

    def spy(
        connection: sqlite3.Connection,
        name: str,
        extensions: list[str],
        destination_folder: str,
    ) -> Rule:
        seen.append((dialog.save_button.text(), dialog.save_button.isEnabled()))
        return real_create(connection, name, extensions, destination_folder)

    monkeypatch.setattr(dialog_module, "create_rule", spy)

    dialog.save_button.click()

    assert seen == [("Salvando...", False)]


def test_banco_indisponivel_mostra_critical_e_o_dialogo_continua_aberto(
    qtbot: QtBot, conn: sqlite3.Connection, monkeypatch: pytest.MonkeyPatch
) -> None:
    dialog = _dialog(qtbot, conn)
    _fill(dialog, "Planilhas", "xlsx", "Trabalho")
    shown: list[str] = []

    def failing(*args: object, **kwargs: object) -> Rule:
        raise FilePilotError("BANCO_INDISPONIVEL", "Não foi possível acessar o histórico.")

    def critical(parent: object, title: str, text: str) -> None:
        shown.append(text)

    monkeypatch.setattr(dialog_module, "create_rule", failing)
    monkeypatch.setattr(QMessageBox, "critical", critical)

    dialog.save_button.click()

    assert shown == ["Não foi possível acessar o histórico."]
    assert dialog.result() != QDialog.DialogCode.Accepted
    assert dialog.save_button.text() == "Salvar"
    assert dialog.save_button.isEnabled() is True
    assert all(label.isHidden() for label in dialog.error_labels.values())


def test_cancelar_fecha_sem_gravar(qtbot: QtBot, conn: sqlite3.Connection) -> None:
    dialog = _dialog(qtbot, conn)
    _fill(dialog, "Planilhas", "xlsx", "Trabalho")

    dialog.cancel_button.click()

    assert dialog.result() == QDialog.DialogCode.Rejected
    assert list_rules(conn) == []
