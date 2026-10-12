"""Worker da organizacao: roda `organize` fora da thread da interface (SPEC 7.2).

O servico `organize` nunca importa PySide6 (SPEC 3.2); so este modulo liga o
`progress_callback` dele a um sinal Qt. A conexao SQLite nao atravessa threads,
entao o worker abre a propria a partir do caminho do banco.
"""

from pathlib import Path

from PySide6.QtCore import QObject, Qt, QThread, Signal, Slot

from filepilot.db.connection import open_connection
from filepilot.domain.models import Plan
from filepilot.services.organizer import internal_error, organize
from filepilot.services.undo import undo_last


class OrganizeWorker(QObject):
    """Executa o plano e avisa o progresso, o resultado ou a falha por sinais."""

    progress = Signal(int, int, str)
    finished = Signal(object)
    failed = Signal(str, str)

    def __init__(self, plan: Plan, db_path: Path) -> None:
        super().__init__()
        self._plan = plan
        self._db_path = db_path

    @Slot()
    def run(self) -> None:
        """Organiza o plano; termina sempre com `finished` ou com `failed`."""
        try:
            conn = open_connection(self._db_path)
            try:
                result = organize(self._plan, conn, self.progress.emit)
            finally:
                conn.close()
        except Exception as exc:
            # Qualquer falha vira `failed`; so o erro de contrato chega a pessoa.
            error = internal_error(exc)
            self.failed.emit(error.code, error.message)
            return
        self.finished.emit(result)


class UndoWorker(QObject):
    """Desfaz a ultima organizacao fora da thread da interface (SPEC 7.2).

    Abre a propria conexao pelo mesmo motivo do `OrganizeWorker`. `undo_last`
    pega o `OPERATION_LOCK` sem bloquear e levanta `ORGANIZACAO_EM_ANDAMENTO`.
    """

    finished = Signal(object)
    failed = Signal(str, str)

    def __init__(self, db_path: Path) -> None:
        super().__init__()
        self._db_path = db_path

    @Slot()
    def run(self) -> None:
        """Desfaz; termina sempre com `finished` ou com `failed`."""
        try:
            conn = open_connection(self._db_path)
            try:
                result = undo_last(conn)
            finally:
                conn.close()
        except Exception as exc:
            error = internal_error(exc)
            self.failed.emit(error.code, error.message)
            return
        self.finished.emit(result)


def run_in_thread(worker: OrganizeWorker | UndoWorker) -> QThread:
    """Move o worker para uma `QThread` nova, inicia e devolve a thread.

    A thread termina sozinha quando o worker emite `finished` ou `failed`: o
    `quit` e ligado de forma direta, para rodar na propria thread do worker e
    nunca ficar na fila de uma thread de interface que ja esta em `wait`.
    Quem chama guarda as referencias ao worker e a thread, espera a thread
    acabar (`wait`) e so entao as solta: apagar qualquer um dos dois com a
    thread rodando derruba o processo.
    """
    thread = QThread()
    worker.moveToThread(thread)
    thread.started.connect(worker.run)
    worker.finished.connect(thread.quit, Qt.ConnectionType.DirectConnection)
    worker.failed.connect(thread.quit, Qt.ConnectionType.DirectConnection)
    thread.start()
    return thread
