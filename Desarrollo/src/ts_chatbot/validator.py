"""Validacion de SQL generado por el chatbot."""

from __future__ import annotations

import re

_FORBIDDEN = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|EXECUTE|COPY)\b",
    re.IGNORECASE,
)


def extract_sql_from_response(response: str) -> str | None:
    """Extrae el bloque SQL de la respuesta del LLM.

    Busca bloques ```sql ... ``` o ``` ... ```
    """
    pattern = r"```(?:sql)?\s*\n?(.*?)```"
    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()

    lines = response.split("\n")
    sql_lines = []
    in_sql = False
    for line in lines:
        upper = line.strip().upper()
        if upper.startswith("SELECT") or upper.startswith("WITH"):
            in_sql = True
        if in_sql:
            sql_lines.append(line)
            if line.strip().endswith(";"):
                break

    if sql_lines:
        return "\n".join(sql_lines).strip()
    return None


def validate_sql(sql: str) -> tuple[bool, str]:
    """Valida que el SQL sea seguro (solo lectura).

    Returns:
        (es_valido, mensaje)
    """
    stripped = sql.strip().rstrip(";").strip()
    if not stripped:
        return False, "SQL vacio"

    first_word = stripped.split()[0].upper()
    if first_word not in ("SELECT", "WITH", "SHOW", "EXPLAIN"):
        return False, f"Operacion no permitida: {first_word}"

    if _FORBIDDEN.search(stripped):
        found = _FORBIDDEN.findall(stripped)
        return False, f"Palabras prohibidas: {', '.join(found)}"

    return True, "OK"
