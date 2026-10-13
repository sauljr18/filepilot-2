"""Comando de mypy do fluxo do GitHub Actions (SPEC 45.7).

O teste le `.github/workflows/tests.yml` com `pathlib` e compara linhas
inteiras sem os espacos das pontas: a forma antiga, sem `tests`, e prefixo da
nova e por isso nao pode ser comparada por trecho.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = ROOT / ".github" / "workflows" / "tests.yml"

NEW_COMMAND = "run: python -m mypy --platform win32 filepilot tests"
OLD_COMMANDS = {
    "run: mypy . --no-error-summary",
    "run: python -m mypy --platform win32 filepilot",
}


def workflow_lines() -> list[str]:
    """Linhas do workflow sem os espacos das pontas."""
    return [line.strip() for line in WORKFLOW.read_text(encoding="utf-8").splitlines()]


def test_workflow_runs_mypy_with_tests_folder() -> None:
    assert workflow_lines().count(NEW_COMMAND) == 1


def test_workflow_has_no_old_mypy_command() -> None:
    assert OLD_COMMANDS.isdisjoint(workflow_lines())
