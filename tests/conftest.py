from collections.abc import Callable

import pytest
from PySide6.QtWidgets import QMessageBox

_DIALOGS = ("information", "warning", "critical", "question")


def _forbidden(name: str) -> Callable[..., object]:
    def fail(parent: object, title: str, text: str, *args: object) -> object:
        raise AssertionError(f"caixa de dialogo inesperada ({name}): {title}: {text}")

    return fail


@pytest.fixture(autouse=True)
def _no_modal_dialogs(monkeypatch: pytest.MonkeyPatch) -> None:
    """Impede que um teste abra uma caixa de dialogo real e trave a suite.

    O teste que espera o dialogo troca o metodo por um espiao com
    `monkeypatch.setattr`, depois desta fixture, e o espiao vence.
    """
    for name in _DIALOGS:
        monkeypatch.setattr(QMessageBox, name, staticmethod(_forbidden(name)))
