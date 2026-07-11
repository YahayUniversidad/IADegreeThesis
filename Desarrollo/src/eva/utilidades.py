##
## @file utilidades.py
##
## Contiene funciones de utilidad para el proyecto EVA.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
import math

import polars as pl


def get_columnas_numericas(df: pl.DataFrame) -> list[str]:
    """
    Se obtiene todas las columnas numericas de mi dataframe
    esto necesito pues los numeros tiene un tratameiento para la parte numerica.
    """
    return [c for c in df.columns if df[c].dtype.is_numeric()]

def get_columnas_string(df: pl.DataFrame) -> list[str]:
    """
    Se obtiene todas las columnas de tipo string o categórico
    esto necesito pues los strings tienen un tratameiento para la parte de texto.
    """
    return [c for c in df.columns if df[c].dtype in (pl.String, pl.Categorical)]

def as_float(value):
    """Convierte un valor a float si no es None.

    Args:
        value: Valor a convertir.

    Returns:
        float si el valor no es None o null es mejor pasar como 0
    """
    if value is None:
        return 0.0

    try:
        n = float(value)
        return 0.0 if math.isnan(n) else n
    except (TypeError, ValueError):
        return 0.0

def informar_razon(logger, razon):
    """Convierte un valor a string y lo capitaliza.

    Args:
        logger: Instancia de logger para registrar el título.
        razon: Valor a presentar un subtitulo, puede contener '|' para indicar salto de línea.

    Returns:
        str: Valor capitalizado.
    """
    # Para que se separen los punto y coma del analisis, puse un separador temporal '|-' 
    # para que no se pierda la información de los motivos de exclusión, luego se reemplaza 
    # por un salto de línea '|'
    for linea in str(razon).replace(";", "|-").split("|"):
        print(f"   {linea.strip()}")
