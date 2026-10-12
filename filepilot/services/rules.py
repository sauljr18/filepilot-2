"""Regras personalizadas de organizacao (SPEC 6.6)."""

import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime

from filepilot.domain.errors import FilePilotError
from filepilot.domain.models import Rule

_MESSAGES = {
    "REGRA_INVALIDA": "Corrija os campos destacados da regra.",
    "REGRA_NAO_ENCONTRADA": "A regra não foi encontrada.",
    "BANCO_INDISPONIVEL": "Não foi possível acessar o histórico do FilePilot.",
}

_FIELD_MESSAGES = {
    "name": "Informe um nome de até 60 caracteres.",
    "extensions": "Informe ao menos uma extensão (letras e números, até 15).",
    "destination_folder": "Informe uma subpasta válida dentro da pasta escolhida.",
    "position": "Posição inválida.",
}

_NAME_MAX = 60
_EXTENSION_PATTERN = re.compile(r"[a-z0-9]{1,15}")
_SEGMENT_SEPARATORS = re.compile(r"[/\\]")
_SEGMENT_FORBIDDEN = frozenset('<>:"|?*')
_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{n}" for n in range(1, 10)}
    | {f"LPT{n}" for n in range(1, 10)}
)


def _error(code: str, fields: dict[str, str] | None = None) -> FilePilotError:
    return FilePilotError(code, _MESSAGES[code], fields)


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


@contextmanager
def _transaction(conn: sqlite3.Connection) -> Iterator[None]:
    """Transacao unica: tudo entra junto ou nada entra; falha do banco vira BANCO_INDISPONIVEL."""
    try:
        conn.execute("BEGIN")
    except sqlite3.Error as exc:
        raise _error("BANCO_INDISPONIVEL") from exc
    try:
        yield
        conn.commit()
    except BaseException as exc:
        conn.rollback()
        if isinstance(exc, sqlite3.Error):
            raise _error("BANCO_INDISPONIVEL") from exc
        raise


def _normalize_extension(raw: str) -> str:
    """Extensao sem espacos nas pontas, sem um `.` inicial e em minusculas."""
    value = raw.strip()
    if value.startswith("."):
        value = value[1:]
    return value.lower()


def _normalize_extensions(raw: list[str]) -> list[str] | None:
    """Extensoes normalizadas e sem repeticao; None quando nao ha nenhuma valida."""
    normalized = [_normalize_extension(item) for item in raw]
    if not normalized or not all(_EXTENSION_PATTERN.fullmatch(ext) for ext in normalized):
        return None
    return list(dict.fromkeys(normalized))


def _is_valid_segment(segment: str) -> bool:
    if segment in ("", ".", ".."):
        return False
    if any(char in _SEGMENT_FORBIDDEN for char in segment):
        return False
    if segment.endswith((".", " ")):
        return False
    return segment.upper() not in _RESERVED_NAMES


def _is_valid_destination(destination: str) -> bool:
    segments = _SEGMENT_SEPARATORS.split(destination)
    return all(_is_valid_segment(segment) for segment in segments)


def _validate(
    name: str, extensions: list[str], destination_folder: str
) -> tuple[str, list[str], str]:
    """Devolve os valores normalizados ou levanta REGRA_INVALIDA com `fields` por campo."""
    fields: dict[str, str] = {}
    clean_name = name.strip()
    if not 1 <= len(clean_name) <= _NAME_MAX:
        fields["name"] = _FIELD_MESSAGES["name"]
    clean_extensions = _normalize_extensions(extensions)
    if clean_extensions is None:
        fields["extensions"] = _FIELD_MESSAGES["extensions"]
    if not _is_valid_destination(destination_folder):
        fields["destination_folder"] = _FIELD_MESSAGES["destination_folder"]
    if fields or clean_extensions is None:
        raise _error("REGRA_INVALIDA", fields)
    return clean_name, clean_extensions, destination_folder


def list_rules(conn: sqlite3.Connection) -> list[Rule]:
    """Regras por `position` crescente, cada uma com as suas extensoes (6.6)."""
    try:
        rows = conn.execute(
            "SELECT id, name, destination_folder, position FROM rules ORDER BY position"
        ).fetchall()
        extension_rows = conn.execute(
            "SELECT rule_id, extension FROM rule_extensions"
        ).fetchall()
    except sqlite3.Error as exc:
        raise _error("BANCO_INDISPONIVEL") from exc
    by_rule: dict[int, set[str]] = {}
    for rule_id, extension in extension_rows:
        by_rule.setdefault(rule_id, set()).add(extension)
    return [
        Rule(
            id=row[0],
            name=row[1],
            destination_folder=row[2],
            position=row[3],
            extensions=frozenset(by_rule.get(row[0], set())),
        )
        for row in rows
    ]


def _insert_extensions(
    conn: sqlite3.Connection, rule_id: int, extensions: list[str]
) -> None:
    conn.executemany(
        "INSERT INTO rule_extensions (rule_id, extension) VALUES (?, ?)",
        [(rule_id, extension) for extension in extensions],
    )


def create_rule(
    conn: sqlite3.Connection,
    name: str,
    extensions: list[str],
    destination_folder: str,
) -> Rule:
    """Cria a regra na ultima posicao, com as extensoes normalizadas (6.6)."""
    clean_name, clean_extensions, destination = _validate(
        name, extensions, destination_folder
    )
    now = _utc_now()
    with _transaction(conn):
        position = conn.execute(
            "SELECT COALESCE(MAX(position), 0) + 1 FROM rules"
        ).fetchone()[0]
        cursor = conn.execute(
            "INSERT INTO rules (name, destination_folder, position, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (clean_name, destination, position, now, now),
        )
        rule_id = cursor.lastrowid
        assert rule_id is not None
        _insert_extensions(conn, rule_id, clean_extensions)
    return Rule(
        id=rule_id,
        name=clean_name,
        destination_folder=destination,
        position=position,
        extensions=frozenset(clean_extensions),
    )


def _current_position(conn: sqlite3.Connection, rule_id: int) -> int:
    row = conn.execute("SELECT position FROM rules WHERE id = ?", (rule_id,)).fetchone()
    if row is None:
        raise _error("REGRA_NAO_ENCONTRADA")
    return int(row[0])


def _renumber(conn: sqlite3.Connection, ordered_ids: list[int]) -> None:
    """Regrava as posicoes de 1 ate o total, na ordem dada, sem violar `UNIQUE (position)`.

    Em duas etapas na mesma transacao: todas as posicoes viram o valor
    negativo e depois recebem a posicao final.
    """
    old_positions = dict(conn.execute("SELECT id, position FROM rules").fetchall())
    conn.execute("UPDATE rules SET position = -position")
    now = _utc_now()
    for new_position, rule_id in enumerate(ordered_ids, start=1):
        if old_positions[rule_id] == new_position:
            conn.execute("UPDATE rules SET position = ? WHERE id = ?", (new_position, rule_id))
        else:
            conn.execute(
                "UPDATE rules SET position = ?, updated_at = ? WHERE id = ?",
                (new_position, now, rule_id),
            )


def _ordered_ids(conn: sqlite3.Connection) -> list[int]:
    rows = conn.execute("SELECT id FROM rules ORDER BY position").fetchall()
    return [row[0] for row in rows]


def update_rule(
    conn: sqlite3.Connection,
    rule_id: int,
    name: str,
    extensions: list[str],
    destination_folder: str,
) -> Rule:
    """Altera nome, extensoes e destino da regra, mantendo a `position` (6.6)."""
    clean_name, clean_extensions, destination = _validate(
        name, extensions, destination_folder
    )
    with _transaction(conn):
        position = _current_position(conn, rule_id)
        conn.execute(
            "UPDATE rules SET name = ?, destination_folder = ?, updated_at = ? WHERE id = ?",
            (clean_name, destination, _utc_now(), rule_id),
        )
        conn.execute("DELETE FROM rule_extensions WHERE rule_id = ?", (rule_id,))
        _insert_extensions(conn, rule_id, clean_extensions)
    return Rule(
        id=rule_id,
        name=clean_name,
        destination_folder=destination,
        position=position,
        extensions=frozenset(clean_extensions),
    )


def delete_rule(conn: sqlite3.Connection, rule_id: int) -> None:
    """Exclui a regra e as extensoes dela e reordena as demais sem lacunas (6.6)."""
    with _transaction(conn):
        _current_position(conn, rule_id)
        conn.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        _renumber(conn, _ordered_ids(conn))


def move_rule(conn: sqlite3.Connection, rule_id: int, new_position: int) -> list[Rule]:
    """Move a regra para `new_position` (de 1 ate o total) e devolve a lista reordenada (6.6)."""
    with _transaction(conn):
        _current_position(conn, rule_id)
        ordered = _ordered_ids(conn)
        if not 1 <= new_position <= len(ordered):
            raise _error("REGRA_INVALIDA", {"position": _FIELD_MESSAGES["position"]})
        ordered.remove(rule_id)
        ordered.insert(new_position - 1, rule_id)
        _renumber(conn, ordered)
    return list_rules(conn)
