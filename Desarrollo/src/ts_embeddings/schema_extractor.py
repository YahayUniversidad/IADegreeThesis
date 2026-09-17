"""Extrae el esquema y datos de muestra de PostgreSQL."""

from __future__ import annotations

import psycopg2
import psycopg2.extras

from src.ts_config import DATABASE_URL


def extract_full_schema() -> list[dict]:
    """Extrae el esquema completo de todas las tablas publicas.

    Returns:
        Lista de dicts con: table_name, columns (lista de dicts con name, type, comment)
    """
    conn = psycopg2.connect(DATABASE_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [r["table_name"] for r in cur.fetchall()]

        cur.execute("""
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
            ORDER BY c.table_name, c.ordinal_position
        """)
        all_cols = cur.fetchall()

        cur.execute("""
            SELECT
                matviewname AS table_name
            FROM pg_matviews
            WHERE schemaname = 'public'
            ORDER BY matviewname
        """)
        mviews = [r["table_name"] for r in cur.fetchall()]

        cur.close()

        schema = []
        for tbl in tables + mviews:
            cols = [c for c in all_cols if c["table_name"] == tbl]
            schema.append({
                "table_name": tbl,
                "table_type": "materialized_view" if tbl in mviews else "table",
                "columns": [
                    {
                        "name": c["column_name"],
                        "type": c["data_type"],
                        "nullable": c["is_nullable"],
                        "comment": c["comment"],
                    }
                    for c in cols
                ],
            })
        return schema
    finally:
        conn.close()


def extract_sample_data(table_name: str, n: int = 5) -> list[dict]:
    """Extrae N filas de muestra de una tabla."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(f"SELECT * FROM {table_name} LIMIT %s", (n,))
        rows = [dict(r) for r in cur.fetchall()]
        cur.close()
        return rows
    except Exception:
        return []
    finally:
        conn.close()


def extract_table_comment(table_name: str) -> str | None:
    """Extrae el comentario de una tabla."""
    conn = psycopg2.connect(DATABASE_URL)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT obj_description(oid) AS comment
            FROM pg_class
            WHERE relname = %s AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
        """, (table_name,))
        row = cur.fetchone()
        cur.close()
        return row[0] if row else None
    finally:
        conn.close()
