from pathlib import Path

from filepilot.db.connection import open_connection
from filepilot.domain.models import Plan, ScannedFile
from filepilot.services.organizer import organize
from filepilot.services.planner import build_plan


def _scanned(folder: Path, name: str) -> ScannedFile:
    path = folder / name
    path.write_bytes(b"novo")
    extension = name.rpartition(".")[2].lower()
    return ScannedFile(path=path, name=name, extension=extension, size_bytes=4)


def _plan(folder: Path, names: list[str]) -> Plan:
    return build_plan(folder, [_scanned(folder, name) for name in names], [])


def test_progresso_e_chamado_n_mais_um_vezes(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf", "c.png"])
    conn = open_connection(tmp_path / "historico.db")
    calls: list[tuple[int, int, str]] = []

    organize(plan, conn, lambda done, total, name: calls.append((done, total, name)))

    assert len(calls) == 4
    assert [call[0] for call in calls] == [0, 1, 2, 3]
    assert {call[1] for call in calls} == {3}
    assert [call[2] for call in calls[:3]] == ["a.pdf", "b.pdf", "c.png"]
    assert calls[-1][0] == calls[-1][1]


def test_arquivo_que_surge_no_destino_ganha_sufixo_e_o_existente_fica_intacto(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["fatura.pdf"])
    assert plan.operations[0].destination_path.name == "fatura.pdf"
    (folder / "Documentos").mkdir()
    (folder / "Documentos" / "fatura.pdf").write_bytes(b"antigo")
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count) == (1, 0)
    assert (folder / "Documentos" / "fatura.pdf").read_bytes() == b"antigo"
    assert (folder / "Documentos" / "fatura (1).pdf").read_bytes() == b"novo"
    assert not (folder / "fatura.pdf").exists()


def test_destination_path_gravado_e_o_nome_final_com_sufixo(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["fatura.pdf"])
    (folder / "Documentos").mkdir()
    (folder / "Documentos" / "fatura.pdf").write_bytes(b"antigo")
    conn = open_connection(tmp_path / "historico.db")

    organize(plan, conn)

    row = conn.execute(
        "SELECT destination_path, source_path, status FROM operations"
    ).fetchone()
    assert row[0] == str(folder / "Documentos" / "fatura (1).pdf")
    assert row[0] != row[1]
    assert row[2] == "movido"


def test_conflito_ocupa_o_proximo_sufixo_livre(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["fatura.pdf"])
    (folder / "Documentos").mkdir()
    (folder / "Documentos" / "fatura.pdf").write_bytes(b"antigo")
    (folder / "Documentos" / "fatura (1).pdf").write_bytes(b"antigo 1")
    conn = open_connection(tmp_path / "historico.db")

    organize(plan, conn)

    assert (folder / "Documentos" / "fatura (1).pdf").read_bytes() == b"antigo 1"
    assert (folder / "Documentos" / "fatura (2).pdf").read_bytes() == b"novo"
