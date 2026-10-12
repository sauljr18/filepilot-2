import errno
from collections.abc import Callable
from pathlib import Path

import pytest

from filepilot.domain.errors import FilePilotError
from filepilot.services.scanner import scan_folder

INVALID_MESSAGE = "A pasta escolhida não existe ou não é uma pasta."

_original_resolve = Path.resolve


def _fail_resolve_for(target: Path, error: Exception) -> Callable[..., Path]:
    def fake_resolve(self: Path, strict: bool = False) -> Path:
        if self == target:
            raise error
        return _original_resolve(self, strict=strict)

    return fake_resolve


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError):
        pytest.skip("o sistema recusou criar o link simbolico")


def test_laco_de_atalhos_levantado_como_runtime_error_vira_pasta_invalida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "laco"
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(folder, RuntimeError("Symlink loop")))

    with pytest.raises(FilePilotError) as info:
        scan_folder(folder)

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE
    assert "Symlink loop" not in info.value.message
    assert isinstance(info.value.__cause__, RuntimeError)


def test_oserror_eloop_na_resolucao_vira_pasta_invalida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "laco"
    error = OSError(errno.ELOOP, "Too many levels of symbolic links")
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(folder, error))

    with pytest.raises(FilePilotError) as info:
        scan_folder(folder)

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE
    assert info.value.__cause__ is error


def test_oserror_eacces_na_resolucao_continua_sendo_oserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "negada"
    error = OSError(errno.EACCES, "Permission denied")
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(folder, error))

    with pytest.raises(OSError) as info:
        scan_folder(folder)

    assert not isinstance(info.value, FilePilotError)
    assert info.value is error


def test_laco_real_de_atalhos_vira_pasta_invalida(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    _symlink(a, b)
    _symlink(b, a)

    with pytest.raises(FilePilotError) as info:
        scan_folder(a)

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE


def test_pasta_com_link_para_o_pai_lista_so_arquivos_regulares(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_bytes(b"x")
    _symlink(tmp_path / "up", tmp_path.parent)

    assert [item.name for item in scan_folder(tmp_path)] == ["a.txt"]
