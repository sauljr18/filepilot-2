import os
import stat
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from filepilot.domain.errors import FilePilotError
from filepilot.services import scanner
from filepilot.services.scanner import scan_folder


def _touch(path: Path, content: bytes = b"x") -> Path:
    path.write_bytes(content)
    return path


def test_lista_so_arquivos_visiveis_ordenados_sem_diferenciar_maiusculas(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch(tmp_path / "banana.txt")
    _touch(tmp_path / "Cereja.txt")
    _touch(tmp_path / "abacaxi.txt")
    _touch(tmp_path / "oculto.txt")
    (tmp_path / "subpasta").mkdir()
    real_read_stat = scanner._read_stat

    def fake_read_stat(path: Path) -> Any:
        info = real_read_stat(path)
        if path.name == "oculto.txt":
            return SimpleNamespace(
                st_mode=info.st_mode,
                st_size=info.st_size,
                st_file_attributes=stat.FILE_ATTRIBUTE_HIDDEN,
            )
        return info

    monkeypatch.setattr(scanner, "_read_stat", fake_read_stat)

    files = scan_folder(tmp_path)

    assert [item.name for item in files] == ["abacaxi.txt", "banana.txt", "Cereja.txt"]


def test_arquivo_de_sistema_e_ignorado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch(tmp_path / "visivel.txt")
    _touch(tmp_path / "sistema.sys")
    real_read_stat = scanner._read_stat

    def fake_read_stat(path: Path) -> Any:
        info = real_read_stat(path)
        if path.name == "sistema.sys":
            return SimpleNamespace(
                st_mode=info.st_mode,
                st_size=info.st_size,
                st_file_attributes=stat.FILE_ATTRIBUTE_SYSTEM,
            )
        return info

    monkeypatch.setattr(scanner, "_read_stat", fake_read_stat)

    assert [item.name for item in scan_folder(tmp_path)] == ["visivel.txt"]


def test_campos_do_arquivo_listado(tmp_path: Path) -> None:
    _touch(tmp_path / "Foto.JPG", b"12345")

    (item,) = scan_folder(tmp_path)

    assert item.path == tmp_path / "Foto.JPG"
    assert item.name == "Foto.JPG"
    assert item.extension == "jpg"
    assert item.size_bytes == 5


@pytest.mark.parametrize(
    ("name", "expected"),
    [("a.tar.gz", "gz"), (".gitignore", ""), ("b.", ""), ("semextensao", "")],
)
def test_extensao_normalizada(tmp_path: Path, name: str, expected: str) -> None:
    _touch(tmp_path / name)

    (item,) = scan_folder(tmp_path)

    assert item.extension == expected


def test_pasta_inexistente_levanta_pasta_invalida(tmp_path: Path) -> None:
    with pytest.raises(FilePilotError) as info:
        scan_folder(tmp_path / "nao-existe")

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == "A pasta escolhida não existe ou não é uma pasta."


def test_caminho_de_arquivo_levanta_pasta_invalida(tmp_path: Path) -> None:
    arquivo = _touch(tmp_path / "a.txt")

    with pytest.raises(FilePilotError) as info:
        scan_folder(arquivo)

    assert info.value.code == "PASTA_INVALIDA"


def test_falha_de_listagem_levanta_pasta_ilegivel(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def raise_permission(self: Path) -> Any:
        raise PermissionError("negado")

    monkeypatch.setattr(Path, "iterdir", raise_permission)

    with pytest.raises(FilePilotError) as info:
        scan_folder(tmp_path)

    assert info.value.code == "PASTA_ILEGIVEL"
    assert info.value.message == "Não foi possível ler a pasta escolhida."


def test_pasta_sem_arquivos_elegiveis_levanta_pasta_vazia(tmp_path: Path) -> None:
    (tmp_path / "so-uma-pasta").mkdir()

    with pytest.raises(FilePilotError) as info:
        scan_folder(tmp_path)

    assert info.value.code == "PASTA_VAZIA"
    assert info.value.message == "A pasta escolhida não tem arquivos para organizar."


def test_link_simbolico_nao_aparece(tmp_path: Path) -> None:
    alvo = _touch(tmp_path / "alvo.txt")
    link = tmp_path / "link.txt"
    try:
        os.symlink(alvo, link)
    except (OSError, NotImplementedError):
        pytest.skip("sem permissao para criar link simbolico")

    assert [item.name for item in scan_folder(tmp_path)] == ["alvo.txt"]


def test_atalho_lnk_aparece_com_extensao_lnk(tmp_path: Path) -> None:
    _touch(tmp_path / "Atalho.lnk")

    (item,) = scan_folder(tmp_path)

    assert item.extension == "lnk"


def test_arquivo_cujo_stat_falha_e_omitido(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _touch(tmp_path / "bom.txt")
    _touch(tmp_path / "ruim.txt")
    real_read_stat = scanner._read_stat

    def fake_read_stat(path: Path) -> Any:
        if path.name == "ruim.txt":
            raise OSError("sumiu durante a listagem")
        return real_read_stat(path)

    monkeypatch.setattr(scanner, "_read_stat", fake_read_stat)

    assert [item.name for item in scan_folder(tmp_path)] == ["bom.txt"]
