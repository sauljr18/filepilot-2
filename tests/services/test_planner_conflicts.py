from pathlib import Path

from filepilot.domain.models import Rule, ScannedFile
from filepilot.services.planner import build_plan


def _file(folder: Path, name: str) -> ScannedFile:
    extension = name.rpartition(".")[2].lower() if "." in name else ""
    return ScannedFile(
        path=folder / name, name=name, extension=extension, size_bytes=1
    )


def _destinations(folder: Path, names: list[str], rules: list[Rule]) -> list[str]:
    plan = build_plan(folder, [_file(folder, name) for name in names], rules)
    return [op.destination_path.name for op in plan.operations]


def _existing(folder: Path, subfolder: str, *names: str) -> None:
    (folder / subfolder).mkdir(exist_ok=True)
    for name in names:
        (folder / subfolder / name).write_bytes(b"x")


def test_destino_ocupado_ganha_sufixo_1(tmp_path: Path) -> None:
    _existing(tmp_path, "Documentos", "fatura.pdf")

    assert _destinations(tmp_path, ["fatura.pdf"], []) == ["fatura (1).pdf"]


def test_destino_com_sufixo_1_tambem_ocupado_ganha_sufixo_2(tmp_path: Path) -> None:
    _existing(tmp_path, "Documentos", "fatura.pdf", "fatura (1).pdf")

    assert _destinations(tmp_path, ["fatura.pdf"], []) == ["fatura (2).pdf"]


def test_nome_livre_nao_muda(tmp_path: Path) -> None:
    _existing(tmp_path, "Documentos", "outro.pdf")

    assert _destinations(tmp_path, ["fatura.pdf"], []) == ["fatura.pdf"]


def test_extensao_dupla_so_o_ultimo_sufixo_fica_depois_do_numero(
    tmp_path: Path,
) -> None:
    _existing(tmp_path, "Compactados", "arquivo.tar.gz")

    assert _destinations(tmp_path, ["arquivo.tar.gz"], []) == ["arquivo.tar (1).gz"]


def test_arquivo_sem_extensao_ganha_sufixo_no_fim(tmp_path: Path) -> None:
    rule = Rule(
        id=1,
        name="Leia-me",
        destination_folder="Textos",
        position=1,
        extensions=frozenset({""}),
    )
    _existing(tmp_path, "Textos", "README")

    assert _destinations(tmp_path, ["README"], [rule]) == ["README (1)"]


def test_comparacao_ignora_maiusculas_e_minusculas(tmp_path: Path) -> None:
    _existing(tmp_path, "Documentos", "FATURA.PDF")

    assert _destinations(tmp_path, ["fatura.pdf"], []) == ["fatura (1).pdf"]


def test_sufixo_existente_em_outra_caixa_tambem_conta(tmp_path: Path) -> None:
    _existing(tmp_path, "Documentos", "Fatura.pdf", "FATURA (1).PDF")

    assert _destinations(tmp_path, ["fatura.pdf"], []) == ["fatura (2).pdf"]


def test_nomes_repetidos_no_mesmo_plano_recebem_sufixos_crescentes(
    tmp_path: Path,
) -> None:
    names = ["a.pdf", "A.PDF", "a.pdf"]

    assert _destinations(tmp_path, names, []) == ["a.pdf", "A (1).PDF", "a (2).pdf"]


def test_mesmo_nome_em_destinos_diferentes_nao_conflita(tmp_path: Path) -> None:
    assert _destinations(tmp_path, ["a.pdf", "a.png"], []) == ["a.pdf", "a.png"]


def test_conflito_com_destino_de_regra(tmp_path: Path) -> None:
    rule = Rule(
        id=1,
        name="Notas",
        destination_folder="Notas",
        position=1,
        extensions=frozenset({"txt"}),
    )
    _existing(tmp_path, "Notas", "nota.txt")

    assert _destinations(tmp_path, ["nota.txt"], [rule]) == ["nota (1).txt"]


def test_plano_nao_altera_arquivo_existente_nem_cria_pasta(tmp_path: Path) -> None:
    _existing(tmp_path, "Documentos", "fatura.pdf")
    (tmp_path / "Documentos" / "fatura.pdf").write_bytes(b"original")

    build_plan(tmp_path, [_file(tmp_path, "fatura.pdf"), _file(tmp_path, "a.png")], [])

    assert (tmp_path / "Documentos" / "fatura.pdf").read_bytes() == b"original"
    assert sorted(path.name for path in tmp_path.iterdir()) == ["Documentos"]
    assert [path.name for path in (tmp_path / "Documentos").iterdir()] == ["fatura.pdf"]
