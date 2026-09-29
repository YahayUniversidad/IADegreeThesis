"""Validador de SQL: solo permite consultas de lectura."""

import re

_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|EXECUTE)\b",
    re.IGNORECASE,
)


def validate_readonly_sql(sql: str) -> tuple[bool, str]:
    """Valida que el SQL sea solo lectura (SELECT/SHOW/EXPLAIN).

    Returns:
        (es_valido, mensaje_error_o_ok)
    """
    stripped = sql.strip().rstrip(";").strip()
    if not stripped:
        return False, "SQL vacio"

    first_word = stripped.split()[0].upper()
    if first_word not in ("SELECT", "SHOW", "EXPLAIN", "WITH"):
        return False, f"Operacion no permitida: {first_word}. Solo SELECT/SHOW/EXPLAIN."

    if _FORBIDDEN_KEYWORDS.search(stripped):
        found = _FORBIDDEN_KEYWORDS.findall(stripped)
        return False, f"Palabras prohibidas detectadas: {', '.join(found)}"

    return True, "OK"
