"""Regras de repositorio da SPEC 11: zero sobrescrita e zero rede (NFR-001).

O teste le os arquivos `.py` com `pathlib` e procura os nomes proibidos na
arvore sintatica, entao comentario e docstring que citam o nome nao contam.
"""

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PACKAGE = ROOT / "filepilot"
SERVICES = PACKAGE / "services"

FORBIDDEN_CALLS = {
    "os": {"replace", "remove"},
    "shutil": {"move", "rmtree"},
}
FORBIDDEN_METHODS = {"unlink"}
NETWORK_MODULES = {"socket", "http", "urllib", "requests"}


def forbidden_calls(source: str) -> list[str]:
    """Nomes de sobrescrita ou apagamento usados no codigo (SPEC 11, NFR-001)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Attribute):
            if node.attr in FORBIDDEN_METHODS:
                found.append(f"{node.attr} (linha {node.lineno})")
            elif (
                isinstance(node.value, ast.Name)
                and node.attr in FORBIDDEN_CALLS.get(node.value.id, set())
            ):
                found.append(f"{node.value.id}.{node.attr} (linha {node.lineno})")
        elif isinstance(node, ast.ImportFrom) and node.module in FORBIDDEN_CALLS:
            for alias in node.names:
                if alias.name in FORBIDDEN_CALLS[node.module] | {"*"}:
                    found.append(f"{node.module}.{alias.name} (linha {node.lineno})")
        elif isinstance(node, ast.Name) and node.id in FORBIDDEN_METHODS:
            found.append(f"{node.id} (linha {node.lineno})")
    return found


def network_imports(source: str) -> list[str]:
    """Modulos de rede importados, inclusive submodulos (SPEC 11, sem rede)."""
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names = [alias.name for alias in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names = [node.module]
        else:
            continue
        for name in names:
            if name.split(".")[0] in NETWORK_MODULES:
                found.append(f"{name} (linha {node.lineno})")
    return found


def _python_files(directory: Path) -> list[Path]:
    files = sorted(directory.rglob("*.py"))
    assert files, f"nenhum arquivo .py em {directory}"
    return files


def test_servicos_nao_sobrescrevem_nem_apagam_arquivos() -> None:
    offenders = {
        str(path.relative_to(ROOT)): forbidden_calls(path.read_text(encoding="utf-8"))
        for path in _python_files(SERVICES)
    }

    assert {name: found for name, found in offenders.items() if found} == {}


def test_pacote_nao_importa_modulos_de_rede() -> None:
    offenders = {
        str(path.relative_to(ROOT)): network_imports(path.read_text(encoding="utf-8"))
        for path in _python_files(PACKAGE)
    }

    assert {name: found for name, found in offenders.items() if found} == {}


@pytest.mark.parametrize(
    "source",
    [
        "import os\nos.replace('a', 'b')\n",
        "import os\nos.remove('a')\n",
        "import shutil\nshutil.move('a', 'b')\n",
        "import shutil\nshutil.rmtree('a')\n",
        "from pathlib import Path\nPath('a').unlink()\n",
        "from pathlib import Path\nPath('a').unlink(missing_ok=True)\n",
        "from shutil import move\nmove('a', 'b')\n",
        "from shutil import rmtree as apagar\napagar('a')\n",
        "from os import replace\nreplace('a', 'b')\n",
        "from os import *\n",
        "from shutil import *\n",
    ],
)
def test_detector_acusa_chamada_proibida(source: str) -> None:
    assert forbidden_calls(source) != []


@pytest.mark.parametrize(
    "source",
    [
        "import os\nos.rename('a', 'b')\n",
        "from pathlib import Path\nPath('a').rmdir()\n",
        "# os.replace e shutil.move so em comentario\n",
        '"""Nunca usa os.remove nem Path.unlink."""\n',
    ],
)
def test_detector_aceita_codigo_permitido(source: str) -> None:
    assert forbidden_calls(source) == []


@pytest.mark.parametrize(
    "source",
    [
        "import socket\n",
        "import http\n",
        "import http.client\n",
        "import urllib.request\n",
        "import requests\n",
        "from urllib import request\n",
        "from urllib.parse import quote\n",
        "from http.server import HTTPServer\n",
        "import os, socket\n",
    ],
)
def test_detector_acusa_importacao_de_rede(source: str) -> None:
    assert network_imports(source) != []


@pytest.mark.parametrize(
    "source",
    [
        "import sqlite3\n",
        "from filepilot.services import socketpool\n",
        "# import socket\n",
        "import httpx_like_name\n",
    ],
)
def test_detector_aceita_importacao_sem_rede(source: str) -> None:
    assert network_imports(source) == []
