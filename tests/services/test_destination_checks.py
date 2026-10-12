import os
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.models import Plan, PlannedOperation
from filepilot.services import organizer
from filepilot.services.destination_checks import (
    MAX_PATH,
    check_destination,
    has_shortcut,
)
from filepilot.services.organizer import organize


def _operations(
    folder: Path, destination_parent: Path, names: list[str]
) -> list[PlannedOperation]:
    operations = []
    for seq, name in enumerate(names, start=1):
        source = folder / name
        source.write_bytes(name.encode())
        operations.append(
            PlannedOperation(
                seq=seq,
                source_path=source,
                destination_path=destination_parent / name,
                category="documentos",
                rule_name=None,
            )
        )
    return operations


def _link(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError:
        pytest.skip("sem permissao para criar link simbolico")


def test_destino_com_exatamente_259_caracteres_passa(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    padding = MAX_PATH - len(str(folder / "x" / "a.pdf"))
    destination = folder / ("x" * (1 + padding)) / "a.pdf"
    assert len(str(destination)) == MAX_PATH

    assert check_destination(folder, destination) is None


def test_destino_com_260_caracteres_e_recusado(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    padding = MAX_PATH - len(str(folder / "x" / "a.pdf"))
    destination = folder / ("x" * (2 + padding)) / "a.pdf"
    assert len(str(destination)) == MAX_PATH + 1

    assert check_destination(folder, destination) == "caminho de destino muito longo"


def test_caminho_longo_nao_chama_rename_nem_cria_a_subpasta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    long_parent = folder / ("x" * 250)
    plan = Plan(folder=folder, operations=_operations(folder, long_parent, ["a.pdf"]))
    calls: list[object] = []

    def fake_rename(source: object, destination: object) -> None:
        calls.append((source, destination))

    monkeypatch.setattr(organizer.os, "rename", fake_rename)
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert calls == []
    assert result.failures == [("a.pdf", "caminho de destino muito longo")]
    assert not long_parent.exists()
    assert (folder / "a.pdf").is_file()


def test_subpasta_que_e_link_para_fora_recusa_todos_os_arquivos(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    outside = tmp_path / "fora"
    folder.mkdir()
    outside.mkdir()
    _link(folder / "Documentos", outside)
    plan = Plan(
        folder=folder,
        operations=_operations(folder, folder / "Documentos", ["a.pdf", "b.pdf"]),
    )
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count) == (0, 2)
    assert {message for _, message in result.failures} == {
        "a subpasta de destino é um atalho"
    }
    assert list(outside.iterdir()) == []
    assert (folder / "a.pdf").is_file()
    assert (folder / "b.pdf").is_file()


def test_verificacao_vale_para_cada_nivel_da_subpasta(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    outside = tmp_path / "fora"
    (folder / "Trabalho").mkdir(parents=True)
    outside.mkdir()
    _link(folder / "Trabalho" / "Contratos", outside)
    destination = folder / "Trabalho" / "Contratos" / "2026" / "a.pdf"

    assert has_shortcut(folder, destination.parent)
    assert check_destination(folder, destination) == "a subpasta de destino é um atalho"
    assert not has_shortcut(folder, folder / "Trabalho")


def test_link_no_primeiro_nivel_de_regra_com_varios_segmentos(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    outside = tmp_path / "fora"
    folder.mkdir()
    outside.mkdir()
    _link(folder / "Trabalho", outside)
    destination = folder / "Trabalho" / "Contratos" / "a.pdf"

    assert check_destination(folder, destination) == "a subpasta de destino é um atalho"


def test_subpasta_comum_inexistente_ou_existente_passa(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    (folder / "Documentos").mkdir(parents=True)

    assert check_destination(folder, folder / "Documentos" / "a.pdf") is None
    assert check_destination(folder, folder / "Novas" / "a.pdf") is None


def test_destino_fora_da_pasta_e_recusado_depois_das_verificacoes_1_e_2(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()

    assert (
        check_destination(folder, tmp_path / "fora" / "a.pdf")
        == "o destino fica fora da pasta escolhida"
    )


@pytest.mark.skipif(os.name != "nt", reason="junction so existe no Windows")
def test_junction_para_fora_da_pasta_e_atalho(tmp_path: Path) -> None:
    import subprocess

    folder = tmp_path / "escolhida"
    outside = tmp_path / "fora"
    folder.mkdir()
    outside.mkdir()
    subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(folder / "Documentos"), str(outside)],
        check=True,
        capture_output=True,
    )

    assert has_shortcut(folder, folder / "Documentos")
    assert (
        check_destination(folder, folder / "Documentos" / "a.pdf")
        == "a subpasta de destino é um atalho"
    )
