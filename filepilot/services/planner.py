"""Planejamento das operacoes de organizacao (SPEC 6.2).

So le o disco (nomes ja existentes nos destinos): nao cria pastas, nao move
arquivos e nao toca no banco. Simulacao e organizacao usam esta mesma funcao.
"""

import os
from pathlib import Path

from filepilot.domain.categories import CATEGORIES
from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import (
    Plan,
    PlannedOperation,
    Rule,
    ScannedFile,
)
from filepilot.services.scanner import resolve_folder

_MESSAGES = {
    "DESTINO_FORA_DA_PASTA": "O destino fica fora da pasta escolhida.",
}


def _error(code: str) -> FilePilotError:
    return FilePilotError(code, _MESSAGES[code])


def _target(extension: str, rules: list[Rule]) -> tuple[str, str | None, str | None] | None:
    """Subpasta, categoria e nome da regra do arquivo; a regra vence a categoria."""
    for rule in sorted(rules, key=lambda item: item.position):
        if extension in rule.extensions:
            return rule.destination_folder, None, rule.name
    for key, category in CATEGORIES.items():
        if extension in category.extensions:
            return category.folder, key, None
    return None


def _existing_names(directory: Path) -> set[str]:
    """Nomes ja presentes no destino, sem diferenciar maiusculas; pasta ausente e vazia."""
    try:
        with os.scandir(directory) as entries:
            return {entry.name.casefold() for entry in entries}
    except OSError:
        return set()


def _inside(folder: Path, destination: Path) -> bool:
    return resolve_folder(destination).is_relative_to(resolve_folder(folder))


def _free_name(name: str, taken: set[str]) -> str:
    """Nome livre: o proprio ou `<base> (n)<ext>` com n crescente a partir de 1."""
    if name.casefold() not in taken:
        return name
    suffix = Path(name).suffix
    base = name[: len(name) - len(suffix)]
    number = 1
    while f"{base} ({number}){suffix}".casefold() in taken:
        number += 1
    return f"{base} ({number}){suffix}"


def build_plan(folder: Path, files: list[ScannedFile], rules: list[Rule]) -> Plan:
    """Calcula as operacoes de `files` sem tocar no disco nem no banco (6.2)."""
    operations: list[PlannedOperation] = []
    skipped: list[ScannedFile] = []
    taken_by_directory: dict[str, set[str]] = {}
    for item in files:
        target = _target(item.extension, rules)
        if target is None:
            skipped.append(item)
            continue
        subfolder, category, rule_name = target
        directory = folder / subfolder
        if not _inside(folder, directory / item.name):
            raise _error("DESTINO_FORA_DA_PASTA")
        key = str(directory).casefold()
        if key not in taken_by_directory:
            taken_by_directory[key] = _existing_names(directory)
        taken = taken_by_directory[key]
        final_name = _free_name(item.name, taken)
        taken.add(final_name.casefold())
        destination = directory / final_name
        if not _inside(folder, destination):
            raise _error("DESTINO_FORA_DA_PASTA")
        operations.append(
            PlannedOperation(
                seq=len(operations) + 1,
                source_path=item.path,
                destination_path=destination,
                category=category,
                rule_name=rule_name,
            )
        )
    return Plan(folder=folder, operations=operations, skipped=skipped)
