from pathlib import Path

import pytest

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Rule, ScannedFile
from filepilot.services.planner import build_plan


def _file(folder: Path, name: str) -> ScannedFile:
    extension = name.rpartition(".")[2].lower() if "." in name else ""
    return ScannedFile(
        path=folder / name, name=name, extension=extension, size_bytes=1
    )


def _rule(destination: str) -> Rule:
    return Rule(
        id=1,
        name="Fuga",
        destination_folder=destination,
        position=1,
        extensions=frozenset({"txt"}),
    )


def _tree(folder: Path) -> list[tuple[str, bytes | None]]:
    return sorted(
        (str(path.relative_to(folder)), path.read_bytes() if path.is_file() else None)
        for path in folder.rglob("*")
    )


def test_destino_fora_da_pasta_levanta_erro_e_nao_devolve_plano(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    files = [_file(folder, "a.pdf"), _file(folder, "nota.txt")]

    with pytest.raises(FilePilotError) as raised:
        build_plan(folder, files, [_rule("../fora")])

    assert raised.value.code == "DESTINO_FORA_DA_PASTA"
    assert raised.value.message == "O destino fica fora da pasta escolhida."
    assert not (tmp_path / "fora").exists()


def test_subpasta_que_sobe_e_volta_para_dentro_e_aceita(tmp_path: Path) -> None:
    plan = build_plan(tmp_path, [_file(tmp_path, "nota.txt")], [_rule("a/../b")])

    assert plan.operations[0].destination_path.resolve() == (
        tmp_path.resolve() / "b" / "nota.txt"
    )


def test_link_simbolico_que_leva_para_fora_e_recusado(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    outside = tmp_path / "fora"
    folder.mkdir()
    outside.mkdir()
    try:
        (folder / "atalho").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("sem permissao para criar link simbolico")

    with pytest.raises(FilePilotError) as raised:
        build_plan(folder, [_file(folder, "nota.txt")], [_rule("atalho")])

    assert raised.value.code == "DESTINO_FORA_DA_PASTA"


def test_arvore_da_pasta_fica_identica_depois_do_plano(tmp_path: Path) -> None:
    (tmp_path / "fatura.pdf").write_bytes(b"pdf")
    (tmp_path / "foto.png").write_bytes(b"png")
    (tmp_path / "Documentos").mkdir()
    (tmp_path / "Documentos" / "fatura.pdf").write_bytes(b"antigo")
    before = _tree(tmp_path)

    plan = build_plan(
        tmp_path, [_file(tmp_path, "fatura.pdf"), _file(tmp_path, "foto.png")], []
    )

    assert len(plan.operations) == 2
    assert _tree(tmp_path) == before


def test_plano_e_vazio_quando_nenhum_arquivo_tem_categoria_ou_regra(
    tmp_path: Path,
) -> None:
    plan = build_plan(tmp_path, [_file(tmp_path, "setup.exe")], [])

    assert plan.is_empty
    assert [item.name for item in plan.skipped] == ["setup.exe"]


def test_plano_nao_e_vazio_com_uma_operacao(tmp_path: Path) -> None:
    plan = build_plan(tmp_path, [_file(tmp_path, "a.pdf")], [])

    assert not plan.is_empty
