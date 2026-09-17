"""Herramientas MCP para consultar la base de datos y datamart."""

from __future__ import annotations

import json

import psycopg2.extras

from .db import get_conn, put_conn
from .security import validate_readonly_sql

_TABLES_OPS = ("creditos", "amortizacion", "juicios")
_TABLES_DM = (
    "dim_tiempo", "dim_riesgo", "dim_sector", "dim_sucursal",
    "fact_creditos_mensual", "fact_predicciones",
    "mv_creditos_mensuales", "mv_creditos", "mv_predicciones",
)


def get_schema(tables: list[str] | None = None) -> dict:
    """Devuelve el esquema (columnas, tipos, comentarios) de las tablas solicitadas."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        target = tables or list(_TABLES_OPS + _TABLES_DM)
        placeholders = ",".join(["%s"] * len(target))
        cur.execute(f"""
            SELECT
                c.table_name,
                c.column_name,
                c.data_type,
                c.is_nullable,
                pgd.description AS comment
            FROM information_schema.columns c
            LEFT JOIN pg_catalog.pg_statio_all_tables st
                ON c.table_schema = st.schemaname AND c.table_name = st.relname
            LEFT JOIN pg_catalog.pg_description pgd
                ON pgd.objoid = st.relid AND pgd.objsubid = c.ordinal_position
            WHERE c.table_schema = 'public'
              AND c.table_name IN ({placeholders})
            ORDER BY c.table_name, c.ordinal_position
        """, target)
        rows = cur.fetchall()
        cur.close()

        schema: dict[str, list] = {}
        for row in rows:
            tbl = row["table_name"]
            schema.setdefault(tbl, []).append({
                "columna": row["column_name"],
                "tipo": row["data_type"],
                "nullable": row["is_nullable"],
                "comentario": row["comment"],
            })
        return schema
    finally:
        put_conn(conn)


def query_sql(sql: str, limit: int = 100) -> dict:
    """Ejecuta una consulta SQL de solo lectura y devuelve los resultados."""
    ok, msg = validate_readonly_sql(sql)
    if not ok:
        return {"error": msg}

    if "LIMIT" not in sql.upper():
        sql = sql.rstrip().rstrip(";")
        sql += f" LIMIT {limit}"

    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(sql)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        return {"columns": columns, "rows": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        put_conn(conn)


def get_datamart_info() -> dict:
    """Devuelve informacion del datamart: dimensiones, hechos, conteos."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        info: dict = {}

        for table in _TABLES_DM:
            try:
                cur.execute(f"SELECT COUNT(*) AS cnt FROM {table}")
                cnt = cur.fetchone()["cnt"]
                info[table] = {"filas": cnt}
            except Exception:
                info[table] = {"filas": "no disponible (ejecutar datamart primero)"}

        cur.close()
        return info
    finally:
        put_conn(conn)


def get_sample_data(table: str, n: int = 5) -> dict:
    """Devuelve N filas de muestra de una tabla."""
    ok, msg = validate_readonly_sql(f"SELECT * FROM {table}")
    if not ok:
        return {"error": f"Tabla no permitida: {msg}"}

    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f"SELECT * FROM {table} LIMIT %s", (n,))
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        return {"table": table, "columns": columns, "rows": [dict(r) for r in rows]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        put_conn(conn)


def query_datamart(query_type: str, params: dict | None = None) -> dict:
    """Consultas predefinidas al datamart.

    query_type: 'crisis_tendencia' | 'resumen_sucursal' | 'predicciones_recientes'
    """
    params = params or {}
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        if query_type == "crisis_tendencia":
            cur.execute("""
                SELECT mes, riesgo, sector, codigo_sucursal,
                       num_creditos, crisis_flag, tasa_judicial, tasa_mora_90
                FROM mv_creditos_mensuales
                WHERE crisis_flag = 1
                ORDER BY mes DESC
                LIMIT 50
            """)
        elif query_type == "resumen_sucursal":
            sucursal = params.get("codigo_sucursal")
            where = "WHERE su.codigo_sucursal = %s" if sucursal else ""
            cur.execute(f"""
                SELECT su.codigo_sucursal, t.anio, t.trimestre,
                       SUM(f.num_creditos) AS total_creditos,
                       SUM(f.monto_total) AS monto_total,
                       AVG(f.tasa_mora_90) AS mora_promedio,
                       AVG(f.tasa_judicial) AS judicial_promedio
                FROM fact_creditos_mensual f
                JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
                JOIN dim_sucursal su ON f.id_sucursal = su.id_sucursal
                {where}
                GROUP BY su.codigo_sucursal, t.anio, t.trimestre
                ORDER BY t.anio DESC, t.trimestre DESC
                LIMIT 100
            """, [sucursal] if sucursal else None)
        elif query_type == "predicciones_recientes":
            cur.execute("""
                SELECT t.mes, r.codigo_riesgo, s.codigo_sector, su.codigo_sucursal,
                       p.prob_media, p.pred_media, p.crisis_count
                FROM fact_predicciones p
                JOIN dim_tiempo t ON p.id_tiempo = t.id_tiempo
                JOIN dim_riesgo r ON p.id_riesgo = r.id_riesgo
                JOIN dim_sector s ON p.id_sector = s.id_sector
                JOIN dim_sucursal su ON p.id_sucursal = su.id_sucursal
                ORDER BY t.mes DESC
                LIMIT 50
            """)
        else:
            return {"error": f"query_type desconocido: {query_type}. Opciones: crisis_tendencia, resumen_sucursal, predicciones_recientes"}

        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        return {"query_type": query_type, "columns": columns, "rows": [dict(r) for r in rows], "count": len(rows)}
    except Exception as e:
        return {"error": str(e)}
    finally:
        put_conn(conn)
