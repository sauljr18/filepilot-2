from pathlib import Path

from filepilot.domain.models import Rule, ScannedFile
from filepilot.services.planner import build_plan


def _file(folder: Path, name: str) -> ScannedFile:
    extension = name.rpartition(".")[2].lower() if "." in name else ""
    return ScannedFile(
        path=folder / name, name=name, extension=extension, size_bytes=1
    )


def _rule(
    rule_id: int, name: str, destination: str, position: int, *extensions: str
) -> Rule:
    return Rule(
        id=rule_id,
        name=name,
        destination_folder=destination,
        position=position,
        extensions=frozenset(extensions),
    )


def test_categoria_padrao_e_arquivo_sem_categoria_em_skipped(tmp_path: Path) -> None:
    files = [
        _file(tmp_path, "fatura.pdf"),
        _file(tmp_path, "foto.JPG"),
        _file(tmp_path, "setup.exe"),
    ]

    plan = build_plan(tmp_path, files, [])

    assert [op.category for op in plan.operations] == ["documentos", "imagens"]
    assert [op.destination_path for op in plan.operations] == [
        tmp_path / "Documentos" / "fatura.pdf",
        tmp_path / "Imagens" / "foto.JPG",
    ]
    assert [item.name for item in plan.skipped] == ["setup.exe"]


def test_regra_vence_a_categoria_padrao(tmp_path: Path) -> None:
    rules = [_rule(1, "Contratos", "Contratos", 1, "pdf")]

    plan = build_plan(tmp_path, [_file(tmp_path, "fatura.pdf")], rules)

    operation = plan.operations[0]
    assert operation.rule_name == "Contratos"
    assert operation.category is None
    assert operation.destination_path == tmp_path / "Contratos" / "fatura.pdf"


def test_menor_position_vence_regra_posterior_mesmo_fora_de_ordem(
    tmp_path: Path,
) -> None:
    rules = [
        _rule(2, "Tardia", "Tardia", 5, "pdf"),
        _rule(1, "Cedo", "Cedo", 2, "pdf", "txt"),
    ]

    plan = build_plan(tmp_path, [_file(tmp_path, "a.pdf")], rules)

    assert plan.operations[0].rule_name == "Cedo"
    assert plan.operations[0].destination_path == tmp_path / "Cedo" / "a.pdf"


def test_regra_so_vale_para_suas_extensoes(tmp_path: Path) -> None:
    rules = [_rule(1, "Planilhas", "Planilhas", 1, "ods")]

    plan = build_plan(tmp_path, [_file(tmp_path, "a.pdf")], rules)

    assert plan.operations[0].rule_name is None
    assert plan.operations[0].category == "documentos"


def test_operacao_de_categoria_nao_tem_rule_name(tmp_path: Path) -> None:
    plan = build_plan(tmp_path, [_file(tmp_path, "clipe.mp4")], [])

    operation = plan.operations[0]
    assert operation.category == "videos"
    assert operation.rule_name is None
    assert operation.source_path == tmp_path / "clipe.mp4"


def test_seq_comeca_em_1_e_segue_a_ordem_dos_arquivos(tmp_path: Path) -> None:
    files = [
        _file(tmp_path, "b.pdf"),
        _file(tmp_path, "x.exe"),
        _file(tmp_path, "a.png"),
        _file(tmp_path, "c.zip"),
    ]

    plan = build_plan(tmp_path, files, [])

    assert [op.seq for op in plan.operations] == [1, 2, 3]
    assert [op.source_path.name for op in plan.operations] == ["b.pdf", "a.png", "c.zip"]


def test_sem_arquivos_e_sem_regras_o_plano_e_vazio(tmp_path: Path) -> None:
    plan = build_plan(tmp_path, [], [])

    assert plan.operations == []
    assert plan.skipped == []
    assert plan.folder == tmp_path
