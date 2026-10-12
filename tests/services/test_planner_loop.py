import errno
from collections.abc import Callable
from pathlib import Path

import pytest

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Rule, ScannedFile
from filepilot.services.planner import build_plan

INVALID_MESSAGE = "A pasta escolhida não existe ou não é uma pasta."

_original_resolve = Path.resolve


def _fail_resolve_for(target: Path, error: Exception) -> Callable[..., Path]:
    def fake_resolve(self: Path, strict: bool = False) -> Path:
        if self == target:
            raise error
        return _original_resolve(self, strict=strict)

    return fake_resolve


def _symlink(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("o sistema recusou criar o link simbolico")


def _file(folder: Path, name: str) -> ScannedFile:
    extension = name.rpartition(".")[2].lower() if "." in name else ""
    return ScannedFile(path=folder / name, name=name, extension=extension, size_bytes=1)


def _tree(folder: Path) -> list[tuple[str, bool]]:
    return sorted(
        (str(path.relative_to(folder)), path.is_symlink()) for path in folder.rglob("*")
    )


def _folder_with_pdf(tmp_path: Path) -> Path:
    folder = tmp_path / "entrada"
    folder.mkdir()
    (folder / "a.pdf").write_bytes(b"x")
    return folder


def test_laco_no_destino_levantado_como_runtime_error_vira_pasta_invalida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = _folder_with_pdf(tmp_path)
    target = folder / "Documentos" / "a.pdf"
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(target, RuntimeError("Symlink loop")))

    with pytest.raises(FilePilotError) as info:
        build_plan(folder, [_file(folder, "a.pdf")], [])

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE
    assert "Symlink loop" not in info.value.message
    assert isinstance(info.value.__cause__, RuntimeError)


def test_oserror_eloop_na_resolucao_do_destino_vira_pasta_invalida(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = _folder_with_pdf(tmp_path)
    error = OSError(errno.ELOOP, "Too many levels of symbolic links")
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(folder / "Documentos" / "a.pdf", error))

    with pytest.raises(FilePilotError) as info:
        build_plan(folder, [_file(folder, "a.pdf")], [])

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE
    assert info.value.__cause__ is error


def test_oserror_eacces_na_resolucao_do_destino_continua_sendo_oserror(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = _folder_with_pdf(tmp_path)
    error = OSError(errno.EACCES, "Permission denied")
    monkeypatch.setattr(Path, "resolve", _fail_resolve_for(folder / "Documentos" / "a.pdf", error))

    with pytest.raises(OSError) as info:
        build_plan(folder, [_file(folder, "a.pdf")], [])

    assert not isinstance(info.value, FilePilotError)
    assert info.value is error


def test_laco_real_no_destino_vira_pasta_invalida_e_a_arvore_fica_identica(
    tmp_path: Path,
) -> None:
    folder = _folder_with_pdf(tmp_path)
    _symlink(folder / "Documentos", folder / "Documentos")
    before = _tree(folder)

    with pytest.raises(FilePilotError) as info:
        build_plan(folder, [_file(folder, "a.pdf")], [])

    assert info.value.code == "PASTA_INVALIDA"
    assert info.value.message == INVALID_MESSAGE
    assert _tree(folder) == before


def test_laco_real_em_subpasta_que_nenhum_arquivo_usa_nao_impede_o_plano(
    tmp_path: Path,
) -> None:
    folder = _folder_with_pdf(tmp_path)
    _symlink(folder / "Imagens", folder / "Imagens")

    plan = build_plan(folder, [_file(folder, "a.pdf")], [])

    assert [item.destination_path for item in plan.operations] == [
        folder / "Documentos" / "a.pdf"
    ]


def test_destino_fora_da_pasta_continua_sendo_destino_fora_da_pasta(
    tmp_path: Path,
) -> None:
    folder = _folder_with_pdf(tmp_path)
    rule = Rule(
        id=1,
        name="Fuga",
        destination_folder="../fora",
        position=1,
        extensions=frozenset({"pdf"}),
    )

    with pytest.raises(FilePilotError) as info:
        build_plan(folder, [_file(folder, "a.pdf")], [rule])

    assert info.value.code == "DESTINO_FORA_DA_PASTA"
