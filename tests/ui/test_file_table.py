from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication, QPalette
from pytestqt.qtbot import QtBot

from filepilot.domain.models import Rule, ScannedFile
from filepilot.services.planner import build_plan
from filepilot.ui.file_table import FileTableView


def _file(folder: Path, name: str) -> ScannedFile:
    extension = name.rpartition(".")[2].lower() if "." in name else ""
    return ScannedFile(path=folder / name, name=name, extension=extension, size_bytes=1)


def _rule(name: str, destination: str, *extensions: str) -> Rule:
    return Rule(
        id=1,
        name=name,
        destination_folder=destination,
        position=1,
        extensions=frozenset(extensions),
    )


def _view(qtbot: QtBot) -> FileTableView:
    view = FileTableView()
    qtbot.addWidget(view)
    return view


def _cells(view: FileTableView, row: int) -> list[str]:
    model = view.model
    return [
        model.data(model.index(row, column), Qt.ItemDataRole.DisplayRole)
        for column in range(model.columnCount())
    ]


def test_colunas_na_ordem_do_contrato(qtbot: QtBot) -> None:
    view = _view(qtbot)

    model = view.model
    headers = [
        model.headerData(column, Qt.Orientation.Horizontal)
        for column in range(model.columnCount())
    ]
    assert headers == ["Arquivo", "Extensão", "Categoria", "Destino", "Regra"]


def test_categoria_mostra_a_subpasta_padrao_e_destino_relativo(
    qtbot: QtBot, tmp_path: Path
) -> None:
    files = [
        _file(tmp_path, "fatura.pdf"),
        _file(tmp_path, "foto.png"),
        _file(tmp_path, "filme.mp4"),
        _file(tmp_path, "backup.zip"),
    ]
    view = _view(qtbot)

    view.set_rows(files, build_plan(tmp_path, files, []))

    assert [_cells(view, row) for row in range(4)] == [
        ["fatura.pdf", "pdf", "Documentos", str(Path("Documentos") / "fatura.pdf"), ""],
        ["foto.png", "png", "Imagens", str(Path("Imagens") / "foto.png"), ""],
        ["filme.mp4", "mp4", "Videos", str(Path("Videos") / "filme.mp4"), ""],
        ["backup.zip", "zip", "Compactados", str(Path("Compactados") / "backup.zip"), ""],
    ]


def test_regra_aparece_so_na_coluna_regra(qtbot: QtBot, tmp_path: Path) -> None:
    files = [_file(tmp_path, "contrato.pdf")]
    plan = build_plan(tmp_path, files, [_rule("Contratos", "Juridico", "pdf")])
    view = _view(qtbot)

    view.set_rows(files, plan)

    assert _cells(view, 0) == [
        "contrato.pdf",
        "pdf",
        "Regra personalizada",
        str(Path("Juridico") / "contrato.pdf"),
        "Contratos",
    ]


def test_arquivo_sem_categoria_tem_destino_vazio_e_aparece_em_cinza(
    qtbot: QtBot, tmp_path: Path
) -> None:
    files = [_file(tmp_path, "setup.exe"), _file(tmp_path, "nota.txt")]
    view = _view(qtbot)

    view.set_rows(files, build_plan(tmp_path, files, []))

    assert _cells(view, 0) == ["setup.exe", "exe", "sem categoria", "", ""]
    model = view.model
    disabled = QGuiApplication.palette().color(
        QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text
    )
    assert model.data(model.index(0, 0), Qt.ItemDataRole.ForegroundRole) == disabled
    assert model.data(model.index(1, 0), Qt.ItemDataRole.ForegroundRole) is None


def test_listado_mostra_a_categoria_prevista_com_destino_vazio(
    qtbot: QtBot, tmp_path: Path
) -> None:
    files = [_file(tmp_path, "fatura.pdf")]
    view = _view(qtbot)

    view.set_rows(files, build_plan(tmp_path, files, []), show_destination=False)

    assert _cells(view, 0) == ["fatura.pdf", "pdf", "Documentos", "", ""]


def test_linha_com_regra_fica_em_negrito_so_na_coluna_regra(
    qtbot: QtBot, tmp_path: Path
) -> None:
    files = [_file(tmp_path, "contrato.pdf")]
    plan = build_plan(tmp_path, files, [_rule("Contratos", "Juridico", "pdf")])
    view = _view(qtbot)

    view.set_rows(files, plan)

    model = view.model
    bold_rule = model.data(model.index(0, 4), Qt.ItemDataRole.FontRole)
    assert bold_rule is not None and bold_rule.bold()
    assert model.data(model.index(0, 0), Qt.ItemDataRole.FontRole) is None


def test_sem_linhas_mostra_a_mensagem_de_tabela_vazia(
    qtbot: QtBot, tmp_path: Path
) -> None:
    view = _view(qtbot)
    assert view.empty_label.text() == "Nenhum arquivo para mostrar."
    assert view._stack.currentWidget() is view.empty_label

    files = [_file(tmp_path, "fatura.pdf")]
    view.set_rows(files, build_plan(tmp_path, files, []))
    assert view._stack.currentWidget() is view.view

    view.set_rows([], None)
    assert view._stack.currentWidget() is view.empty_label


def test_nao_ha_ordenacao_por_clique_no_cabecalho(qtbot: QtBot) -> None:
    view = _view(qtbot)

    assert view.view.isSortingEnabled() is False
    assert view.view.horizontalHeader().sectionsClickable() is False


def test_somente_leitura(qtbot: QtBot, tmp_path: Path) -> None:
    files = [_file(tmp_path, "fatura.pdf")]
    view = _view(qtbot)
    view.set_rows(files, None)

    model = view.model
    assert not model.flags(model.index(0, 0)) & Qt.ItemFlag.ItemIsEditable
    assert view.view.horizontalHeader().stretchLastSection() is False


def test_sem_plano_a_categoria_fica_vazia(qtbot: QtBot, tmp_path: Path) -> None:
    view = _view(qtbot)

    view.set_rows([_file(tmp_path, "fatura.pdf")], None)

    assert _cells(view, 0) == ["fatura.pdf", "pdf", "", "", ""]
