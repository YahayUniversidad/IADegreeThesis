##
## @file utilidades.py
##
## Funciones utilitarias para el manejo de figuras y otros recursos comunes.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
import math
import os
import tempfile

import matplotlib.pyplot as plt
import mlflow
import polars as pl


def save_figura(fig, name, output_dir=None):
    """Guarda figura en disco y retorna el path.

    Args:
        fig: matplotlib figure object
        name: nombre base del archivo (sin extension)
        output_dir: directorio de salida (si None, usa temp dir)

    Returns:
        str: path completo del archivo guardado

    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        path = os.path.join(output_dir, f"{name}.png")
    else:
        path = os.path.join(tempfile.gettempdir(), f"{name}.png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


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
    
    
def configurar_mlflow(mlflow_tracking_uri: str, mlflow_experiment_name: str) -> mlflow: # type: ignore
    """ Configura MLflow para el seguimiento de experimentos.

    Args:
        mlflow_tracking_uri (str): URI de seguimiento de MLflow.
        mlflow_experiment_name (str): Nombre del experimento en MLflow.

    Returns:
        mlflow: Objeto mlflow configurado.
    """
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    try:
        mlflow.set_experiment(mlflow_experiment_name)
    except Exception:
        mlflow.create_experiment(mlflow_experiment_name)
        mlflow.set_experiment(mlflow_experiment_name)
        
    return mlflow

