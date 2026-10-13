"""Leitura do nivel da pasta escolhida (SPEC 6.1)."""

import ctypes
import errno
import os
import stat
import sys
from pathlib import Path

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import ScannedFile

_MESSAGES = {
    "PASTA_INVALIDA": "A pasta escolhida não existe ou não é uma pasta.",
    "PASTA_ILEGIVEL": "Não foi possível ler a pasta escolhida.",
    "PASTA_VAZIA": "A pasta escolhida não tem arquivos para organizar.",
    "PASTA_PROTEGIDA": "Esta pasta é protegida e não pode ser organizada. Escolha outra pasta.",
}

_HIDDEN_OR_SYSTEM = stat.FILE_ATTRIBUTE_HIDDEN | stat.FILE_ATTRIBUTE_SYSTEM

# Variavel de ambiente e valor padrao das pastas do sistema e de programas (6.1).
_PROTECTED_ENV = (
    ("SystemRoot", r"C:\Windows"),
    ("ProgramFiles", r"C:\Program Files"),
    ("ProgramFiles(x86)", r"C:\Program Files (x86)"),
)

_DRIVE_REMOTE = 4
_DRIVE_UNKNOWN = 0

# ERROR_CANT_RESOLVE_FILENAME: laco de atalhos no Windows.
_WINERROR_CANT_RESOLVE = 1921

# Limite de saltos de link da travessia (MAXSYMLINKS do Linux).
_MAX_SYMLINK_HOPS = 40


def _error(code: str) -> FilePilotError:
    return FilePilotError(code, _MESSAGES[code])


def _read_stat(path: Path) -> os.stat_result:
    """Le os metadados sem seguir link simbolico."""
    return os.stat(path, follow_symlinks=False)


def _drive_type(anchor: str) -> int:
    """Tipo da unidade pelo GetDriveTypeW; fora do Windows nao ha verificacao."""
    if sys.platform != "win32":
        return _DRIVE_UNKNOWN
    return int(ctypes.windll.kernel32.GetDriveTypeW(anchor))


def _crosses_symlink_loop(path: Path) -> bool:
    """True se a travessia passa de 40 saltos de link (45.4); nunca levanta."""
    absolute = path if path.is_absolute() else Path.cwd() / path
    current = Path(absolute.anchor)
    pending = list(reversed(absolute.parts[1:]))
    hops = 0
    try:
        while pending:
            part = pending.pop()
            if part == "..":
                current = current.parent
                continue
            candidate = current / part
            if not candidate.is_symlink():
                current = candidate
                continue
            hops += 1
            if hops > _MAX_SYMLINK_HOPS:
                return True
            target = Path(os.readlink(candidate))
            if target.is_absolute():
                current = Path(target.anchor)
                pending.extend(reversed(target.parts[1:]))
            else:
                pending.extend(reversed(target.parts))
    except OSError:
        return False
    return False


def resolve_folder(folder: Path) -> Path:
    """Resolve a pasta uma unica vez; laco de atalhos vira PASTA_INVALIDA (27.2, 45.4)."""
    try:
        resolved = folder.resolve()
    except RuntimeError as exc:
        raise _error("PASTA_INVALIDA") from exc
    except OSError as exc:
        if exc.errno == errno.ELOOP or getattr(exc, "winerror", None) == _WINERROR_CANT_RESOLVE:
            raise _error("PASTA_INVALIDA") from exc
        raise
    if _crosses_symlink_loop(folder):
        raise _error("PASTA_INVALIDA")
    return resolved


def _protected_root(variable: str, default: str) -> Path:
    """Raiz protegida da variavel de ambiente; ausente, vazia ou so espacos vale o padrao (27.3)."""
    value = os.environ.get(variable)
    if value is None or value.strip() == "":
        value = default
    return Path(value).resolve()


def _is_protected(folder: Path, resolved: Path) -> bool:
    """Raiz de unidade, pasta do sistema ou de programas (ou dentro delas) e pasta de rede."""
    if str(folder).startswith("\\\\"):
        return True
    if resolved == Path(resolved.anchor):
        return True
    for variable, default in _PROTECTED_ENV:
        root = _protected_root(variable, default)
        if resolved == root or root in resolved.parents:
            return True
    return _drive_type(resolved.anchor) == _DRIVE_REMOTE


def _extension(name: str) -> str:
    """Extensao em minusculas, sem ponto; vazia para `.gitignore` e `arquivo.`."""
    stem, dot, ext = name.rpartition(".")
    if not dot or not stem:
        return ""
    return ext.lower()


def _scan_entry(path: Path) -> ScannedFile | None:
    """Devolve o arquivo elegivel ou None (nao regular, oculto, de sistema ou ilegivel)."""
    try:
        info = _read_stat(path)
    except OSError:
        return None
    if not stat.S_ISREG(info.st_mode):
        return None
    if getattr(info, "st_file_attributes", 0) & _HIDDEN_OR_SYSTEM:
        return None
    return ScannedFile(
        path=path,
        name=path.name,
        extension=_extension(path.name),
        size_bytes=info.st_size,
    )


def scan_folder(folder: Path) -> list[ScannedFile]:
    """Lista os arquivos elegiveis do nivel da pasta, ordenados por nome (6.1)."""
    if str(folder).startswith("\\\\"):
        raise _error("PASTA_PROTEGIDA")
    resolved = resolve_folder(folder)
    if _is_protected(folder, resolved):
        raise _error("PASTA_PROTEGIDA")
    if not folder.is_dir():
        raise _error("PASTA_INVALIDA")
    try:
        entries = list(folder.iterdir())
    except OSError as exc:
        raise _error("PASTA_ILEGIVEL") from exc
    files = [item for item in map(_scan_entry, entries) if item is not None]
    if not files:
        raise _error("PASTA_VAZIA")
    files.sort(key=lambda item: (item.name.casefold(), item.name))
    return files
