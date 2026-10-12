from collections.abc import Iterator
from itertools import permutations
from pathlib import Path

import pytest

from filepilot.domain.models import ScannedFile
from filepilot.services import scanner
from filepilot.services.scanner import scan_folder


def _fake_entry(path: Path) -> ScannedFile:
    return ScannedFile(path=path, name=path.name, extension="", size_bytes=1)


def _scan_with_order(
    monkeypatch: pytest.MonkeyPatch, folder: Path, names: tuple[str, ...]
) -> list[str]:
    def fake_iterdir(self: Path) -> Iterator[Path]:
        return iter([folder / name for name in names])

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)
    monkeypatch.setattr(scanner, "_scan_entry", _fake_entry)

    return [item.name for item in scan_folder(folder)]


def test_empate_de_casefold_desempata_pelo_nome_exato(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    result = _scan_with_order(monkeypatch, tmp_path, ("b.txt", "a.txt", "A.txt"))

    assert result == ["A.txt", "a.txt", "b.txt"]


def test_ordem_nao_depende_da_ordem_de_entrada(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entradas = [
        ("b.txt", "a.txt", "A.txt"),
        ("A.txt", "a.txt", "b.txt"),
        ("a.txt", "A.txt", "b.txt"),
    ]

    results = [_scan_with_order(monkeypatch, tmp_path, entrada) for entrada in entradas]

    assert results[0] == results[1] == results[2]


def test_tres_variantes_do_mesmo_nome_em_todas_as_permutacoes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    nomes = ("Foto.JPG", "foto.jpg", "FOTO.jpg")

    results = [_scan_with_order(monkeypatch, tmp_path, entrada) for entrada in permutations(nomes)]

    assert len(results) == 6
    assert all(result == results[0] for result in results)
    assert results[0] == ["FOTO.jpg", "Foto.JPG", "foto.jpg"]


def test_nomes_que_ja_diferiam_em_casefold_seguem_alfabeticos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for entrada in permutations(("beta.txt", "Alfa.txt")):
        assert _scan_with_order(monkeypatch, tmp_path, entrada) == ["Alfa.txt", "beta.txt"]
