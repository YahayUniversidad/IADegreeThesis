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