import errno
import os
import sys
from collections.abc import Callable
from pathlib import Path

import pytest

from filepilot.domain.errors import FilePilotError
from filepilot.services import scanner
from filepilot.services.scanner import _crosses_symlink_loop, scan_folder

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
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        if sys.platform == "win32" and os.environ.get("GITHUB_ACTIONS") == "true":
            pytest.fail("o sistema recusou criar o link simbolico")
        pytest.skip("o sistema recusou criar o link simbolico")


def _windows_resolve(self: Path, strict: bool = False) -> Path:
    """Emula o Path.resolve do Windows, que nao enxerga o laco e devolve o caminho como veio."""
    return self


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


def test_pasta_que_aponta_para_si_mesma_com_resolve_do_windows_vira_pasta_invalida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "laco"
    _symlink(folder, folder)
    monkeypatch.setattr(Path, "resolve", _windows_resolve)

    with pytest.raises(FilePilotError) as info:
        scan_folder(folder)

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE
    assert info.value.__cause__ is None


def test_ciclo_de_dois_atalhos_com_resolve_do_windows_vira_pasta_invalida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    _symlink(a, b)
    _symlink(b, a)
    monkeypatch.setattr(Path, "resolve", _windows_resolve)

    with pytest.raises(FilePilotError) as info:
        scan_folder(a)

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE


def test_atalho_valido_com_resolve_do_windows_lista_os_arquivos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real = tmp_path / "real"
    real.mkdir()
    (real / "a.txt").write_bytes(b"x")
    link = tmp_path / "atalho"
    _symlink(link, real)
    monkeypatch.setattr(Path, "resolve", _windows_resolve)

    assert [item.name for item in scan_folder(link)] == ["a.txt"]


def test_resolve_que_levanta_runtime_error_nao_chama_a_travessia(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "laco"
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(folder, RuntimeError("Symlink loop")))
    calls: list[Path] = []

    def spy(path: Path) -> bool:
        calls.append(path)
        return False

    monkeypatch.setattr(scanner, "_crosses_symlink_loop", spy)

    with pytest.raises(FilePilotError) as info:
        scan_folder(folder)

    assert info.value.code == "PASTA_INVALIDA"
    assert isinstance(info.value.__cause__, RuntimeError)
    assert calls == []


def test_travessia_depois_de_resolve_sem_erro_levanta_pasta_invalida_sem_causa(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "pasta"
    folder.mkdir()
    calls: list[Path] = []

    def spy(path: Path) -> bool:
        calls.append(path)
        return True

    monkeypatch.setattr(scanner, "_crosses_symlink_loop", spy)

    with pytest.raises(FilePilotError) as info:
        scan_folder(folder)

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.__cause__ is None
    assert calls == [folder]


def test_travessia_devolve_true_para_atalho_que_aponta_para_si_mesmo(tmp_path: Path) -> None:
    link = tmp_path / "link"
    _symlink(link, link)

    assert _crosses_symlink_loop(link) is True
    assert _crosses_symlink_loop(link / "dentro") is True


def test_travessia_devolve_true_para_o_ciclo_a_b_a(tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    _symlink(a, b)
    _symlink(b, a)

    assert _crosses_symlink_loop(a) is True


def test_travessia_devolve_false_para_atalho_valido_e_caminho_inexistente(
    tmp_path: Path,
) -> None:
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink(link, real)

    assert _crosses_symlink_loop(link) is False
    assert _crosses_symlink_loop(link / "nao_existe" / "sub") is False
    assert _crosses_symlink_loop(tmp_path / "nao_existe") is False


def test_travessia_acompanha_atalho_relativo_e_ponto_ponto(tmp_path: Path) -> None:
    (tmp_path / "real").mkdir()
    (tmp_path / "sub").mkdir()
    _symlink(tmp_path / "sub" / "volta", Path("..") / "sub" / "volta")

    assert _crosses_symlink_loop(tmp_path / "sub" / "volta") is True
    assert _crosses_symlink_loop(tmp_path / "sub" / ".." / "real") is False


def test_travessia_conta_so_os_saltos_de_atalho_e_passa_de_40_devolve_true(
    tmp_path: Path,
) -> None:
    (tmp_path / "fim").mkdir()
    for number in range(41):
        target = tmp_path / ("fim" if number == 40 else f"l{number + 1}")
        _symlink(tmp_path / f"l{number}", target)

    assert _crosses_symlink_loop(tmp_path / "l1") is False
    assert _crosses_symlink_loop(tmp_path / "l0") is True


def test_travessia_com_readlink_negado_devolve_false_sem_levantar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    link = tmp_path / "link"
    _symlink(link, link)

    def fake_readlink(path: str | os.PathLike[str]) -> str:
        raise OSError(errno.EACCES, "Permission denied")

    monkeypatch.setattr(os, "readlink", fake_readlink)

    assert _crosses_symlink_loop(link) is False


def test_travessia_com_is_symlink_negado_devolve_false_sem_levantar(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fake_is_symlink(self: Path) -> bool:
        raise PermissionError(errno.EACCES, "Permission denied")

    monkeypatch.setattr(Path, "is_symlink", fake_is_symlink)

    assert _crosses_symlink_loop(tmp_path / "qualquer" / "coisa") is False


def test_pasta_com_link_para_o_pai_lista_so_arquivos_regulares(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_bytes(b"x")
    _symlink(tmp_path / "up", tmp_path.parent)

    assert [item.name for item in scan_folder(tmp_path)] == ["a.txt"]
