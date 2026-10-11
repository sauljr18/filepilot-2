"""Modelos de dominio do FilePilot (SPEC 6.1, 6.2, 6.3 e 6.6).

Os nomes dos campos seguem as colunas de 5.3 e 5.4.
"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class ScannedFile:
    """Arquivo regular encontrado no nivel da pasta escolhida (6.1)."""

    path: Path
    name: str
    extension: str
    size_bytes: int


@dataclass(frozen=True)
class Rule:
    """Regra personalizada de organizacao (6.2 e 6.6)."""

    id: int
    name: str
    destination_folder: str
    position: int
    extensions: frozenset[str]


@dataclass(frozen=True)
class PlannedOperation:
    """Movimentacao planejada de um arquivo (6.2)."""

    seq: int
    source_path: Path
    destination_path: Path
    category: str | None
    rule_name: str | None


@dataclass
class Plan:
    """Plano de organizacao: operacoes e arquivos sem categoria (6.2)."""

    folder: Path
    operations: list[PlannedOperation] = field(default_factory=list)
    skipped: list[ScannedFile] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.operations


@dataclass
class OrganizationResult:
    """Resultado de uma organizacao real (6.3)."""

    organization_id: int
    moved_count: int
    failed_count: int
    failures: list[tuple[str, str]] = field(default_factory=list)
