import sqlite3
from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Plan, ScannedFile
from filepilot.services import undo
from filepilot.services.history import last_undoable
from filepilot.services.organizer import OPERATION_LOCK, organize
from filepilot.services.planner import build_plan
from filepilot.services.undo import undo_last


def _scanned(folder: Path, name: str, content: bytes | None = None) -> ScannedFile:
    path = folder / name
    path.write_bytes(name.encode() if content is None else content)
    extension = name.rpartition(".")[2].lower()
    return ScannedFile(path=path, name=name, extension=extension, size_bytes=1)


def _plan(folder: Path, names: list[str]) -> Plan:
    return build_plan(folder, [_scanned(folder, name) for name in names], [])


def _tree(folder: Path) -> list[str]:
    return sorted(str(path.relative_to(folder)) for path in folder.rglob("*"))


def _statuses(conn: sqlite3.Connection, organization_id: int) -> dict[str, tuple[str, str | None]]:
    rows = conn.execute(
        "SELECT source_path, status, error_message FROM operations "
        "WHERE organization_id = ?",
        (organization_id,),
    ).fetchall()
    return {Path(row[0]).name: (row[1], row[2]) for row in rows}


@pytest.fixture
def conn(tmp_path: Path) -> sqlite3.Connection:
    return open_connection(tmp_path / "historico.db")


@pytest.fixture
def folder(tmp_path: Path) -> Path:
    chosen = tmp_path / "escolhida"
    chosen.mkdir()
    return chosen


def test_devolve_cada_arquivo_ao_caminho_e_nome_originais(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organized = organize(_plan(folder, ["fatura.pdf", "foto.png", "clipe.mp4"]), conn)
    assert (folder / "Documentos" / "fatura.pdf").is_file()

    result = undo_last(conn)

    assert result.organization_id == organized.organization_id
    assert (result.restored_count, result.not_restored) == (3, [])
    assert _tree(folder) == ["clipe.mp4", "fatura.pdf", "foto.png"]
    assert (folder / "fatura.pdf").read_bytes() == b"fatura.pdf"


def test_restaura_arquivos_que_receberam_sufixo(
    conn: sqlite3.Connection, folder: Path
) -> None:
    (folder / "Documentos").mkdir()
    (folder / "Documentos" / "a.pdf").write_bytes(b"ja existia")
    organize(_plan(folder, ["a.pdf"]), conn)
    assert (folder / "Documentos" / "a (1).pdf").is_file()

    result = undo_last(conn)

    assert result.restored_count == 1
    assert (folder / "a.pdf").read_bytes() == b"a.pdf"
    assert not (folder / "Documentos" / "a (1).pdf").exists()
    assert (folder / "Documentos" / "a.pdf").read_bytes() == b"ja existia"


def test_grava_restaurado_marca_desfeita_e_last_undoable_passa_a_none(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organized = organize(_plan(folder, ["a.pdf", "b.png"]), conn)

    undo_last(conn)

    assert _statuses(conn, organized.organization_id) == {
        "a.pdf": ("restaurado", None),
        "b.png": ("restaurado", None),
    }
    status, undone_at = conn.execute(
        "SELECT status, undone_at FROM organizations WHERE id = ?",
        (organized.organization_id,),
    ).fetchone()
    assert status == "desfeita"
    assert undone_at is not None
    assert last_undoable(conn) is None


def test_remove_subpastas_vazias_e_preserva_a_pasta_escolhida(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organize(_plan(folder, ["a.pdf", "b.png"]), conn)

    result = undo_last(conn)

    assert sorted(result.removed_folders) == sorted(
        [str(folder / "Documentos"), str(folder / "Imagens")]
    )
    assert folder.is_dir()
    assert _tree(folder) == ["a.pdf", "b.png"]


def test_pasta_com_arquivo_permanece(conn: sqlite3.Connection, folder: Path) -> None:
    organize(_plan(folder, ["a.pdf"]), conn)
    (folder / "Documentos" / "de_outra_origem.txt").write_bytes(b"x")

    result = undo_last(conn)

    assert result.removed_folders == []
    assert (folder / "Documentos" / "de_outra_origem.txt").is_file()
    assert (folder / "a.pdf").is_file()


def test_sobe_pelo_pai_ate_a_pasta_escolhida(
    conn: sqlite3.Connection, folder: Path
) -> None:
    aninhada = folder / "Docs" / "2026"
    aninhada.mkdir(parents=True)
    arquivo = folder / "a.pdf"
    arquivo.write_bytes(b"a")
    destino = aninhada / "a.pdf"
    arquivo.rename(destino)
    organization_id = _insert_organization(conn, folder)
    _insert_operation(conn, organization_id, 1, arquivo, destino)

    result = undo_last(conn)

    assert result.removed_folders == [str(aninhada), str(folder / "Docs")]
    assert folder.is_dir()
    assert _tree(folder) == ["a.pdf"]


def test_subida_para_na_pasta_do_pai_que_ainda_tem_arquivo(
    conn: sqlite3.Connection, folder: Path
) -> None:
    aninhada = folder / "Docs" / "2026"
    aninhada.mkdir(parents=True)
    (folder / "Docs" / "outro.txt").write_bytes(b"x")
    arquivo = folder / "a.pdf"
    destino = aninhada / "a.pdf"
    destino.write_bytes(b"a")
    organization_id = _insert_organization(conn, folder)
    _insert_operation(conn, organization_id, 1, arquivo, destino)

    result = undo_last(conn)

    assert result.removed_folders == [str(aninhada)]
    assert (folder / "Docs" / "outro.txt").is_file()


def test_arquivo_apagado_vira_nao_restaurado_e_os_demais_sao_restaurados(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organized = organize(_plan(folder, ["a.pdf", "b.pdf", "c.png"]), conn)
    (folder / "Documentos" / "a.pdf").unlink()

    result = undo_last(conn)

    assert result.restored_count == 2
    assert result.not_restored == [
        (str(folder / "a.pdf"), "arquivo não está mais no destino")
    ]
    assert _statuses(conn, organized.organization_id)["a.pdf"] == (
        "nao_restaurado",
        "arquivo não está mais no destino",
    )
    assert (folder / "b.pdf").is_file() and (folder / "c.png").is_file()


def test_caminho_original_ocupado_nao_sobrescreve(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organized = organize(_plan(folder, ["a.pdf", "b.png"]), conn)
    (folder / "a.pdf").write_bytes(b"novo arquivo do usuario")

    result = undo_last(conn)

    assert result.restored_count == 1
    assert result.not_restored == [(str(folder / "a.pdf"), "caminho original ocupado")]
    assert (folder / "a.pdf").read_bytes() == b"novo arquivo do usuario"
    assert (folder / "Documentos" / "a.pdf").read_bytes() == b"a.pdf"
    assert _statuses(conn, organized.organization_id)["a.pdf"] == (
        "nao_restaurado",
        "caminho original ocupado",
    )
    assert (folder / "b.png").is_file()


def test_organizacao_fica_desfeita_mesmo_com_nao_restaurados(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organized = organize(_plan(folder, ["a.pdf"]), conn)
    (folder / "Documentos" / "a.pdf").unlink()

    undo_last(conn)

    status = conn.execute(
        "SELECT status FROM organizations WHERE id = ?", (organized.organization_id,)
    ).fetchone()[0]
    assert status == "desfeita"
    assert last_undoable(conn) is None


def test_oserror_no_rename_vira_nao_restaurado_com_o_texto_do_erro(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["a.pdf"]), conn)

    def boom(src: object, dst: object) -> None:
        raise PermissionError("acesso negado")

    monkeypatch.setattr(undo.os, "rename", boom)

    result = undo_last(conn)

    assert result.restored_count == 0
    assert result.not_restored == [(str(folder / "a.pdf"), "acesso negado")]
    assert _statuses(conn, organized.organization_id)["a.pdf"] == (
        "nao_restaurado",
        "acesso negado",
    )
    assert (folder / "Documentos" / "a.pdf").is_file()


def test_guarda_recusa_caminho_original_fora_da_pasta_escolhida(
    conn: sqlite3.Connection, folder: Path, tmp_path: Path
) -> None:
    fora = tmp_path / "fora"
    fora.mkdir()
    destino = folder / "Documentos" / "a.pdf"
    destino.parent.mkdir()
    destino.write_bytes(b"a")
    organization_id = _insert_organization(conn, folder)
    _insert_operation(conn, organization_id, 1, fora / "a.pdf", destino)

    result = undo_last(conn)

    assert result.restored_count == 0
    assert [path for path, _ in result.not_restored] == [str(fora / "a.pdf")]
    assert not (fora / "a.pdf").exists()
    assert destino.is_file()


def test_operacoes_com_falha_ficam_como_estao(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organization_id = _insert_organization(conn, folder)
    destino = folder / "Documentos" / "a.pdf"
    destino.parent.mkdir()
    destino.write_bytes(b"a")
    _insert_operation(conn, organization_id, 1, folder / "a.pdf", destino)
    _insert_operation(
        conn, organization_id, 2, folder / "b.pdf", None, "falha", "sem permissão"
    )

    result = undo_last(conn)

    assert result.restored_count == 1
    assert _statuses(conn, organization_id)["b.pdf"] == ("falha", "sem permissão")


def test_desfaz_em_ordem_de_seq_decrescente(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organize(_plan(folder, ["a.pdf", "b.pdf", "c.pdf"]), conn)
    order: list[str] = []
    real_rename = undo.os.rename

    def spy(src: str | Path, dst: str | Path) -> None:
        order.append(Path(dst).name)
        real_rename(src, dst)

    monkeypatch.setattr(undo.os, "rename", spy)

    undo_last(conn)

    assert order == ["c.pdf", "b.pdf", "a.pdf"]


def test_sem_organizacao_desfazivel_levanta_nada_para_desfazer(
    conn: sqlite3.Connection,
) -> None:
    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)

    assert raised.value.code == "NADA_PARA_DESFAZER"
    assert raised.value.message == "Não há organização para desfazer."


def test_nao_desfaz_duas_vezes(conn: sqlite3.Connection, folder: Path) -> None:
    organize(_plan(folder, ["a.pdf"]), conn)
    undo_last(conn)

    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)

    assert raised.value.code == "NADA_PARA_DESFAZER"


def test_durante_organizacao_em_andamento_levanta_e_nao_altera_nada(
    conn: sqlite3.Connection, folder: Path
) -> None:
    organize(_plan(folder, ["a.pdf"]), conn)
    before = _tree(folder)
    assert OPERATION_LOCK.acquire(blocking=False)
    try:
        with pytest.raises(FilePilotError) as raised:
            undo_last(conn)
    finally:
        OPERATION_LOCK.release()

    assert raised.value.code == "ORGANIZACAO_EM_ANDAMENTO"
    assert raised.value.message == "Aguarde a organização terminar."
    assert _tree(folder) == before
    assert last_undoable(conn) is not None


def test_libera_o_lock_ao_terminar_e_ao_falhar(
    conn: sqlite3.Connection, folder: Path
) -> None:
    with pytest.raises(FilePilotError):
        undo_last(conn)
    assert OPERATION_LOCK.acquire(blocking=False)
    OPERATION_LOCK.release()
    organize(_plan(folder, ["a.pdf"]), conn)
    undo_last(conn)
    assert OPERATION_LOCK.acquire(blocking=False)
    OPERATION_LOCK.release()


def test_falha_do_banco_ao_gravar_devolve_o_arquivo_e_levanta_banco_indisponivel(
    conn: sqlite3.Connection, folder: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    organized = organize(_plan(folder, ["a.pdf"]), conn)

    def broken(*args: object, **kwargs: object) -> None:
        raise sqlite3.OperationalError("disco cheio")

    monkeypatch.setattr(undo, "_record_status", broken)

    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"
    assert (folder / "Documentos" / "a.pdf").is_file()
    assert not (folder / "a.pdf").exists()
    assert _statuses(conn, organized.organization_id)["a.pdf"][0] == "movido"
    assert OPERATION_LOCK.acquire(blocking=False)
    OPERATION_LOCK.release()


def test_banco_fechado_levanta_banco_indisponivel(tmp_path: Path) -> None:
    conn = open_connection(tmp_path / "historico.db")
    conn.close()

    with pytest.raises(FilePilotError) as raised:
        undo_last(conn)

    assert raised.value.code == "BANCO_INDISPONIVEL"


def _insert_organization(conn: sqlite3.Connection, folder: Path) -> int:
    now = "2026-10-11T12:00:00Z"
    cursor = conn.execute(
        "INSERT INTO organizations (folder_path, started_at, status, "
        "moved_count, failed_count, created_at, updated_at) "
        "VALUES (?, ?, 'concluida', 1, 0, ?, ?)",
        (str(folder), now, now, now),
    )
    conn.commit()
    assert cursor.lastrowid is not None
    return cursor.lastrowid


def _insert_operation(
    conn: sqlite3.Connection,
    organization_id: int,
    seq: int,
    source: Path,
    destination: Path | None,
    status: str = "movido",
    error_message: str | None = None,
) -> None:
    now = "2026-10-11T12:00:00Z"
    conn.execute(
        "INSERT INTO operations (organization_id, seq, source_path, "
        "destination_path, status, error_message, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            organization_id,
            seq,
            str(source),
            None if destination is None else str(destination),
            status,
            error_message,
            now,
            now,
        ),
    )
    conn.commit()
