"""Aba Organizar: pasta, lista, simulacao, organizacao com progresso e desfazer (SPEC 7.2)."""

import sqlite3
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QThread, Signal
from PySide6.QtGui import QShowEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import OrganizationResult, Plan, ScannedFile
from filepilot.services.history import OrganizationRow, last_undoable
from filepilot.services.planner import build_plan
from filepilot.services.rules import list_rules
from filepilot.services.scanner import scan_folder
from filepilot.services.undo import UndoResult
from filepilot.ui.file_table import FileTableView
from filepilot.ui.organize_worker import OrganizeWorker, UndoWorker, run_in_thread

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
_PROGRESS_FORMAT = "%v de %m arquivos"
_ERROR_TITLE = "FilePilot"
_FOLDER_CHANGED = (
    "A pasta mudou desde a simulação. "
    "Confira a nova simulação e clique em Organizar de novo."
)
# Texto de PASTA_ILEGIVEL (SPEC 6); repetido aqui porque a ui nao importa o
# dicionario privado do scanner. Um teste compara os dois.
_UNREADABLE = "Não foi possível ler a pasta escolhida."
# Texto de BANCO_INDISPONIVEL (SPEC 6), repetido pelo mesmo motivo de `_UNREADABLE`.
_DATABASE_UNAVAILABLE = "Não foi possível acessar o histórico do FilePilot."

# Estados em que ha uma lista valida na tabela e a pessoa pode agir sobre ela.
_ACTIONABLE = (MODE_LISTED, MODE_SIMULATED)
# Estados em que a leitura da pasta ou a organizacao esta em andamento.
_BUSY = (MODE_LOADING, MODE_ORGANIZING)


def _signature(plan: Plan | None) -> list[tuple[Path, Path, str | None]]:
    """O que a pessoa confere na simulacao: origem, destino e regra, na ordem."""
    if plan is None:
        return []
    return [
        (operation.source_path, operation.destination_path, operation.rule_name)
        for operation in plan.operations
    ]


class OrganizeTab(QWidget):
    """Mostra a pasta e o plano, simula e executa a organizacao com progresso.

    `db_path` e o caminho do banco que a janela guarda (SPEC 7.1): o worker abre
    a propria conexao nele, porque a de `conn` nao atravessa threads.
    """

    organization_finished = Signal(int)
    # "Ver detalhes": pede a janela que abra o Historico nesta organizacao.
    details_requested = Signal(int)
    # Verdadeiro enquanto a organizacao ou o desfazer rodam; a janela o espelha em
    # `organizing`, que tambem impede fechar a janela com a thread viva.
    organizing_changed = Signal(bool)

    def __init__(self, conn: sqlite3.Connection, db_path: Path | None = None) -> None:
        super().__init__()
        self._conn = conn
        self._db_path = db_path
        self.folder: Path | None = None
        self.files: list[ScannedFile] = []
        self.plan: Plan | None = None
        self.mode = MODE_EMPTY
        self._last_organization_id: int | None = None
        # Ultima organizacao desfazivel (6.4); `None` desabilita "Desfazer".
        self._undoable: OrganizationRow | None = None
        self._undoing = False
        self._undo_folder: Path | None = None
        self._thread: QThread | None = None
        # O Python apaga o worker se ninguem guardar a referencia enquanto ele roda.
        self._worker: OrganizeWorker | UndoWorker | None = None

        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.choose_button = QPushButton("Escolher pasta...")
        self.refresh_button = QPushButton("Atualizar")
        self.table = FileTableView()
        self.simulate_button = QPushButton("Simular")
        self.organize_button = QPushButton("Organizar")
        self.undo_button = QPushButton("Desfazer última organização")
        self.progress = QProgressBar()
        self.progress.setFormat(_PROGRESS_FORMAT)
        self.progress.setVisible(False)
        self.summary = QLabel()
        self.details_button = QPushButton("Ver detalhes")
        self.details_button.setVisible(False)
        self._build_layout()

        self.choose_button.clicked.connect(self.choose_folder)
        self.refresh_button.clicked.connect(self.refresh)
        self.simulate_button.clicked.connect(self.simulate)
        self.organize_button.clicked.connect(self.organize)
        self.undo_button.clicked.connect(self.undo)
        self.details_button.clicked.connect(self._on_details_clicked)
        self._show_empty()
        self.refresh_undo()

    def _build_layout(self) -> None:
        folder_bar = QHBoxLayout()
        folder_bar.addWidget(self.folder_edit, 1)
        folder_bar.addWidget(self.choose_button)
        folder_bar.addWidget(self.refresh_button)
        action_bar = QHBoxLayout()
        action_bar.addWidget(self.simulate_button)
        action_bar.addWidget(self.organize_button)
        action_bar.addWidget(self.undo_button)
        action_bar.addStretch(1)
        summary_bar = QHBoxLayout()
        summary_bar.addWidget(self.summary)
        summary_bar.addWidget(self.details_button)
        summary_bar.addStretch(1)
        layout = QVBoxLayout(self)
        layout.addLayout(folder_bar)
        layout.addWidget(self.table, 1)
        layout.addLayout(action_bar)
        layout.addWidget(self.progress)
        layout.addLayout(summary_bar)

    # -- estados ---------------------------------------------------------

    def _set_mode(self, mode: str) -> None:
        self.mode = mode
        self._update_buttons()

    def _update_buttons(self) -> None:
        busy = self.mode in _BUSY or self._undoing
        actionable = self.mode in _ACTIONABLE and not self._undoing
        has_operations = self.plan is not None and not self.plan.is_empty
        self.choose_button.setEnabled(not busy)
        self.refresh_button.setEnabled(self.folder is not None and not busy)
        self.simulate_button.setEnabled(actionable)
        self.organize_button.setEnabled(actionable and has_operations)
        self.undo_button.setEnabled(
            self._undoable is not None and self.mode != MODE_ORGANIZING and not self._undoing
        )

    def refresh_undo(self) -> None:
        """Reavalia `last_undoable` e habilita ou desabilita "Desfazer" (7.2)."""
        try:
            self._undoable = last_undoable(self._conn)
        except FilePilotError:
            # Sem historico legivel nao ha o que desfazer; a aba Historico mostra o erro.
            self._undoable = None
        self._update_buttons()

    def showEvent(self, event: QShowEvent) -> None:  # noqa: N802 - nome do Qt
        """Ao abrir a aba, reavalia o botao Desfazer."""
        super().showEvent(event)
        self.refresh_undo()

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

    def _read_folder(self, folder: Path, empty_ok: bool = False) -> Plan | None:
        """Le a pasta e recalcula o plano com as regras atuais; None em erro.

        Com `empty_ok`, pasta sem arquivos nao e erro: e o estado normal depois
        de organizar tudo, e vira uma lista vazia com plano vazio.
        """
        self.summary.setText(_LOADING)
        self._set_mode(MODE_LOADING)
        QCoreApplication.processEvents()
        try:
            files = scan_folder(folder)
            plan = build_plan(folder, files, list_rules(self._conn))
        except FilePilotError as error:
            if empty_ok and error.code == "PASTA_VAZIA":
                self.files = []
                self.plan = Plan(folder)
                return self.plan
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
        self.progress.setVisible(False)
        self.details_button.setVisible(False)
        if self._read_folder(self.folder) is not None:
            self._show_listed()

    def simulate(self) -> None:
        """Le a pasta e recalcula o plano com as regras atuais, sem alterar o disco."""
        if self.folder is None:
            return
        self.progress.setVisible(False)
        plan = self._read_folder(self.folder)
        if plan is not None:
            self._show_simulated(plan)

    def organize(self) -> None:
        """Le a pasta de novo, confere com a simulacao exibida e executa o plano."""
        if self.folder is None:
            return
        self.progress.setVisible(False)
        self.details_button.setVisible(False)
        previous_mode = self.mode
        shown = _signature(self.plan)
        plan = self._read_folder(self.folder)
        if plan is None:
            return
        if plan.is_empty:
            if previous_mode == MODE_SIMULATED:
                self._show_simulated(plan)
            else:
                self._show_listed()
                self.summary.setText(_NO_OPERATIONS)
            return
        if previous_mode == MODE_SIMULATED and _signature(plan) != shown:
            self._show_simulated(plan)
            self.summary.setText(_FOLDER_CHANGED)
            return
        self._start_organization(plan)

    def _start_organization(self, plan: Plan) -> None:
        """Dispara o `OrganizeWorker` em uma `QThread`, com a barra zerada."""
        if self._db_path is None:
            self._on_failed("BANCO_INDISPONIVEL", _DATABASE_UNAVAILABLE)
            return
        worker = OrganizeWorker(plan, self._db_path)
        worker.progress.connect(self._on_progress)
        worker.finished.connect(self._on_finished)
        worker.failed.connect(self._on_failed)
        self.progress.setRange(0, len(plan.operations))
        self.progress.setValue(0)
        self.progress.setVisible(True)
        self.summary.setText("")
        self._set_mode(MODE_ORGANIZING)
        self.organizing_changed.emit(True)
        self._worker = worker
        self._thread = run_in_thread(worker)

    def _release_worker(self) -> None:
        """Espera a thread acabar e solta o worker e a thread."""
        if self._thread is not None:
            # O `quit` direto de `run_in_thread` ja rodou quando o sinal chegou aqui.
            self._thread.wait()
            self._thread = None
        self._worker = None

    def _on_progress(self, done: int, total: int, filename: str) -> None:
        self.progress.setRange(0, total)
        self.progress.setValue(done)

    def _on_finished(self, result: OrganizationResult) -> None:
        """Fecha a barra, relê a pasta e avisa que a organizacao terminou."""
        self._release_worker()
        self.progress.setValue(self.progress.maximum())
        if self.folder is not None and self._read_folder(self.folder, empty_ok=True) is not None:
            self._show_listed()
            self.summary.setText(
                f"Concluído: {result.moved_count} movidos, {result.failed_count} falhas."
            )
        self._last_organization_id = result.organization_id
        self.details_button.setVisible(result.failed_count > 0)
        self.refresh_undo()
        self.organizing_changed.emit(False)
        self.organization_finished.emit(result.organization_id)

    def _on_details_clicked(self) -> None:
        if self._last_organization_id is not None:
            self.details_requested.emit(self._last_organization_id)

    def _on_failed(self, code: str, message: str) -> None:
        """Mostra o erro de contrato ou o inesperado e deixa a janela aberta."""
        self._release_worker()
        self.organizing_changed.emit(False)
        self._show_error(FilePilotError(code, message))
        # Uma organizacao interrompida ja pode ser desfeita.
        self.refresh_undo()
        QMessageBox.critical(self, _ERROR_TITLE, message)

    # -- desfazer --------------------------------------------------------

    def undo(self) -> None:
        """Desfaz a ultima organizacao em uma `QThread`, sem pedir confirmacao."""
        undoable = self._undoable
        if undoable is None or self._undoing or self.mode == MODE_ORGANIZING:
            return
        if self._db_path is None:
            self.summary.setText(_DATABASE_UNAVAILABLE)
            return
        worker = UndoWorker(self._db_path)
        worker.finished.connect(self._on_undone)
        worker.failed.connect(self._on_undo_failed)
        self._undo_folder = Path(undoable.folder_path)
        self._undoing = True
        self._update_buttons()
        self.organizing_changed.emit(True)
        self._worker = worker
        self._thread = run_in_thread(worker)

    def _on_undone(self, result: UndoResult) -> None:
        """Mostra o resumo, relê a pasta se era a atual e reavalia o botao."""
        self._release_worker()
        self._undoing = False
        message = f"Desfeito: {result.restored_count} arquivos restaurados."
        if result.not_restored:
            paths = ", ".join(path for path, _ in result.not_restored)
            message = f"{message} Não restaurados: {paths}"
        if self.folder is not None and self._undo_folder == self.folder:
            if self._read_folder(self.folder, empty_ok=True) is not None:
                self._show_listed()
                self.summary.setText(message)
        else:
            self.summary.setText(message)
        self.refresh_undo()
        self.organizing_changed.emit(False)

    def _on_undo_failed(self, code: str, message: str) -> None:
        """Mostra a mensagem do erro de contrato no resumo e reavalia o botao."""
        self._release_worker()
        self._undoing = False
        self.summary.setText(message)
        self.refresh_undo()
        self.organizing_changed.emit(False)
