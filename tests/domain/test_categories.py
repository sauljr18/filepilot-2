import dataclasses
from pathlib import Path

from filepilot.domain.categories import CATEGORIES
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import (
    OrganizationResult,
    Plan,
    PlannedOperation,
    Rule,
    ScannedFile,
)


def test_categories_tem_as_quatro_chaves_com_subpastas() -> None:
    assert {key: cat.folder for key, cat in CATEGORIES.items()} == {
        "documentos": "Documentos",
        "imagens": "Imagens",
        "videos": "Videos",
        "compactados": "Compactados",
    }


def test_categories_quantidade_de_extensoes() -> None:
    contagem = {key: len(cat.extensions) for key, cat in CATEGORIES.items()}
    assert contagem == {
        "documentos": 11,
        "imagens": 8,
        "videos": 6,
        "compactados": 5,
    }


def test_categories_extensoes_da_tabela() -> None:
    assert CATEGORIES["documentos"].extensions == {
        "pdf", "doc", "docx", "txt", "rtf", "odt",
        "xls", "xlsx", "ppt", "pptx", "csv",
    }
    assert CATEGORIES["imagens"].extensions == {
        "jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff",
    }
    assert CATEGORIES["videos"].extensions == {
        "mp4", "mkv", "avi", "mov", "wmv", "webm",
    }
    assert CATEGORIES["compactados"].extensions == {
        "zip", "rar", "7z", "tar", "gz",
    }


def test_categories_extensoes_em_minusculas_sem_ponto() -> None:
    for cat in CATEGORIES.values():
        for ext in cat.extensions:
            assert ext == ext.lower()
            assert not ext.startswith(".")


def test_categories_nenhuma_extensao_em_duas_categorias() -> None:
    todas = [ext for cat in CATEGORIES.values() for ext in cat.extensions]
    assert len(todas) == len(set(todas))


def test_filepilot_error_guarda_os_tres_valores() -> None:
    erro = FilePilotError("REGRA_INVALIDA", "Corrija os campos.", {"name": "x"})
    assert isinstance(erro, Exception)
    assert erro.code == "REGRA_INVALIDA"
    assert erro.message == "Corrija os campos."
    assert erro.fields == {"name": "x"}


def test_filepilot_error_fields_padrao_e_none() -> None:
    erro = FilePilotError("PASTA_VAZIA", "Sem arquivos.")
    assert erro.fields is None


def test_dataclasses_existem_com_os_campos_da_spec() -> None:
    def nomes(cls: type) -> list[str]:
        return [f.name for f in dataclasses.fields(cls)]

    assert nomes(ScannedFile) == ["path", "name", "extension", "size_bytes"]
    assert nomes(Rule) == [
        "id", "name", "destination_folder", "position", "extensions",
    ]
    assert nomes(PlannedOperation) == [
        "seq", "source_path", "destination_path", "category", "rule_name",
    ]
    assert nomes(Plan) == ["folder", "operations", "skipped"]
    assert nomes(OrganizationResult) == [
        "organization_id", "moved_count", "failed_count", "failures",
    ]


def test_plan_is_empty_sem_operacoes(tmp_path: Path) -> None:
    assert Plan(folder=tmp_path).is_empty is True


def test_plan_is_empty_falso_com_operacoes(tmp_path: Path) -> None:
    operacao = PlannedOperation(
        seq=1,
        source_path=tmp_path / "a.pdf",
        destination_path=tmp_path / "Documentos" / "a.pdf",
        category="documentos",
        rule_name=None,
    )
    assert Plan(folder=tmp_path, operations=[operacao]).is_empty is False
