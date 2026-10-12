"""Dialogo para criar e editar uma regra (SPEC 7.5)."""

import sqlite3

from PySide6.QtCore import QCoreApplication, Signal
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Rule
from filepilot.services.rules import create_rule, update_rule

TITLE_NEW = "Nova regra"
TITLE_EDIT = "Editar regra"
SAVE_LABEL = "Salvar"
SAVING_LABEL = "Salvando..."
CANCEL_LABEL = "Cancelar"
ERROR_TITLE = "FilePilot"

LABEL_NAME = "Nome"
LABEL_EXTENSIONS = "Extensões (separadas por vírgula)"
LABEL_DESTINATION = "Subpasta de destino"
EXAMPLE_NAME = "Planilhas do trabalho"
EXAMPLE_EXTENSIONS = "xlsx, csv"
EXAMPLE_DESTINATION = "Trabalho/Planilhas"

_ERROR_STYLE = "color: red;"
INVALID_RULE = "REGRA_INVALIDA"


class RuleEditorDialog(QDialog):
    """Cria uma regra, ou edita `rule`, chamando o servico de regras."""

    saved = Signal(int)

    def __init__(
        self,
        conn: sqlite3.Connection,
        rule: Rule | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._conn = conn
        self._rule = rule
        self.setWindowTitle(TITLE_NEW if rule is None else TITLE_EDIT)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText(EXAMPLE_NAME)
        self.extensions_edit = QLineEdit()
        self.extensions_edit.setPlaceholderText(EXAMPLE_EXTENSIONS)
        self.destination_edit = QLineEdit()
        self.destination_edit.setPlaceholderText(EXAMPLE_DESTINATION)
        self.error_labels = {
            "name": self._new_error_label(),
            "extensions": self._new_error_label(),
            "destination_folder": self._new_error_label(),
        }
        self.save_button = QPushButton(SAVE_LABEL)
        self.save_button.setDefault(True)
        self.cancel_button = QPushButton(CANCEL_LABEL)
        self._build_layout()
        if rule is not None:
            self._show_rule(rule)

        self.save_button.clicked.connect(self.save)
        self.cancel_button.clicked.connect(self.reject)

    @staticmethod
    def _new_error_label() -> QLabel:
        label = QLabel()
        label.setStyleSheet(_ERROR_STYLE)
        label.setWordWrap(True)
        label.setVisible(False)
        return label

    def _build_layout(self) -> None:
        layout = QVBoxLayout(self)
        fields = (
            (LABEL_NAME, self.name_edit, "name"),
            (LABEL_EXTENSIONS, self.extensions_edit, "extensions"),
            (LABEL_DESTINATION, self.destination_edit, "destination_folder"),
        )
        for text, edit, key in fields:
            layout.addWidget(QLabel(text))
            layout.addWidget(edit)
            layout.addWidget(self.error_labels[key])
        button_bar = QHBoxLayout()
        button_bar.addStretch(1)
        button_bar.addWidget(self.save_button)
        button_bar.addWidget(self.cancel_button)
        layout.addLayout(button_bar)

    def _show_rule(self, rule: Rule) -> None:
        """Mostra os valores da regra, como o servico os devolveu."""
        self.name_edit.setText(rule.name)
        self.extensions_edit.setText(", ".join(sorted(rule.extensions)))
        self.destination_edit.setText(rule.destination_folder)

    # -- gravacao --------------------------------------------------------

    def _extensions(self) -> list[str]:
        text = self.extensions_edit.text()
        return text.split(",") if text.strip() else []

    def _clear_errors(self) -> None:
        for label in self.error_labels.values():
            label.clear()
            label.setVisible(False)

    def _set_saving(self, saving: bool) -> None:
        self.save_button.setText(SAVING_LABEL if saving else SAVE_LABEL)
        self.save_button.setEnabled(not saving)
        if saving:
            QCoreApplication.processEvents()

    def _write(self) -> Rule:
        name = self.name_edit.text()
        destination = self.destination_edit.text()
        if self._rule is None:
            return create_rule(self._conn, name, self._extensions(), destination)
        return update_rule(self._conn, self._rule.id, name, self._extensions(), destination)

    def _show_failure(self, error: FilePilotError) -> None:
        """Mensagem por campo em REGRA_INVALIDA; qualquer outro erro vai a um aviso."""
        shown = False
        if error.code == INVALID_RULE and error.fields:
            for key, message in error.fields.items():
                label = self.error_labels.get(key)
                if label is not None:
                    label.setText(message)
                    label.setVisible(True)
                    shown = True
        if not shown:
            QMessageBox.critical(self, ERROR_TITLE, error.message)

    def save(self) -> None:
        """Grava a regra; em erro o dialogo continua aberto."""
        self._clear_errors()
        self._set_saving(True)
        try:
            rule = self._write()
        except FilePilotError as error:
            self._set_saving(False)
            self._show_failure(error)
            return
        self._set_saving(False)
        self._show_rule(rule)
        self.saved.emit(rule.id)
        self.accept()
