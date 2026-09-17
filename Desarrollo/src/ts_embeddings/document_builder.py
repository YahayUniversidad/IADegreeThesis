##
## @file document_builder.py
##
## Convierte esquema y datos de muestra en documentos de texto para embeddings.
##
## @author omargo33
## @version septiembre 2026
##

from __future__ import annotations

from .schema_extractor import extract_full_schema, extract_sample_data, extract_table_comment

def _format_column(col: dict) -> str:
    """ Formato de columna para el documento de esquema.
    
    Args:
        col (dict): Diccionario con la información de la columna.

    Returns:
        str: Representación en texto de la columna.
    """    
    parts = [f"{col['name']} ({col['type']})"]
    if col.get("comment"):
        parts.append(f"- {col['comment']}")
    return " ".join(parts)

def build_schema_documents() -> list[dict]:
    """Genera documentos de texto a partir del esquema de la BD.

    Returns:
        Lista de dicts con la información de los documentos generados: id, text, metadata
    """
    schema = extract_full_schema()
    docs = []

    for table in schema:
        tname = table["table_name"]
        comment = extract_table_comment(tname)
        table_type = table["table_type"]

        lines = [f"Tabla: {tname} (tipo: {table_type})"]
        if comment:
            lines.append(f"Descripcion: {comment}")
        lines.append("Columnas:")
        for col in table["columns"]:
            lines.append(f"  - {_format_column(col)}")

        text = "\n".join(lines)
        docs.append({
            "id": f"schema_{tname}",
            "text": text,
            "metadata": {"type": "schema", "table": tname, "table_type": table_type},
        })

    return docs

def build_sample_documents(n: int = 5) -> list[dict]:
    """Genera documentos de texto con filas de muestra de cada tabla.

    Returns:
        Lista de dicts con: id, text, metadata
    """
    schema = extract_full_schema()
    docs = []

    for table in schema:
        tname = table["table_name"]
        samples = extract_sample_data(tname, n)
        if not samples:
            continue

        lines = [f"Ejemplo de datos de la tabla '{tname}' ({len(samples)} filas):"]
        for i, row in enumerate(samples):
            row_parts = [f"{k}={v}" for k, v in row.items() if v is not None]
            lines.append(f"  Fila {i+1}: {', '.join(row_parts[:10])}")
            if len(row_parts) > 10:
                lines.append(f"    ... y {len(row_parts) - 10} columnas mas")

        text = "\n".join(lines)
        docs.append({
            "id": f"sample_{tname}",
            "text": text,
            "metadata": {"type": "sample", "table": tname},
        })

    return docs


def build_fewshot_documents() -> list[dict]:
    """Genera documentos few-shot: pares pregunta -> SQL.
    
    few-shot es pocos ejemplos.

    Returns:
        Lista de dicts con: id, text, metadata
    """
    examples = [
        {
            "id": "fewshot_1",
            "text": (
                "Pregunta: ¿Cuantos creditos hay por sucursal?\n"
                "SQL: SELECT codigo_sucursal, COUNT(*) AS total_creditos "
                "FROM creditos GROUP BY codigo_sucursal ORDER BY total_creditos DESC"
            ),
            "metadata": {"type": "fewshot", "domain": "creditos"},
        },
        {
            "id": "fewshot_2",
            "text": (
                "Pregunta: ¿Cual es el monto total de creditos en crisis?\n"
                "SQL: SELECT SUM(monto_total) AS total_crisis "
                "FROM mv_creditos_mensuales WHERE crisis_flag = 1"
            ),
            "metadata": {"type": "fewshot", "domain": "crisis"},
        },
        {
            "id": "fewshot_3",
            "text": (
                "Pregunta: ¿Cuales son las predicciones mas recientes?\n"
                "SQL: SELECT t.mes, r.codigo_riesgo, s.codigo_sector, su.codigo_sucursal, "
                "p.prob_media, p.pred_media "
                "FROM fact_predicciones p "
                "JOIN dim_tiempo t ON p.id_tiempo = t.id_tiempo "
                "JOIN dim_riesgo r ON p.id_riesgo = r.id_riesgo "
                "JOIN dim_sector s ON p.id_sector = s.id_sector "
                "JOIN dim_sucursal su ON p.id_sucursal = su.id_sucursal "
                "ORDER BY t.mes DESC LIMIT 20"
            ),
            "metadata": {"type": "fewshot", "domain": "predicciones"},
        },
        {
            "id": "fewshot_4",
            "text": (
                "Pregunta: ¿Cual es la tasa de mora promedio por sector?\n"
                "SQL: SELECT ds.codigo_sector, AVG(f.tasa_mora_90) AS mora_promedio "
                "FROM fact_creditos_mensual f "
                "JOIN dim_sector ds ON f.id_sector = ds.id_sector "
                "GROUP BY ds.codigo_sector ORDER BY mora_promedio DESC"
            ),
            "metadata": {"type": "fewshot", "domain": "mora"},
        },
        {
            "id": "fewshot_5",
            "text": (
                "Pregunta: ¿Cuantos creditos judiciales hay?\n"
                "SQL: SELECT COUNT(*) AS creditos_judiciales "
                "FROM creditos WHERE judicial = 'S'"
            ),
            "metadata": {"type": "fewshot", "domain": "judicial"},
        },
        {
            "id": "fewshot_6",
            "text": (
                "Pregunta: ¿Cual es el promedio de tasa de interes por anio?\n"
                "SQL: SELECT t.anio, AVG(f.tasa_interes_promedio) AS tasa_promedio "
                "FROM fact_creditos_mensual f "
                "JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo "
                "GROUP BY t.anio ORDER BY t.anio"
            ),
            "metadata": {"type": "fewshot", "domain": "interes"},
        },
    ]
    return examples


def build_all_documents() -> list[dict]:
    """Genera todos los documentos para embeddings.

    Combina documentos de esquema, datos de muestra y ejemplos few-shot en una sola lista.
    
    Returns:
        list[dict]: Lista de documentos para embeddings.
    """
    docs = []
    docs.extend(build_schema_documents())
    docs.extend(build_sample_documents(n=5))
    docs.extend(build_fewshot_documents())
    return docs
