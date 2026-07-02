##
## @file utilidades.py
##
## Contiene funciones de utilidad para el proyecto EVA.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
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
