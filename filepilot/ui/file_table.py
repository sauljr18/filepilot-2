"""Tabela de arquivos da aba Organizar (SPEC 7.3)."""

from dataclasses import dataclass
from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt
from PySide6.QtGui import QFont, QGuiApplication, QPalette
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLabel,
    QStackedLayout,
    QTableView,
    QWidget,
)

from filepilot.domain.categories import CATEGORIES
from filepilot.domain.models import PlannedOperation, Plan, ScannedFile

HEADERS = ("Arquivo", "Extensão", "Categoria", "Destino", "Regra")
_COLUMN_FILE = 0
_COLUMN_DESTINATION = 3
_COLUMN_RULE = 4

CUSTOM_RULE = "Regra personalizada"
NO_CATEGORY = "sem categoria"
EMPTY_MESSAGE = "Nenhum arquivo para mostrar."

# Largura inicial das colunas que rolam na horizontal em tela estreita.
_WIDE_COLUMN_WIDTH = 240

_Index = QModelIndex | QPersistentModelIndex


@dataclass(frozen=True)
class _Row:
    name: str
    extension: str
    category: str
    destination: str
    rule: str
    uncategorized: bool


def _category_label(operation: PlannedOperation | None, planned: bool) -> str:
    """Rotulo da coluna Categoria; sem plano calculado nao ha o que prever."""
    if not planned:
        return ""
    if operation is None:
        return NO_CATEGORY
    if operation.rule_name is not None:
        return CUSTOM_RULE
    if operation.category is None:
        return NO_CATEGORY
    return CATEGORIES[operation.category].folder


def _build_row(
    item: ScannedFile,
    operation: PlannedOperation | None,
    plan: Plan | None,
    show_destination: bool,
) -> _Row:
    destination = ""
    if operation is not None and plan is not None and show_destination:
        destination = str(operation.destination_path.relative_to(plan.folder))
    category = _category_label(operation, plan is not None)
    return _Row(
        name=item.name,
        extension=item.extension,
        category=category,
        destination=destination,
        rule=(operation.rule_name or "") if operation is not None else "",
        uncategorized=category == NO_CATEGORY,
    )


class FileTableModel(QAbstractTableModel):
    """Linhas somente leitura, na ordem de `files` (7.3)."""

    def __init__(self) -> None:
        super().__init__()
        self._rows: list[_Row] = []

    def set_rows(
        self,
        files: list[ScannedFile],
        plan: Plan | None,
        show_destination: bool = True,
    ) -> None:
        """Troca as linhas; `show_destination` falso deixa a coluna Destino vazia."""
        by_source = (
            {op.source_path: op for op in plan.operations} if plan is not None else {}
        )
        rows = [
            _build_row(item, by_source.get(item.path), plan, show_destination)
            for item in files
        ]
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: N802 - nome do Qt
        return 0 if parent.isValid() else len(self._rows)

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
        row = self._rows[index.row()]
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return (row.name, row.extension, row.category, row.destination, row.rule)[column]
        if role == Qt.ItemDataRole.ForegroundRole and row.uncategorized:
            return QGuiApplication.palette().color(
                QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text
            )
        if role == Qt.ItemDataRole.FontRole and column == _COLUMN_RULE and row.rule:
            font = QFont()
            font.setBold(True)
            return font
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None

    def flags(self, index: _Index) -> Qt.ItemFlag:
        """Somente leitura e sem selecao de celula editavel."""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


class FileTableView(QWidget):
    """`QTableView` de `FileTableModel` e a mensagem de tabela vazia (7.3)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.model = FileTableModel()
        self.view = QTableView()
        self.view.setModel(self.model)
        self.view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.view.verticalHeader().setVisible(False)
        self._configure_header()
        self.empty_label = QLabel(EMPTY_MESSAGE)
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._stack = QStackedLayout(self)
        self._stack.setContentsMargins(0, 0, 0, 0)
        self._stack.addWidget(self.view)
        self._stack.addWidget(self.empty_label)
        self._show_current()

    def _configure_header(self) -> None:
        header = self.view.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsClickable(False)
        for column in range(len(HEADERS)):
            wide = column in (_COLUMN_FILE, _COLUMN_DESTINATION)
            header.setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.Interactive
                if wide
                else QHeaderView.ResizeMode.ResizeToContents,
            )
        header.resizeSection(_COLUMN_FILE, _WIDE_COLUMN_WIDTH)
        header.resizeSection(_COLUMN_DESTINATION, _WIDE_COLUMN_WIDTH)

    def set_rows(
        self,
        files: list[ScannedFile],
        plan: Plan | None,
        show_destination: bool = True,
    ) -> None:
        """Mostra `files` com a categoria e o destino previstos em `plan`."""
        self.model.set_rows(files, plan, show_destination)
        self._show_current()

    def _show_current(self) -> None:
        empty = self.model.rowCount() == 0
        self._stack.setCurrentWidget(self.empty_label if empty else self.view)
