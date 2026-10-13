"""Aba Historico: organizacoes por pagina e as operacoes de cada uma (SPEC 7.4)."""

import sqlite3
from datetime import UTC, datetime
from pathlib import Path
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
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from filepilot.domain.errors import FilePilotError
from filepilot.services.history import (
    OperationRow,
    OrganizationRow,
    get_organization_detail,
    list_organizations,
)

ORGANIZATION_HEADERS = ("Data e hora", "Pasta", "Movidos", "Falhas", "Situação")
OPERATION_HEADERS = ("Arquivo", "Origem", "Destino final", "Situação", "Detalhe")

PAGE_SIZE = 50

_ORGANIZATION_STATUS = {
    "concluida": "Concluída",
    "interrompida": "Interrompida",
    "desfeita": "Desfeita",
    "em_andamento": "Em andamento",
}
_OPERATION_STATUS = {
    "movido": "Movido",
    "falha": "Falha",
    "restaurado": "Restaurado",
    "nao_restaurado": "Não restaurado",
}

_LOADING_HISTORY = "Carregando histórico..."
_LOADING_DETAIL = "Carregando detalhes..."
_EMPTY_HISTORY = "Nenhuma organização registrada ainda."
_NO_SELECTION = "Selecione uma organização."
_NO_OPERATIONS = "Nenhum arquivo nesta organização."

_Index = QModelIndex | QPersistentModelIndex


def format_local_time(started_at: str) -> str:
    """`started_at` (UTC, ISO 8601 com Z) no horario local, `dd/MM/yyyy HH:mm`."""
    try:
        moment = datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ")
        return moment.replace(tzinfo=UTC).astimezone().strftime("%d/%m/%Y %H:%M")
    except (ValueError, OverflowError, OSError):
        return started_at


class _TextTableModel(QAbstractTableModel):
    """Linhas de texto somente leitura, as mesmas para as duas tabelas."""

    def __init__(self, headers: tuple[str, ...]) -> None:
        super().__init__()
        self._headers = headers
        self._rows: list[tuple[str, ...]] = []

    def set_rows(self, rows: list[tuple[str, ...]]) -> None:
        self.beginResetModel()
        self._rows = rows
        self.endResetModel()

    def rowCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: N802 - nome do Qt
        return 0 if parent.isValid() else len(self._rows)

    def columnCount(self, parent: _Index = QModelIndex()) -> int:  # noqa: N802 - nome do Qt
        return 0 if parent.isValid() else len(self._headers)

    def headerData(  # noqa: N802 - nome do Qt
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            return self._headers[section]
        return None

    def data(self, index: _Index, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._rows[index.row()][index.column()]
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        return None

    def flags(self, index: _Index) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable


def _organization_cells(row: OrganizationRow) -> tuple[str, ...]:
    return (
        format_local_time(row.started_at),
        row.folder_path,
        str(row.moved_count),
        str(row.failed_count),
        _ORGANIZATION_STATUS.get(row.status, row.status),
    )


def _operation_cells(row: OperationRow) -> tuple[str, ...]:
    return (
        Path(row.source_path).name,
        row.source_path,
        row.destination_path or "",
        _OPERATION_STATUS.get(row.status, row.status),
        row.error_message or "",
    )


def _make_view(name: str, model: _TextTableModel) -> QTableView:
    view = QTableView()
    view.setObjectName(name)
    view.setModel(model)
    view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    view.setHorizontalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
    view.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
    view.verticalHeader().setVisible(False)
    view.horizontalHeader().setStretchLastSection(True)
    return view


class HistoryTab(QWidget):
    """Lista as organizacoes (50 por pagina) e as operacoes da selecionada.

    A aba nao conhece o banco: le tudo por `list_organizations` e
    `get_organization_detail`, e mostra a mensagem de `FilePilotError` como veio.
    """

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__()
        self._conn = conn
        self.page = 1
        self.selected_id: int | None = None
        self.total = 0
        self._rows: list[OrganizationRow] = []

        self.organization_model = _TextTableModel(ORGANIZATION_HEADERS)
        self.operation_model = _TextTableModel(OPERATION_HEADERS)
        self.organization_view = _make_view("OrganizationTableView", self.organization_model)
        self.operation_view = _make_view("OperationTableView", self.operation_model)
        self.status_label = QLabel()
        self.detail_label = QLabel(_NO_SELECTION)
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.previous_button = QPushButton("Anterior")
        self.next_button = QPushButton("Próxima")
        self.retry_button = QPushButton("Tentar de novo")
        self.retry_button.setVisible(False)
        self._build_layout()

        self.previous_button.clicked.connect(self._go_previous)
        self.next_button.clicked.connect(self._go_next)
        self.retry_button.clicked.connect(self._retry)
        self.organization_view.selectionModel().selectionChanged.connect(
            self._on_selection_changed
        )
        self._update_buttons()
        self._show_detail_message(_NO_SELECTION)

    def _build_layout(self) -> None:
        pager = QHBoxLayout()
        pager.addWidget(self.previous_button)
        pager.addWidget(self.next_button)
        pager.addWidget(self.retry_button)
        pager.addStretch(1)
        left = QVBoxLayout()
        left.addWidget(self.organization_view, 1)
        left.addLayout(pager)
        right = QVBoxLayout()
        right.addWidget(self.detail_label)
        right.addWidget(self.operation_view, 1)
        panels = QHBoxLayout()
        panels.addLayout(left, 1)
        panels.addLayout(right, 1)
        layout = QVBoxLayout(self)
        layout.addWidget(self.status_label)
        layout.addLayout(panels, 1)

    # -- estado ----------------------------------------------------------

    def _update_buttons(self) -> None:
        self.previous_button.setEnabled(self.page > 1)
        self.next_button.setEnabled(self.page * PAGE_SIZE < self.total)

    def _show_detail_message(self, text: str) -> None:
        """Troca o painel direito por uma mensagem, sem tabela."""
        self.operation_model.set_rows([])
        self.detail_label.setText(text)
        self.detail_label.setVisible(True)
        self.operation_view.setVisible(False)

    def _show_operations(self, operations: list[OperationRow]) -> None:
        if not operations:
            self._show_detail_message(_NO_OPERATIONS)
            return
        self.operation_model.set_rows([_operation_cells(row) for row in operations])
        self.detail_label.setVisible(False)
        self.operation_view.setVisible(True)

    def _show_error(self, error: FilePilotError) -> None:
        self._set_organizations([], self.page, 0)
        self.status_label.setText(error.message)
        self.retry_button.setVisible(True)

    def _set_organizations(
        self,
        rows: list[OrganizationRow],
        page: int,
        total: int,
        select_id: int | None = None,
    ) -> None:
        """Troca as linhas; mantem `select_id` selecionado se ele estiver na pagina."""
        self._rows = rows
        self.page = page
        self.total = total
        self.selected_id = None
        selection = self.organization_view.selectionModel()
        selection.blockSignals(True)
        self.organization_model.set_rows([_organization_cells(row) for row in rows])
        self.organization_view.clearSelection()
        selection.blockSignals(False)
        self._update_buttons()
        self._show_detail_message(_NO_SELECTION)
        for position, row in enumerate(rows):
            if row.id == select_id:
                self.organization_view.selectRow(position)
                break

    # -- leitura ---------------------------------------------------------

    def reload(self) -> None:
        """Le de novo a pagina atual; chamado ao dar foco a aba (7.1)."""
        self._load_page(self.page, self.selected_id)

    def _retry(self) -> None:
        """Botao de nova tentativa: so o detalhe, se ha selecao; senao a pagina."""
        if self._rows and self.selected_id is not None:
            self._load_detail(self.selected_id)
        else:
            self.reload()

    def _load_page(self, page: int, select_id: int | None = None) -> bool:
        """Carrega a pagina pedida; falso se o banco falhou."""
        self.retry_button.setVisible(False)
        self.status_label.setText(_LOADING_HISTORY)
        QCoreApplication.processEvents()
        try:
            result = list_organizations(self._conn, page, PAGE_SIZE)
        except FilePilotError as error:
            self._show_error(error)
            return False
        self._set_organizations(result.items, result.page, result.total, select_id)
        self.status_label.setText("" if result.total else _EMPTY_HISTORY)
        return True

    def on_organization_finished(self, organization_id: int) -> None:
        """Uma organizacao terminou: volta a pagina 1 e recarrega (7.4)."""
        self._load_page(1)

    def show_organization(self, organization_id: int) -> None:
        """Carrega a pagina que contem a organizacao, a seleciona e mostra os detalhes.

        Se ela nao esta em nenhuma pagina, fica a pagina 1 sem selecao.
        """
        page = 1
        while True:
            if not self._load_page(page, organization_id):
                return
            if self.selected_id == organization_id:
                return
            if self.page * PAGE_SIZE >= self.total:
                break
            page += 1
        self._load_page(1)

    def _go_previous(self) -> None:
        self._load_page(self.page - 1)

    def _go_next(self) -> None:
        self._load_page(self.page + 1)

    def _on_selection_changed(self) -> None:
        indexes = self.organization_view.selectionModel().selectedRows()
        if not indexes:
            self.selected_id = None
            self._show_detail_message(_NO_SELECTION)
            return
        self.selected_id = self._rows[indexes[0].row()].id
        self._load_detail(self.selected_id)

    def _load_detail(self, organization_id: int) -> None:
        self.retry_button.setVisible(False)
        self._show_detail_message(_LOADING_DETAIL)
        QCoreApplication.processEvents()
        try:
            operations = get_organization_detail(self._conn, organization_id)
        except FilePilotError as error:
            self._show_detail_message(error.message)
            self.retry_button.setVisible(True)
            return
        self._show_operations(operations)
