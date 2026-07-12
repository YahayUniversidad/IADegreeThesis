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
from src.sql import (
    SQL_CREA_DIM_RIESGO,
    SQL_CREA_DIM_SECTOR,
    SQL_CREA_DIM_SUCURSAL,
    SQL_CREA_DIM_TIEMPO,
    SQL_CREA_FACT_CREDITOS,
    SQL_CREATE_IDX_MV,
    SQL_CREATE_MV,
    SQL_DROP_MV,
    SQL_INSERT_DIM_RIESGO,
    SQL_INSERT_DIM_SECTOR,
    SQL_INSERT_DIM_SUCURSAL,
    SQL_INSERT_DIM_TIEMPO,
    SQL_UPSERT_FACT_CREDITOS,
)


def _crear_ddl(conn):
    """Crea dimensiones y tabla de hechos (DDL).
    
    Args:
        conn: Conexion a la base de datos.
    
    """
    ddl_tablas = [
        ("dim_tiempo", SQL_CREA_DIM_TIEMPO),
        ("dim_riesgo", SQL_CREA_DIM_RIESGO),
        ("dim_sector", SQL_CREA_DIM_SECTOR),
        ("dim_sucursal", SQL_CREA_DIM_SUCURSAL),
        ("fact_creditos_mensual", SQL_CREA_FACT_CREDITOS),
    ]
    cur = conn.cursor()
    for nombre, ddl in ddl_tablas:
        cur.execute(ddl)
        print("OK: %s" % nombre)
    cur.close()


def _crear_mv(conn):
    """DROP + CREATE + INDEX de la vista materializada.
    
    Args:
        conn: Conexion a la base de datos.
    
    """
    cur = conn.cursor()
    print("Eliminando vista materializada anterior...")
    cur.execute(SQL_DROP_MV)
    print("Creando vista materializada...")
    cur.execute(SQL_CREATE_MV)
    print("Creando indice unico...")
    cur.execute(SQL_CREATE_IDX_MV)
    cur.close()
    print("Vista materializada mv_creditos_mensuales creada.")


def _refresh_mv(conn):
    """REFRESH MATERIALIZED VIEW CONCURRENTLY.
    
    Args:
        conn: Conexion a la base de datos.
    
    """
    cur = conn.cursor()
    cur.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_creditos_mensuales")
    cur.execute("SELECT COUNT(*) FROM mv_creditos_mensuales")
    count = cur.fetchone()[0]
    cur.close()
    print(f"MV refrescada: {count:,} registros")
    return count

def _pobrar_dim_generico(conn, nombre_dim, sql_insert):
    """Inserta datos en una dimension generica desde la MV.
    
    Args:
        conn: Conexion a la base de datos.
        nombre_dim: Nombre de la dimension.
        sql_insert: Sentencia SQL para insertar los datos.
    

    """
    cur = conn.cursor()
    cur.execute(sql_insert)
    print(f"{nombre_dim}: {cur.rowcount} filas insertadas")
    cur.close()


def _poblar_dims(conn):
    """Pobla todas las dimensiones.
    
    Args:
        conn: Conexion a la base de datos.
    
    """
    _pobrar_dim_generico(conn, "dim_riesgo", SQL_INSERT_DIM_TIEMPO)
    _pobrar_dim_generico(conn, "dim_riesgo", SQL_INSERT_DIM_RIESGO)
    _pobrar_dim_generico(conn, "dim_sector", SQL_INSERT_DIM_SECTOR)
    _pobrar_dim_generico(conn, "dim_sucursal", SQL_INSERT_DIM_SUCURSAL)


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


def ejecutar(string_conexion):
    """Ejecuta el pipeline completo: refresh MV -> dims -> fact -> validar.
    
    Args:
        string_conexion: Cadena de conexion a la base de datos.
    
    """

    conn = psycopg2.connect(string_conexion)

    try:
        _crear_ddl(conn)
        _crear_mv(conn)
        _refresh_mv(conn)
        _poblar_dims(conn)
        _poblar_fact(conn)
        _validar(conn)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar pipeline: {e}")
        raise
    finally:
        conn.close()