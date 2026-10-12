import ctypes
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from filepilot.domain.errors import FilePilotError
from filepilot.services import scanner
from filepilot.services.scanner import scan_folder

PROTECTED_MESSAGE = "Esta pasta é protegida e não pode ser organizada. Escolha outra pasta."

ENV_VARIABLES = ["SystemRoot", "ProgramFiles", "ProgramFiles(x86)"]


def _assert_protected(folder: Path) -> None:
    with pytest.raises(FilePilotError) as info:
        scan_folder(folder)

    assert info.value.code == "PASTA_PROTEGIDA"
    assert info.value.message == PROTECTED_MESSAGE


def test_raiz_de_unidade_e_protegida() -> None:
    _assert_protected(Path(Path.cwd().anchor))


def test_pasta_protegida_e_recusada_antes_de_listar(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_listing(self: Path) -> Any:
        raise AssertionError("listou uma pasta protegida")

    monkeypatch.setattr(Path, "iterdir", fail_listing)

    _assert_protected(Path(Path.cwd().anchor))


@pytest.mark.parametrize("variable", ENV_VARIABLES)
def test_pasta_das_variaveis_de_ambiente_e_protegida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variable: str
) -> None:
    root = tmp_path / "sistema"
    root.mkdir()
    (root / "arquivo.txt").write_bytes(b"x")
    monkeypatch.setenv(variable, str(root))

    _assert_protected(root)


@pytest.mark.parametrize("variable", ENV_VARIABLES)
def test_pasta_dentro_das_variaveis_de_ambiente_e_protegida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variable: str
) -> None:
    root = tmp_path / "sistema"
    inner = root / "a" / "b"
    inner.mkdir(parents=True)
    (inner / "arquivo.txt").write_bytes(b"x")
    monkeypatch.setenv(variable, str(root))

    _assert_protected(root / "a")
    _assert_protected(inner)


@pytest.mark.parametrize(
    ("variable", "default"),
    [
        ("SystemRoot", r"C:\Windows"),
        ("ProgramFiles", r"C:\Program Files"),
        ("ProgramFiles(x86)", r"C:\Program Files (x86)"),
    ],
)
def test_padrao_quando_a_variavel_esta_ausente(
    monkeypatch: pytest.MonkeyPatch, variable: str, default: str
) -> None:
    monkeypatch.delenv(variable, raising=False)

    _assert_protected(Path(default))


def test_pasta_fora_das_protegidas_e_listada(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    protegida = tmp_path / "sistema"
    protegida.mkdir()
    livre = tmp_path / "livre"
    livre.mkdir()
    (livre / "a.txt").write_bytes(b"x")
    monkeypatch.setenv("SystemRoot", str(protegida))

    assert [item.name for item in scan_folder(livre)] == ["a.txt"]


@pytest.mark.parametrize("value", ["", "   "])
@pytest.mark.parametrize("variable", ENV_VARIABLES)
def test_variavel_vazia_ou_so_espacos_vale_como_ausente(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, variable: str, value: str
) -> None:
    pasta = tmp_path / "pasta"
    pasta.mkdir()
    (pasta / "a.txt").write_bytes(b"x")
    monkeypatch.setenv(variable, value)
    monkeypatch.chdir(tmp_path)

    assert [item.name for item in scan_folder(pasta)] == ["a.txt"]


@pytest.mark.parametrize("value", ["", "   "])
def test_raiz_protegida_vazia_usa_o_padrao_e_nao_a_pasta_atual(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv("SystemRoot", value)
    monkeypatch.chdir(tmp_path)

    root = scanner._protected_root("SystemRoot", r"C:\Windows")

    assert root == Path(r"C:\Windows").resolve()
    assert root != tmp_path.resolve()


def test_raiz_protegida_com_valor_definido_e_resolvida_como_esta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SystemRoot", str(tmp_path))

    assert scanner._protected_root("SystemRoot", r"C:\Windows") == tmp_path.resolve()


def test_caminho_unc_e_protegido() -> None:
    _assert_protected(Path(r"\\servidor\pasta"))


def test_unidade_de_rede_simulada_e_protegida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a.txt").write_bytes(b"x")
    anchors: list[str] = []

    def fake_drive_type(anchor: str) -> int:
        anchors.append(anchor)
        return 4

    monkeypatch.setattr(scanner, "_drive_type", fake_drive_type)

    _assert_protected(tmp_path)
    assert anchors == [tmp_path.resolve().anchor]


def test_unidade_local_simulada_e_aceita(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "a.txt").write_bytes(b"x")
    monkeypatch.setattr(scanner, "_drive_type", lambda anchor: 3)

    assert [item.name for item in scan_folder(tmp_path)] == ["a.txt"]


def test_drive_type_chama_get_drive_type_w_no_windows(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    def fake_get_drive_type(anchor: str) -> int:
        calls.append(anchor)
        return 4

    fake_windll = SimpleNamespace(kernel32=SimpleNamespace(GetDriveTypeW=fake_get_drive_type))
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(ctypes, "windll", fake_windll, raising=False)

    assert scanner._drive_type("Z:\\") == 4
    assert calls == ["Z:\\"]


@pytest.mark.skipif(sys.platform == "win32", reason="so vale fora do Windows")
def test_fora_do_windows_a_verificacao_de_unidade_e_ignorada(tmp_path: Path) -> None:
    (tmp_path / "a.txt").write_bytes(b"x")

    assert scanner._drive_type(tmp_path.resolve().anchor) == 0
    assert [item.name for item in scan_folder(tmp_path)] == ["a.txt"]


@pytest.mark.skipif(sys.platform != "win32", reason="so vale no Windows")
def test_unidade_do_sistema_no_windows_nao_e_de_rede() -> None:
    assert scanner._drive_type(Path.cwd().anchor) != 4
