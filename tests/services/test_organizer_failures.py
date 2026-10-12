import os
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Plan, PlannedOperation, ScannedFile
from filepilot.services import organizer
from filepilot.services.organizer import OPERATION_LOCK, organize
from filepilot.services.planner import build_plan


def _scanned(folder: Path, name: str) -> ScannedFile:
    path = folder / name
    path.write_bytes(name.encode())
    extension = name.rpartition(".")[2].lower()
    return ScannedFile(path=path, name=name, extension=extension, size_bytes=1)


def _plan(folder: Path, names: list[str]) -> Plan:
    return build_plan(folder, [_scanned(folder, name) for name in names], [])


def _manual_plan(folder: Path, source: Path, destination: Path) -> Plan:
    operation = PlannedOperation(
        seq=1,
        source_path=source,
        destination_path=destination,
        category="documentos",
        rule_name=None,
    )
    return Plan(folder=folder, operations=[operation])


def test_permission_error_vira_falha_e_os_demais_sao_movidos(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf", "c.pdf"])
    real_rename = os.rename

    def fake_rename(source: str | Path, destination: str | Path) -> None:
        if Path(source).name == "b.pdf":
            raise PermissionError("acesso negado")
        real_rename(source, destination)

    monkeypatch.setattr(organizer.os, "rename", fake_rename)
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count) == (2, 1)
    assert result.failures == [("b.pdf", "sem permissão para mover o arquivo")]
    assert (folder / "b.pdf").is_file()
    assert (folder / "Documentos" / "a.pdf").is_file()
    assert (folder / "Documentos" / "c.pdf").is_file()
    failed = conn.execute(
        "SELECT destination_path, error_message FROM operations WHERE status = 'falha'"
    ).fetchall()
    assert failed == [(None, "sem permissão para mover o arquivo")]
    counts = conn.execute(
        "SELECT status, moved_count, failed_count FROM organizations"
    ).fetchone()
    assert counts == ("concluida", 2, 1)


def test_arquivo_apagado_entre_o_plano_e_a_execucao_vira_falha(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf"])
    (folder / "a.pdf").unlink()
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count) == (1, 1)
    assert result.failures == [("a.pdf", "arquivo não encontrado")]


def test_segunda_organizacao_com_a_trava_tomada_levanta_erro(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf"])
    conn = open_connection(tmp_path / "historico.db")

    assert OPERATION_LOCK.acquire(blocking=False)
    try:
        with pytest.raises(FilePilotError) as raised:
            organize(plan, conn)
    finally:
        OPERATION_LOCK.release()

    assert raised.value.code == "ORGANIZACAO_EM_ANDAMENTO"
    assert raised.value.message == "Aguarde a organização terminar."
    assert (folder / "a.pdf").is_file()
    assert conn.execute("SELECT COUNT(*) FROM organizations").fetchone()[0] == 0


def test_a_trava_e_liberada_depois_de_uma_excecao(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf"])
    conn = open_connection(tmp_path / "historico.db")

    def explode(done: int, total: int, name: str) -> None:
        raise RuntimeError("falha na interface")

    with pytest.raises(RuntimeError):
        organize(plan, conn, explode)

    assert OPERATION_LOCK.acquire(blocking=False)
    OPERATION_LOCK.release()


def test_sqlite_error_ao_gravar_devolve_o_arquivo_e_levanta_erro(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _plan(folder, ["a.pdf", "b.pdf"])
    conn = open_connection(tmp_path / "historico.db")
    conn.execute(
        "CREATE TRIGGER falha_gravacao BEFORE INSERT ON operations "
        "BEGIN SELECT RAISE(ABORT, 'disco cheio'); END"
    )
    conn.commit()

    with pytest.raises(FilePilotError) as raised:
        organize(plan, conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert (folder / "a.pdf").read_bytes() == b"a.pdf"
    assert (folder / "b.pdf").is_file()
    assert not (folder / "Documentos" / "a.pdf").exists()
    assert conn.execute("SELECT COUNT(*) FROM operations").fetchone()[0] == 0
    assert OPERATION_LOCK.acquire(blocking=False)
    OPERATION_LOCK.release()


def test_destino_fora_da_pasta_vira_falha_sem_mover(tmp_path: Path) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    source = folder / "a.pdf"
    source.write_bytes(b"a")
    plan = _manual_plan(folder, source, tmp_path / "fora" / "a.pdf")
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count) == (0, 1)
    assert source.is_file()
    assert not (tmp_path / "fora").exists()
    row = conn.execute(
        "SELECT status, destination_path, error_message FROM operations"
    ).fetchone()
    assert row[0] == "falha"
    assert row[1] is None
    assert row[2]


def test_subpasta_que_e_link_para_fora_recusa_todos_os_arquivos(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    outside = tmp_path / "fora"
    folder.mkdir()
    outside.mkdir()
    try:
        (folder / "Documentos").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("sem permissao para criar link simbolico")
    operations = []
    for seq, name in enumerate(["a.pdf", "b.pdf"], start=1):
        source = folder / name
        source.write_bytes(name.encode())
        operations.append(
            PlannedOperation(
                seq=seq,
                source_path=source,
                destination_path=folder / "Documentos" / name,
                category="documentos",
                rule_name=None,
            )
        )
    plan = Plan(folder=folder, operations=operations)
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count) == (0, 2)
    assert {message for _, message in result.failures} == {
        "a subpasta de destino é um atalho"
    }
    assert list(outside.iterdir()) == []
    assert (folder / "a.pdf").is_file()
    assert (folder / "b.pdf").is_file()


def test_caminho_de_destino_acima_de_259_caracteres_vira_falha(
    tmp_path: Path,
) -> None:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    source = folder / "a.pdf"
    source.write_bytes(b"a")
    long_destination = folder / ("x" * 250) / "a.pdf"
    plan = _manual_plan(folder, source, long_destination)
    conn = open_connection(tmp_path / "historico.db")

    result = organize(plan, conn)

    assert result.failures == [("a.pdf", "caminho de destino muito longo")]
    assert source.is_file()
    assert not (folder / ("x" * 250)).exists()
