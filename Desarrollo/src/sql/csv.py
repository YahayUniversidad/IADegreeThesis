##
## @file csv.py
##
## Contiene funciones para capturar y procesar archivos CSV en la base de datos.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import sys
from pathlib import Path

sys.path.insert(0, "..")

import polars as pl
import psycopg2
from psycopg2 import sql
from src.sql.queries import (
    SCRIPT_CREATE_TABLE_TEMPORAL_CSV,
    SQL_CREATE_TABLE_AMORTIZACION,
    SQL_CREATE_TABLE_CREDITOS,
    SQL_CREATE_TABLE_JUICIOS,
)
from src.sql.utilidades import ejeucta_script_generico


def crear_tablas_estructura(string_conexion):
    """Crea o actualiza la estructura de las tablas en la base de datos.
    Args:
        string_conexion (str): Cadena de conexión a la base de datos.
    """

    ## Crea o Actualiza la estructura de las tablas en la base de datos
    ejeucta_script_generico(string_conexion, SQL_CREATE_TABLE_CREDITOS, "Crea tabla creditos")
    ejeucta_script_generico(
        string_conexion, SQL_CREATE_TABLE_AMORTIZACION, "Crea tabla amortizacion"
    )
    ejeucta_script_generico(string_conexion, SQL_CREATE_TABLE_JUICIOS, "Crea tabla juicios")
    ejeucta_script_generico(
        string_conexion, SCRIPT_CREATE_TABLE_TEMPORAL_CSV, "Crea tabla temporal"
    )


def capturar_datos_csv(string_conexion, path_carpeta):
    """
    Captura los datos de todos los archivos CSV en la carpeta especificada.

    Args:
        string_conexion (str): Cadena de conexión a la base de datos.
        path_carpeta (Path): Ruta de la carpeta que contiene los archivos CSV.

    Raises:
        Exception: Si ocurre un error durante la captura de datos o la eliminación de archivos CSV.

    Returns:
        list: Lista de rutas de archivos CSV encontrados en la carpeta.
    """

    carpeta = Path(path_carpeta)

    archivos_csv = list(carpeta.glob("*.csv"))

    if not archivos_csv:
        print("No se encontraron archivos CSV en la carpeta.")
    else:
        for archivo in archivos_csv:
            try:
                print(f"Datos leídos de {archivo.name}:")
                _ejecutar_proceso_csv(string_conexion, archivo)
                archivo.unlink()
                print(f"Archivo eliminado con éxito: {archivo.name}")
            except Exception as e:
                print(f"Error al procesar o borrar {archivo.name}: {e}")


def _ejecutar_proceso_csv(string_conexion, file_path_csv):
    """Ejecuar proceso de csv

    Procesa un archivo CSV y lo carga en la tabla correspondiente según el número de columnas.
        39: Carga en la tabla "creditos".
        16: Carga en la tabla "amortizacion".
        9: Carga en la tabla "juicios".

    Args:
        string_conexion (str): Cadena de conexión a la base de datos.
        file_path_csv (Path): Ruta del archivo CSV a procesar.

    Raises:
        ValueError: Si el número de columnas del CSV no coincide con ninguna tabla definida.
    """

    df = pl.read_csv(file_path_csv, n_rows=1, ignore_errors=True)

    if len(df.columns) == 39:
        _cargar_csv(string_conexion, file_path_csv, "creditos", "numero_credito")
        return

    if len(df.columns) == 16:
        _cargar_csv(string_conexion, file_path_csv, "amortizacion", "numero_credito, ordencal")
        return

    if len(df.columns) == 9:
        _cargar_csv(string_conexion, file_path_csv, "juicios", "numero_credito")
        return
    else:
        raise ValueError(f"No definido {file_path_csv}")


def _cargar_csv(string_conexion, file_path_csv, nombre_tabla, columnas_conflicto):
    """Carga un archivo CSV en la tabla temporal correspondiente y luego lo inserta en la tabla
    principal.

    Args:
        string_conexion (str): Cadena de conexión a la base de datos.
        file_path_csv (Path): Ruta del archivo CSV a cargar.
        nombre_tabla (str): Nombre de la tabla principal donde se insertarán los datos.
        columnas_conflicto (str): Columnas que se usarán para manejar conflictos durante la
        inserción (ON CONFLICT).

    Raises:
        Exception: Si ocurre un error durante la carga del CSV o la inserción en la tabla principal.

    """
    # Conexión principal
    conn = psycopg2.connect(string_conexion)
    cursor = conn.cursor()

    try:
        print(f"\nSube archivo a pivote: pivot_{file_path_csv}")
        query_cp = sql.SQL("""
            COPY {temp_pivot_table} FROM STDIN WITH CSV HEADER DELIMITER ','
            """).format(temp_pivot_table=sql.Identifier(f"pivot_{nombre_tabla}"))

        with open(file_path_csv, "r", encoding="utf-8") as f:
            cursor.copy_expert(query_cp, f)

        print(f"Carga tabla sin duplicidad: {nombre_tabla}")
        query = sql.SQL("""
            INSERT INTO {temp_table}
            SELECT * FROM {temp_pivot_table}
            ON CONFLICT ({temp_conflict}) DO NOTHING;
        """).format(
            temp_table=sql.Identifier(nombre_tabla),
            temp_pivot_table=sql.Identifier(f"pivot_{nombre_tabla}"),
            temp_conflict=sql.SQL(columnas_conflicto),
        )
        cursor.execute(query)
        filas_creadas = cursor.rowcount
        print(f"Se crearon exitosamente {filas_creadas} nuevos registros.")
        conn.commit()

        print(f"Limpia pivote de: {nombre_tabla}")
        queryClean = sql.SQL(
            """
            delete from {temp_pivot_table}; 
            """
        ).format(temp_pivot_table=sql.Identifier(f"pivot_{nombre_tabla}"))
        cursor.execute(queryClean)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar {nombre_tabla}: {e}")
    finally:
        cursor.close()
        conn.close()
