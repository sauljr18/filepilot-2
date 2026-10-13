"""Regras do .gitignore da raiz (SPEC 45.8).

O teste confere as nove linhas do arquivo e o efeito delas com
`git check-ignore`, sem criar nenhum arquivo no repositorio.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_LINES = [
    "__pycache__/",
    "*.py[cod]",
    "*.egg-info/",
    ".pytest_cache/",
    ".mypy_cache/",
    ".venv/",
    "venv/",
    "build/",
    "dist/",
]
IGNORED_PATHS = [
    "filepilot/__pycache__/x.cpython-312.pyc",
    "filepilot.egg-info/PKG-INFO",
    ".mypy_cache/x",
    ".pytest_cache/x",
    ".venv/x",
    "venv/x",
    "build/x",
    "dist/x",
]
TRACKED_PATHS = [
    "packaging/filepilot.spec",
    ".abt/SPEC.md",
    ".github/workflows/tests.yml",
    "pyproject.toml",
]


def run_git(*args: str) -> subprocess.CompletedProcess[str]:
    """Roda o git na raiz do repositorio e devolve o resultado completo."""
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )


@pytest.fixture(autouse=True)
def require_git_repository() -> None:
    """Pula o teste sem git no PATH ou fora de um repositorio."""
    if shutil.which("git") is None:
        pytest.skip("git nao esta no PATH")
    if run_git("rev-parse", "--is-inside-work-tree").returncode != 0:
        pytest.skip("a raiz do projeto nao e um repositorio git")


def test_gitignore_has_the_nine_lines() -> None:
    text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert text.splitlines() == EXPECTED_LINES


@pytest.mark.parametrize("path", IGNORED_PATHS)
def test_check_ignore_matches_generated_paths(path: str) -> None:
    assert run_git("check-ignore", "-q", path).returncode == 0


@pytest.mark.parametrize("path", TRACKED_PATHS)
def test_check_ignore_skips_tracked_paths(path: str) -> None:
    assert run_git("check-ignore", "-q", path).returncode == 1


def test_no_tracked_file_matches_gitignore() -> None:
    result = run_git("ls-files", "-ci", "--exclude-standard")
    assert result.returncode == 0
    assert result.stdout == ""
