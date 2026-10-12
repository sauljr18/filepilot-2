"""Verificacoes de destino e textos de falha por arquivo (SPEC 6.7).

Usado por `organize` antes de mover cada arquivo. So le o disco: nao cria
pastas, nao move arquivos e nao toca no banco.
"""

import os
import stat
from pathlib import Path

# Decisao explicita (filepilot-v1-4): a guarda de pasta e a do planner; importar
# o helper evita duplicar a logica.
from filepilot.services.planner import _inside

MAX_PATH = 259

IN_USE = "arquivo em uso por outro programa"
NO_PERMISSION = "sem permissão para mover o arquivo"
NOT_FOUND = "arquivo não encontrado"
TOO_LONG = "caminho de destino muito longo"
SHORTCUT = "a subpasta de destino é um atalho"
OUTSIDE = "o destino fica fora da pasta escolhida"
MKDIR = "não foi possível criar a subpasta de destino"
OTHER = "erro ao mover o arquivo"

_WINERROR_IN_USE = 32


def _is_shortcut(path: Path) -> bool:
    """Link simbolico ou junction (6.7); caminho inexistente nao e atalho."""
    if not os.path.lexists(path):
        return False
    if path.is_symlink() or os.path.isjunction(path):
        return True
    attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    return bool(attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def has_shortcut(folder: Path, directory: Path) -> bool:
    """Algum nivel da subpasta de destino, abaixo da pasta escolhida, e atalho."""
    try:
        relative = directory.relative_to(folder)
    except ValueError:
        return False
    current = folder
    for part in relative.parts:
        current = current / part
        if _is_shortcut(current):
            return True
    return False


def check_destination(folder: Path, destination: Path) -> str | None:
    """Texto da falha da verificacao 1, 2 ou 3 de 6.7, nessa ordem; `None` se passa."""
    if len(str(destination)) > MAX_PATH:
        return TOO_LONG
    if has_shortcut(folder, destination.parent):
        return SHORTCUT
    if not _inside(folder, destination):
        return OUTSIDE
    return None


def failure_text(exc: OSError, creating: bool) -> str:
    """Texto amigavel da tabela de 6.7; nunca o texto bruto do sistema."""
    if getattr(exc, "winerror", None) == _WINERROR_IN_USE:
        return IN_USE
    if isinstance(exc, PermissionError):
        return NO_PERMISSION
    if creating:
        return MKDIR
    if isinstance(exc, FileNotFoundError):
        return NOT_FOUND
    return OTHER
