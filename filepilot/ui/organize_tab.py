"""Aba Organizar: escolha da pasta, lista de arquivos e simulacao (SPEC 7.2)."""

import sqlite3
from pathlib import Path

from PySide6.QtCore import QCoreApplication
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Plan, ScannedFile
from filepilot.services.planner import build_plan
from filepilot.services.rules import list_rules
from filepilot.services.scanner import scan_folder
from filepilot.ui.file_table import FileTableView

MODE_EMPTY = "vazio"
MODE_LOADING = "carregando"
MODE_LISTED = "listado"
MODE_SIMULATED = "simulado"
MODE_ORGANIZING = "organizando"
MODE_ERROR = "erro"

_CHOOSE_FOLDER = "Escolha uma pasta para começar."
_LOADING = "Lendo a pasta..."
_NO_OPERATIONS = "Não há operações para executar."
_FILE_DIALOG_TITLE = "Escolher pasta"
_NOT_CHANGED = "Nenhum arquivo foi alterado."
# Texto de PASTA_ILEGIVEL (SPEC 6); repetido aqui porque a ui nao importa o
# dicionario privado do scanner. Um teste compara os dois.
_UNREADABLE = "Não foi possível ler a pasta escolhida."

# Estados em que ha uma lista valida na tabela e a pessoa pode agir sobre ela.
_ACTIONABLE = (MODE_LISTED, MODE_SIMULATED)
# Estados em que a leitura da pasta ou a organizacao esta em andamento.
_BUSY = (MODE_LOADING, MODE_ORGANIZING)


class OrganizeTab(QWidget):
    """Mostra a pasta escolhida, o plano e o resultado da simulacao."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        super().__init__()
        self._conn = conn
        self.folder: Path | None = None
        self.files: list[ScannedFile] = []
        self.plan: Plan | None = None
        self.mode = MODE_EMPTY

        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.choose_button = QPushButton("Escolher pasta...")
        self.refresh_button = QPushButton("Atualizar")
        self.table = FileTableView()
        self.simulate_button = QPushButton("Simular")
        self.organize_button = QPushButton("Organizar")
        self.summary = QLabel()
        self._build_layout()

        self.choose_button.clicked.connect(self.choose_folder)
        self.refresh_button.clicked.connect(self.refresh)
        self.simulate_button.clicked.connect(self.simulate)
        self._show_empty()

    def _build_layout(self) -> None:
        folder_bar = QHBoxLayout()
        folder_bar.addWidget(self.folder_edit, 1)
        folder_bar.addWidget(self.choose_button)
        folder_bar.addWidget(self.refresh_button)
        action_bar = QHBoxLayout()
        action_bar.addWidget(self.simulate_button)
        action_bar.addWidget(self.organize_button)
        action_bar.addStretch(1)
        layout = QVBoxLayout(self)
        layout.addLayout(folder_bar)
        layout.addWidget(self.table, 1)
        layout.addLayout(action_bar)
        layout.addWidget(self.summary)

    # -- estados ---------------------------------------------------------

    def _set_mode(self, mode: str) -> None:
        self.mode = mode
        self._update_buttons()

    def _update_buttons(self) -> None:
        actionable = self.mode in _ACTIONABLE
        has_operations = self.plan is not None and not self.plan.is_empty
        self.choose_button.setEnabled(self.mode not in _BUSY)
        self.refresh_button.setEnabled(self.folder is not None and self.mode not in _BUSY)
        self.simulate_button.setEnabled(actionable)
        self.organize_button.setEnabled(actionable and has_operations)

    def _show_empty(self) -> None:
        self.table.set_rows([], None)
        self.summary.setText(_CHOOSE_FOLDER)
        self._set_mode(MODE_EMPTY)

    def _show_error(self, error: FilePilotError) -> None:
        self.files = []
        self.plan = None
        self.table.set_rows([], None)
        self.summary.setText(error.message)
        self._set_mode(MODE_ERROR)

    def _show_listed(self) -> None:
        # Em `listado` a tabela mostra a categoria prevista, sem o destino.
        self.table.set_rows(self.files, self.plan, show_destination=False)
        self.summary.setText(f"{len(self.files)} arquivos na pasta")
        self._set_mode(MODE_LISTED)

    def _show_simulated(self, plan: Plan) -> None:
        self.table.set_rows(self.files, plan, show_destination=True)
        if plan.is_empty:
            self.summary.setText(_NO_OPERATIONS)
        else:
            self.summary.setText(
                f"Simulação: {len(plan.operations)} operações. {_NOT_CHANGED}"
            )
        self._set_mode(MODE_SIMULATED)

    # -- leitura da pasta ------------------------------------------------

    def _read_folder(self, folder: Path) -> Plan | None:
        """Le a pasta e recalcula o plano com as regras atuais; None em erro."""
        self.summary.setText(_LOADING)
        self._set_mode(MODE_LOADING)
        QCoreApplication.processEvents()
        try:
            files = scan_folder(folder)
            plan = build_plan(folder, files, list_rules(self._conn))
        except FilePilotError as error:
            self._show_error(error)
            return None
        except OSError:
            # O texto bruto da excecao fica so na cadeia de excecoes.
            self._show_error(FilePilotError("PASTA_ILEGIVEL", _UNREADABLE))
            return None
        self.files = files
        self.plan = plan
        return plan

    # -- eventos ---------------------------------------------------------

    def choose_folder(self) -> None:
        """Abre o seletor; cancelar mantem tudo como estava."""
        chosen = QFileDialog.getExistingDirectory(self, _FILE_DIALOG_TITLE)
        if not chosen:
            return
        self.folder = Path(chosen)
        self.folder_edit.setText(str(self.folder))
        self.refresh()

    def refresh(self) -> None:
        """Le a pasta de novo, recalcula o plano e descarta a simulacao exibida."""
        if self.folder is None:
            return
        if self._read_folder(self.folder) is not None:
            self._show_listed()

    def simulate(self) -> None:
        """Le a pasta e recalcula o plano com as regras atuais, sem alterar o disco."""
        if self.folder is None:
            return
        plan = self._read_folder(self.folder)
        if plan is not None:
            self._show_simulated(plan)
