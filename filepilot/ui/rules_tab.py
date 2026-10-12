"""Aba Regras: lista, edicao, exclusao e ordem das regras (SPEC 7.5)."""

import sqlite3
from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QCoreApplication,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Rule
from filepilot.services.rules import delete_rule, list_rules, move_rule
from filepilot.ui.rule_editor_dialog import RuleEditorDialog

HEADERS = ("Prioridade", "Nome", "Extensões", "Subpasta")

MODE_LOADING = "carregando"
MODE_EMPTY = "vazio"
MODE_LISTED = "listado"
MODE_ERROR = "erro"

LOADING_MESSAGE = "Carregando regras..."
EMPTY_MESSAGE = 'Nenhuma regra personalizada. Use "Nova regra" para criar a primeira.'
DELETE_TITLE = "Excluir regra"
DELETE_QUESTION = 'Excluir a regra "{name}"? O histórico não será alterado.'
DELETE_LABEL = "Excluir"
CANCEL_LABEL = "Cancelar"

_Index = QModelIndex | QPersistentModelIndex


class RuleTableModel(QAbstractTableModel):
    """Linhas somente leitura, na ordem de prioridade recebida (7.5)."""

    def __init__(self) -> None:
        super().__init__()
        self._rules: list[Rule] = []

    def set_rules(self, rules: list[Rule]) -> None:
        self.beginResetModel()
        self._rules = list(rules)
        self.endResetModel()

    def rowCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: N802 - nome do Qt
        return 0 if parent.isValid() else len(self._rules)

    def columnCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: N802 - nome do Qt
        return 0 if parent.isValid() else len(HEADERS)

    def headerData(  # noqa: N802 - nome do Qt
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return HEADERS[section]
        return None

    def data(self, index: _Index, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        rule = self._rules[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return (
                str(rule.position),
                rule.name,
                ", ".join(sorted(rule.extensions)),
                rule.destination_folder,
            )[index.column()]
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None

    def flags(self, index: _Index) -> Qt.ItemFlag:
        """Somente leitura, com a linha selecionavel."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


class RuleTableView(QTableView):
    """`QTableView` de `RuleTableModel` com selecao de uma linha inteira (7.5)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.rules_model = RuleTableModel()
        self.setModel(self.rules_model)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionsClickable(False)


class RulesTab(QWidget):
    """Mostra as regras por prioridade e chama o servico para cada acao."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__()
        self._conn = conn
        self.rules: list[Rule] = []
        self.mode = MODE_LOADING

        self.table = RuleTableView()
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.new_button = QPushButton("Nova regra")
        self.edit_button = QPushButton("Editar")
        self.delete_button = QPushButton("Excluir")
        self.up_button = QPushButton("Subir")
        self.down_button = QPushButton("Descer")
        self._pages = QStackedWidget()
        self._pages.addWidget(self.table)
        self._pages.addWidget(self.message_label)
        self._build_layout()

        self.new_button.clicked.connect(self.new_rule)
        self.edit_button.clicked.connect(self.edit_rule)
        self.delete_button.clicked.connect(self.delete_selected)
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        selection = self.table.selectionModel()
        selection.selectionChanged.connect(self._on_selection_changed)
        self.reload()

    def _build_layout(self) -> None:
        button_bar = QHBoxLayout()
        for button in (
            self.new_button,
            self.edit_button,
            self.delete_button,
            self.up_button,
            self.down_button,
        ):
            button_bar.addWidget(button)
        button_bar.addStretch(1)
        layout = QVBoxLayout(self)
        layout.addLayout(button_bar)
        layout.addWidget(self._pages, 1)

    # -- selecao e botoes ------------------------------------------------

    def _selected_row(self) -> int | None:
        rows = self.table.selectionModel().selectedRows()
        return rows[0].row() if rows else None

    def selected_rule(self) -> Rule | None:
        """A regra da linha selecionada, ou None sem selecao."""
        row = self._selected_row()
        return self.rules[row] if row is not None else None

    def select_rule(self, rule_id: int) -> None:
        """Seleciona a linha da regra `rule_id`, quando ela esta na lista."""
        for row, rule in enumerate(self.rules):
            if rule.id == rule_id:
                self.table.selectRow(row)
                return

    def _on_selection_changed(self, *_args: object) -> None:
        self._update_buttons()

    def _update_buttons(self) -> None:
        row = self._selected_row()
        self.edit_button.setEnabled(row is not None)
        self.delete_button.setEnabled(row is not None)
        self.up_button.setEnabled(row is not None and row > 0)
        self.down_button.setEnabled(row is not None and row < len(self.rules) - 1)

    # -- estados ---------------------------------------------------------

    def _show_message(self, mode: str, text: str) -> None:
        self.mode = mode
        self.message_label.setText(text)
        self._pages.setCurrentWidget(self.message_label)

    def _show_error(self, error: FilePilotError) -> None:
        self.rules = []
        self.table.rules_model.set_rules([])
        self._show_message(MODE_ERROR, error.message)
        self._update_buttons()

    def _show_rules(self, rules: list[Rule], select_id: int | None = None) -> None:
        self.rules = list(rules)
        self.table.rules_model.set_rules(self.rules)
        if self.rules:
            self.mode = MODE_LISTED
            self._pages.setCurrentWidget(self.table)
        else:
            self._show_message(MODE_EMPTY, EMPTY_MESSAGE)
        if select_id is not None:
            self.select_rule(select_id)
        self._update_buttons()

    def _load(self, select_id: int | None) -> None:
        self._show_message(MODE_LOADING, LOADING_MESSAGE)
        QCoreApplication.processEvents()
        try:
            rules = list_rules(self._conn)
        except FilePilotError as error:
            self._show_error(error)
            return
        self._show_rules(rules, select_id)

    def reload(self) -> None:
        """Le as regras de novo, mantendo a selecao quando a regra ainda existe."""
        selected = self.selected_rule()
        self._load(selected.id if selected is not None else None)

    # -- criar e editar --------------------------------------------------

    def new_rule(self) -> None:
        """Abre o dialogo para criar uma regra."""
        self._open_editor(None)

    def edit_rule(self) -> None:
        """Abre o dialogo para editar a regra selecionada."""
        rule = self.selected_rule()
        if rule is not None:
            self._open_editor(rule)

    def _open_editor(self, rule: Rule | None) -> None:
        dialog = RuleEditorDialog(self._conn, rule, self)
        dialog.saved.connect(self._on_saved)
        dialog.exec()

    def _on_saved(self, rule_id: int) -> None:
        self._load(rule_id)

    # -- excluir e reordenar ---------------------------------------------

    def _confirm_delete(self, name: str) -> bool:
        """Pergunta antes de excluir; so o botao Excluir confirma."""
        box = QMessageBox(
            QMessageBox.Icon.Question,
            DELETE_TITLE,
            DELETE_QUESTION.format(name=name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self,
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)
        yes = box.button(QMessageBox.StandardButton.Yes)
        no = box.button(QMessageBox.StandardButton.No)
        if yes is not None:
            yes.setText(DELETE_LABEL)
        if no is not None:
            no.setText(CANCEL_LABEL)
        return box.exec() == QMessageBox.StandardButton.Yes

    def delete_selected(self) -> None:
        """Exclui a regra selecionada depois da confirmacao."""
        rule = self.selected_rule()
        if rule is None or not self._confirm_delete(rule.name):
            return
        try:
            delete_rule(self._conn, rule.id)
        except FilePilotError as error:
            self._show_error(error)
            return
        self._load(None)

    def move_up(self) -> None:
        """Sobe a regra selecionada uma posicao."""
        self._move(-1)

    def move_down(self) -> None:
        """Desce a regra selecionada uma posicao."""
        self._move(1)

    def _move(self, offset: int) -> None:
        rule = self.selected_rule()
        if rule is None:
            return
        try:
            rules = move_rule(self._conn, rule.id, rule.position + offset)
        except FilePilotError as error:
            self._show_error(error)
            return
        self._show_rules(rules, rule.id)
