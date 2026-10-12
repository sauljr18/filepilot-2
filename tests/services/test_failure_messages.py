from pathlib import Path

import pytest

from filepilot.db.connection import open_connection
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Plan, PlannedOperation
from filepilot.services import organizer
from filepilot.services.destination_checks import failure_text
from filepilot.services.organizer import internal_error, organize

RAW_TEXT = "texto bruto do sistema operacional"


def _single_plan(folder: Path) -> Plan:
    source = folder / "a.pdf"
    source.write_bytes(b"a")
    operation = PlannedOperation(
        seq=1,
        source_path=source,
        destination_path=folder / "Documentos" / "a.pdf",
        category="documentos",
        rule_name=None,
    )
    return Plan(folder=folder, operations=[operation])


def _winerror(exc: OSError, code: int) -> OSError:
    exc.winerror = code  # type: ignore[attr-defined]
    return exc


def _stored_message(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, exc: OSError, *, on: str
) -> str:
    folder = tmp_path / "escolhida"
    folder.mkdir()
    plan = _single_plan(folder)
    conn = open_connection(tmp_path / "historico.db")

    def raiser(*args: object, **kwargs: object) -> None:
        raise exc

    if on == "rename":
        monkeypatch.setattr(organizer.os, "rename", raiser)
    else:
        monkeypatch.setattr(Path, "mkdir", raiser)

    result = organize(plan, conn)

    assert (result.moved_count, result.failed_count) == (0, 1)
    row = conn.execute(
        "SELECT status, destination_path, error_message FROM operations"
    ).fetchone()
    assert row[0] == "falha"
    assert row[1] is None
    assert result.failures == [("a.pdf", row[2])]
    assert RAW_TEXT not in row[2]
    return str(row[2])


def test_permission_error_com_winerror_32_e_arquivo_em_uso(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exc = _winerror(PermissionError(RAW_TEXT), 32)

    message = _stored_message(tmp_path, monkeypatch, exc, on="rename")

    assert message == "arquivo em uso por outro programa"


def test_oserror_com_winerror_32_e_arquivo_em_uso(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exc = _winerror(OSError(RAW_TEXT), 32)

    message = _stored_message(tmp_path, monkeypatch, exc, on="rename")

    assert message == "arquivo em uso por outro programa"


def test_outro_permission_error_e_sem_permissao(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    exc = _winerror(PermissionError(RAW_TEXT), 5)

    message = _stored_message(tmp_path, monkeypatch, exc, on="rename")

    assert message == "sem permissão para mover o arquivo"


def test_file_not_found_e_arquivo_nao_encontrado(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    message = _stored_message(
        tmp_path, monkeypatch, FileNotFoundError(RAW_TEXT), on="rename"
    )

    assert message == "arquivo não encontrado"


def test_falha_de_mkdir_nao_consegue_criar_a_subpasta(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    message = _stored_message(tmp_path, monkeypatch, OSError(RAW_TEXT), on="mkdir")

    assert message == "não foi possível criar a subpasta de destino"


def test_permission_error_no_mkdir_continua_sem_permissao(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    message = _stored_message(
        tmp_path, monkeypatch, PermissionError(RAW_TEXT), on="mkdir"
    )

    assert message == "sem permissão para mover o arquivo"


def test_qualquer_outro_oserror_e_erro_ao_mover(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    message = _stored_message(tmp_path, monkeypatch, OSError(RAW_TEXT), on="rename")

    assert message == "erro ao mover o arquivo"


def test_failure_text_nao_exige_winerror_fora_do_windows() -> None:
    assert failure_text(OSError(RAW_TEXT), creating=False) == "erro ao mover o arquivo"
    assert (
        failure_text(FileNotFoundError(RAW_TEXT), creating=True)
        == "não foi possível criar a subpasta de destino"
    )


def test_excecao_inesperada_vira_erro_interno() -> None:
    error = internal_error(RuntimeError(RAW_TEXT))

    assert isinstance(error, FilePilotError)
    assert error.code == "ERRO_INTERNO"
    assert error.message == "Ocorreu um erro inesperado. Tente de novo."
    assert RAW_TEXT not in error.message


def test_erro_de_contrato_nao_e_reclassificado() -> None:
    original = FilePilotError("BANCO_INDISPONIVEL", "Não foi possível acessar.")

    assert internal_error(original) is original
