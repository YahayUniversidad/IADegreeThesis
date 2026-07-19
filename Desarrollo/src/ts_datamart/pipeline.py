##
## @file pipeline.py
##
## Pipeline del datamart: crea MV, dimensiones, fact table y valida integridad.
## Toda la logica SQL viene de src.sql.queries.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import psycopg2
from src.ts_sql import (
    SCRIPT_CREA_FACT_CREDITOS,
    SCRIPT_CREA_FACT_PREDICCIONES,
    SCRIPT_CREATE_MV_CREDITOS,
    SCRIPT_CREATE_MV_CREDITOS_MENSUALES,
    SCRIPT_CREATE_MV_PREDICCIONES,
    SQL_CREA_DIM_RIESGO,
    SQL_CREA_DIM_SECTOR,
    SQL_CREA_DIM_SUCURSAL,
    SQL_CREA_DIM_TIEMPO,
    SQL_INSERT_DIM_RIESGO,
    SQL_INSERT_DIM_SECTOR,
    SQL_INSERT_DIM_SUCURSAL,
    SQL_INSERT_DIM_TIEMPO,
    SQL_REFRESH_MV_CREDITOS,
    SQL_REFRESH_MV_CREDITOS_MENSUALES,
    SQL_REFRESH_MV_PREDICCIONES,
    SQL_UPSERT_FACT_CREDITOS,
    ejeucta_script_generico,
)


def _crear_ddl(string_conexion):
    """Crea dimensiones y tabla de hechos (DDL).

    Args:
        string_conexion: Cadena de conexión a la base de datos.

    """
    ddl_tablas = [
        ("dim_tiempo", SQL_CREA_DIM_TIEMPO),
        ("dim_riesgo", SQL_CREA_DIM_RIESGO),
        ("dim_sector", SQL_CREA_DIM_SECTOR),
        ("dim_sucursal", SQL_CREA_DIM_SUCURSAL),
        ("fact_creditos_mensual", SCRIPT_CREA_FACT_CREDITOS),
        ("fact_predicciones", SCRIPT_CREA_FACT_PREDICCIONES),
        ("mv_creditos_mensuales", SCRIPT_CREATE_MV_CREDITOS_MENSUALES),
        ("mv_predicciones", SCRIPT_CREATE_MV_PREDICCIONES),
        ("mv_creditos", SCRIPT_CREATE_MV_CREDITOS),
    ]
    for nombre, script in ddl_tablas:
        ejeucta_script_generico(string_conexion, script, nombre)


def _refresh_mv(conn):
    """Refresca las materialized views para el trabajo del datamart.

    Args:
        conn: Conexion a la base de datos.

    """
    refreshed_vm = [
        ("mv_creditos_mensuales", SQL_REFRESH_MV_CREDITOS_MENSUALES),
        ("mv_predicciones", SQL_REFRESH_MV_PREDICCIONES),
        ("mv_creditos", SQL_REFRESH_MV_CREDITOS),
    ]

    cur = conn.cursor()
    for nombre, sql in refreshed_vm:
        cur.execute(sql)
        cur.execute(f"SELECT COUNT(*) FROM {nombre}")
        count = cur.fetchone()[0]
        print(f"MV {nombre} refrescada: {count:,} registros")

    cur.close()


def _poblar_dims(conn):
    """Pobla todas las dimensiones.

    Args:
        conn: Conexion a la base de datos.

    """

    poblar_data = [
        ("dim_tiempo", SQL_INSERT_DIM_TIEMPO),
        ("dim_riesgo", SQL_INSERT_DIM_RIESGO),
        ("dim_sector", SQL_INSERT_DIM_SECTOR),
        ("dim_sucursal", SQL_INSERT_DIM_SUCURSAL),
    ]

    for nombre, sql in poblar_data:
        cur = conn.cursor()
        cur.execute(sql)
        print(f"{nombre}: {cur.rowcount} filas insertadas")
        cur.close()


def _poblar_fact(conn):
    """UPSERT de fact_creditos_mensual desde la MV.

    Args:
        conn: Conexion a la base de datos.

    """
    cur = conn.cursor()
    cur.execute(SQL_UPSERT_FACT_CREDITOS)
    count = cur.rowcount
    cur.close()
    print(f"fact_creditos_mensual: {count} filas insertadas/actualizadas")
    return count


def _validar(conn):
    """Verifica integridad del datamart: FKs nulas, duplicados, conteo.

    Args:
        conn: Conexion a la base de datos.

    """
    cur = conn.cursor()

    cur.execute(
        "SELECT COUNT(*) FROM fact_creditos_mensual "
        "WHERE id_tiempo IS NULL OR id_riesgo IS NULL OR id_sector IS NULL OR id_sucursal IS NULL"
    )
    nulls = cur.fetchone()[0]

    cur.execute(
        "SELECT COUNT(*) FROM ("
        "  SELECT id_tiempo, id_riesgo, id_sector, id_sucursal "
        "  FROM fact_creditos_mensual "
        "  GROUP BY id_tiempo, id_riesgo, id_sector, id_sucursal HAVING COUNT(*) > 1"
        ") t"
    )
    dups = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM fact_creditos_mensual")
    fact_rows = cur.fetchone()[0]

    cur.close()

    print(f"FKs nulas: {nulls}")
    print(f"Duplicados: {dups}")
    print(f"Fact rows: {fact_rows:,}")

    if nulls > 0:
        raise ValueError(f"Se encontraron {nulls} filas con FK nula")
    if dups > 0:
        raise ValueError(f"Se encontraron {dups} filas duplicadas")
    if fact_rows == 0:
        raise ValueError("fact_creditos_mensual esta vacia")

    print("Validacion exitosa")


def ejecutar_datamart(string_conexion):
    """Ejecuta el pipeline completo: refresh MV -> dims -> fact -> validar.

    Args:
        string_conexion: Cadena de conexion a la base de datos.

    Raises:
        ValueError: Si hay errores de integridad en el datamart.
    """

    conn = psycopg2.connect(string_conexion)

    try:
        _crear_ddl(string_conexion)
        _poblar_dims(conn)
        _refresh_mv(conn)
        _poblar_fact(conn)
        _validar(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
