import psycopg2


def ejeucta_script_generico(string_conexion, script, paso):
    """Ejecuta un script genérico en la base de datos.

    Ejecutar sql y script de creación de tablas en la base de datos. Maneja la conexión y el cursor,
    y realiza commit o rollback según corresponda.

    Args:
        string_conexion (str): Cadena de conexión a la base de datos.
        script (str): Script SQL a ejecutar.
        paso (str): Descripción del paso que se está ejecutando.

    """
    # Conexión principal
    conn = psycopg2.connect(string_conexion)
    cursor = conn.cursor()

    try:
        print(f"Paso: {paso}")
        cursor.execute(script)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error al ejecutar {paso}: {e}")
    finally:
        cursor.close()
        conn.close()
