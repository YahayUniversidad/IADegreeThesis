##
## @file riguroso.py
##
## Clase para EVA académico riguroso.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
import logging
import warnings
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns

from scipy.stats import (
    chi2_contingency,
    kstest,
    pearsonr,
    shapiro,
    spearmanr,
    ttest_ind,
)
from sklearn.feature_selection import mutual_info_classif
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_auc_score

from .utilidades import get_columnas_numericas, get_columnas_string

warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class EVAriguroso:
    """
    Clase para EVA académico riguroso.
    Cada variable es analizada cuantitativamente para decidir su inclusión.
    requiere de get_columnas_numericas y get_columnas_string de utilidades.py para poder indentificar dos formas de procesar segun su tipo de dato
    """

    def __init__(self, df: pl.DataFrame, target_col: str = "crisis_flag"):
        """Inicializa la clase EVAriguroso con los parametros indicados
        
        Args:
            self: Instancia de la clase EVAriguroso. En java es un this. 
            df (pl.DataFrame): DataFrame de entrada con los datos a analizar.
            target_col (str, optional): Nombre de la columna objetivo. Defaults to "crisis_flag".
            
        Returns:
            None
        """
        self.df = df
        self.target_col = target_col
        self.reporte_completo: list[dict] = []
        self.evidencias: dict = {}
        self.recomendaciones_finales: list[dict] = []

    def analizar_distribucion(self, col: str) -> dict:
        """Analiza distribución de una variable numérica        
        Args:
            self: Instancia de la clase EVAriguroso.
            col (str): Nombre de la columna a analizar.
        
        Returns:
            dict: Diccionario con estadísticas descriptivas de la columna.
            n: el largo
            nulos: cantidad de nulos
            pct_nulos: porcentaje de nulos
            min: valor mínimo
            max: valor máximo
            mean: media
            median: mediana
            std: desviación estándar
            skew: asimetría
            kurtosis: curtosis
            q1: primer cuartil
            q3: tercer cuartil
            iqr: rango intercuartílico
            pct_outliers: porcentaje de valores atípicos
            normalidad_test: nombre del test de normalidad utilizado
            normalidad_stat: estadístico del test de normalidad
            normalidad_pvalue: valor p del test de normalidad
            es_normal: booleano indicando si la distribución es normal (p > 0.05)
        """
        data = self.df[col].drop_nulls()

        q1 = float(data.quantile(0.25))
        q3 = float(data.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        pct_outliers = float(((data < lower) | (data > upper)).sum() / len(data) * 100)

        stats_dict = {
            "n": len(data),
            "nulos": self.df[col].is_null().sum(),
            "pct_nulos": self.df[col].is_null().mean() * 100,
            "min": float(data.min()),
            "max": float(data.max()),
            "mean": float(data.mean()),
            "median": float(data.median()),
            "std": float(data.std()),
            "skew": float(data.skew()),
            "kurtosis": float(data.kurtosis()),
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "pct_outliers": pct_outliers,
        }

        # Si la data es menor a 5000, se utiliza Shapiro-Wilk, de lo contrario Kolmogorov-Smirnov
        sample_size = min(5000, len(data))
        if len(data) < 5000:
            try:
                shapiro_stat, shapiro_p = shapiro(data.sample(sample_size))
                stats_dict["normalidad_test"] = "Shapiro-Wilk"
                stats_dict["normalidad_stat"] = float(shapiro_stat)
                stats_dict["normalidad_pvalue"] = float(shapiro_p)
                stats_dict["es_normal"] = shapiro_p > 0.05
            except Exception:
                stats_dict["es_normal"] = False
        else:
            try:
                sample = data.sample(sample_size)
                ks_stat, ks_p = kstest(sample, "norm", args=(data.mean(), data.std()))
                stats_dict["normalidad_test"] = "Kolmogorov-Smirnov"
                stats_dict["normalidad_stat"] = float(ks_stat)
                stats_dict["normalidad_pvalue"] = float(ks_p)
                stats_dict["es_normal"] = ks_p > 0.05
            except Exception:
                stats_dict["es_normal"] = False

        return stats_dict

 