import sqlite3
from pathlib import Path

from filepilot.db.connection import open_connection
from filepilot.domain.models import Plan, ScannedFile
from filepilot.services.organizer import organize, simulate
from filepilot.services.planner import build_plan


def _scanned(folder: Path, name: str) -> ScannedFile:
    path = folder / name
    path.write_bytes(name.encode())
    extension = name.rpartition(".")[2].lower()
    return ScannedFile(path=path, name=name, extension=extension, size_bytes=1)


def _plan(folder: Path, names: list[str]) -> Plan:
    files = [_scanned(folder, name) for name in names]
    return build_plan(folder, files, [])


def _tree(folder: Path) -> list[tuple[str, bytes | None]]:
    return sorted(
        (str(path.relative_to(folder)), path.read_bytes() if path.is_file() else None)
        for path in folder.rglob("*")
    )


def test_organize_move_os_arquivos_e_grava_a_organizacao(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["fatura.pdf", "foto.png", "clipe.mp4"])
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count, result.failures) == (3, 0, [])
    assert (folder / "Documentos" / "fatura.pdf").read_bytes() == b"fatura.pdf"
    assert (folder / "Imagens" / "foto.png").is_file()
    assert (folder / "Videos" / "clipe.mp4").is_file()
    assert not (folder / "fatura.pdf").exists()
    organization = conn.execute(
        "SELECT id, folder_path, status, moved_count, failed_count, finished_at "
        "FROM organizations"
    ).fetchall()
    assert len(organization) == 1
    org_id, folder_path, status, moved, failed, finished_at = organization[0]
    assert (org_id, folder_path) == (result.organization_id, str(folder))
    assert (status, moved, failed) == ("concluida", 3, 0)
    assert finished_at is not None
    operations = conn.execute(
        "SELECT seq, status, source_path, destination_path, created_at, updated_at "
        "FROM operations WHERE organization_id = ? ORDER BY seq",
        (org_id,),
    ).fetchall()
    assert [row[0] for row in operations] == [1, 2, 3]
    assert {row[1] for row in operations} == {"movido"}
    for row, planned in zip(operations, plan.operations, strict=True):
        assert row[2] == str(planned.source_path)
        assert row[3] == str(planned.destination_path)
        assert row[4] and row[5]


def test_cada_operacao_e_gravada_com_commit_imediato(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf", "c.pdf"])
    db_path = tmp_path / "historico.db"
    conn = open_connection(db_path)
    seen: list[tuple[int, int]] = []

    def callback(done: int, total: int, filename: str) -> None:
        other = sqlite3.connect(db_path)
        try:
            row = other.execute("SELECT COUNT(*) FROM operations").fetchone()
        finally:
            other.close()
        seen.append((done, row[0]))

    organize(plan, conn, callback)

    assert seen == [(0, 0), (1, 1), (2, 2), (3, 3)]


def test_a_organizacao_abre_em_andamento_antes_do_primeiro_arquivo(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf"])
    db_path = tmp_path / "historico.db"
    conn = open_connection(db_path)
    statuses: list[str] = []

    def callback(done: int, total: int, filename: str) -> None:
        other = sqlite3.connect(db_path)
        try:
            statuses.append(other.execute("SELECT status FROM organizations").fetchone()[0])
        finally:
            other.close()

    organize(plan, conn, callback)

    assert statuses == ["em_andamento", "concluida"]


def test_plano_vazio_devolve_zeros_e_nao_grava_organizacao(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["setup.exe"])
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert plan.is_empty
    assert (result.organization_id, result.moved_count, result.failed_count) == (0, 0, 0)
    assert result.failures == []
    assert conn.execute("SELECT COUNT(*) FROM organizations").fetchone()[0] == 0
    assert (folder / "setup.exe").is_file()


def test_simulate_devolve_o_mesmo_plano_e_a_arvore_fica_identica(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "foto.png"])
    before = _tree(folder)

    assert simulate(plan) is plan
    assert _tree(folder) == before
