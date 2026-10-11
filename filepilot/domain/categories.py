"""Categorias padrao de arquivos (SPEC 5.5): constantes, nao persistidas."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoryDef:
    """Categoria padrao: subpasta de destino e extensoes em minusculas, sem ponto."""

    folder: str
    extensions: frozenset[str]


CATEGORIES: dict[str, CategoryDef] = {
    "documentos": CategoryDef(
        folder="Documentos",
        extensions=frozenset(
            {
                "pdf",
                "doc",
                "docx",
                "txt",
                "rtf",
                "odt",
                "xls",
                "xlsx",
                "ppt",
                "pptx",
                "csv",
            }
        ),
    ),
    "imagens": CategoryDef(
        folder="Imagens",
        extensions=frozenset(
            {"jpg", "jpeg", "png", "gif", "bmp", "webp", "svg", "tiff"}
        ),
    ),
    "videos": CategoryDef(
        folder="Videos",
        extensions=frozenset({"mp4", "mkv", "avi", "mov", "wmv", "webm"}),
    ),
    "compactados": CategoryDef(
        folder="Compactados",
        extensions=frozenset({"zip", "rar", "7z", "tar", "gz"}),
    ),
}
