"""Ponto de entrada: `python -m filepilot` (SPEC 7.1)."""

import sys
from pathlib import Path

from PySide6.QtCore import QLockFile, QStandardPaths
from PySide6.QtWidgets import QApplication, QMessageBox

from filepilot import __version__
from filepilot.domain.errors import FilePilotError
from filepilot.ui.main_window import MainWindow

APP_NAME = "FilePilot"
DB_FILE_NAME = "filepilot.db"
LOCK_FILE_NAME = "filepilot.lock"
# Trava deixada por um processo que caiu e recuperada na abertura seguinte.
STALE_LOCK_TIME_MS = 30_000
_ALREADY_OPEN = "O FilePilot já está aberto."
_DB_UNAVAILABLE = "Não foi possível acessar o histórico do FilePilot."
_LOCK_HELD_BY_OTHER = QLockFile.LockError.LockFailedError
_LOCK_UNAVAILABLE = (
    "Não foi possível verificar se o FilePilot já está aberto. "
    "Confira se você tem permissão para usar a pasta de dados do aplicativo."
)
_USAGE: str = (
    "uso: python -m filepilot [--help | -h | --version | -V]\n"
    "opções:\n"
    "  --help, -h     mostra esta ajuda e sai\n"
    "  --version, -V  mostra a versão e sai"
)


def default_data_dir() -> Path:
    """Pasta de dados do aplicativo no perfil da pessoa (SPEC 5.1)."""
    location = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppDataLocation
    )
    return Path(location)


def open_main_window(data_dir: Path) -> MainWindow | int:
    """Toma a trava de instancia unica, abre o banco e cria a janela.

    Devolve a janela, ou o codigo de saida quando o aplicativo nao deve abrir:
    0 com outra instancia aberta (sem tocar no banco) e 1 com a trava
    inverificavel ou o banco inacessivel.
    """
    try:
        data_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        QMessageBox.critical(None, APP_NAME, _DB_UNAVAILABLE)
        return 1
    lock = QLockFile(str(data_dir / LOCK_FILE_NAME))
    lock.setStaleLockTime(STALE_LOCK_TIME_MS)
    if not lock.tryLock(0):
        if lock.error() == _LOCK_HELD_BY_OTHER:
            QMessageBox.information(None, APP_NAME, _ALREADY_OPEN)
            return 0
        QMessageBox.critical(None, APP_NAME, _LOCK_UNAVAILABLE)
        return 1
    try:
        return MainWindow(data_dir / DB_FILE_NAME, lock)
    except FilePilotError:
        lock.unlock()
        QMessageBox.critical(None, APP_NAME, _DB_UNAVAILABLE)
        return 1


def main() -> int:
    if sys.argv[1:] in (["--version"], ["-V"]):
        print(__version__)
        return 0
    if sys.argv[1:] in (["--help"], ["-h"]):
        print(_USAGE)
        return 0
    app = QApplication(sys.argv)
    app.setApplicationName("FilePilot")
    result = open_main_window(default_data_dir())
    if isinstance(result, int):
        return result
    result.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
