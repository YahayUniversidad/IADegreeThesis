##
## @file riguroso.py
##
## Motor de análisis EVA — solo métodos atómicos.
## No orquesta, no loguea, no grafica, no guarda archivos.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
import numpy as np
import polars as pl
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
from src.common.utilidades import as_float


class AnalisisRiguroso:
    """ Clase para EVA académico riguroso.
    
    Cada variable es analizada cuantitativamente para decidir su inclusión.
    Requiere de get_columnas_numericas y get_columnas_string de utilidades.py para poder identificar
    dos formas de procesar según su tipo de dato.

    """

    def __init__(self, df: pl.DataFrame, target_col: str = "crisis_flag"):
        """Inicializa la clase AnalisisRiguroso con los parametros indicados

        Args:
            self: Instancia de la clase AnalisisRiguroso. En java es un this.
            df (pl.DataFrame): DataFrame de entrada con los datos a analizar.
            target_col (str, optional): Nombre de la columna objetivo. Defaults to "crisis_flag".

        Returns:
            None
        """
        self.df = df
        self.target_col = target_col

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

        q1 = as_float(data.quantile(0.25))
        q3 = as_float(data.quantile(0.75))
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        pct_outliers = float(((data < lower) | (data > upper)).sum() / len(data) * 100)

        stats_dict = {
            "n": len(data),
            "nulos": self.df[col].is_null().sum(),
            "pct_nulos": as_float(self.df[col].is_null().mean()) * 100,
            "min": as_float(data.min()),
            "max": as_float(data.max()),
            "mean": as_float(data.mean()),
            "median": as_float(data.median()),
            "std": as_float(data.std()),
            "skew": as_float(data.skew()),
            "kurtosis": as_float(data.kurtosis()),
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "pct_outliers": pct_outliers,
        }

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

    def analizar_correlacion(self, col: str) -> dict:
        """
        Analiza correlación exhaustiva con target

        Args:
            self: Instancia de la clase EVAriguroso.
            col (str): Nombre de la columna a analizar.

        Returns:
            dict: Diccionario con los resultados del análisis de correlación.
            resultados["pearson_r"]: Coeficiente de correlación de Pearson.
            resultados["pearson_pvalue"]: Valor p del test de Pearson.
            resultados["pearson_significativo"]: Booleano indicando si la correlación de Pearson 
            es significativa (p < 0.05).
            resultados["spearman_r"]: Coeficiente de correlación de Spearman.
            resultados["spearman_pvalue"]: Valor p del test de Spearman.
            resultados["spearman_significativo"]: Booleano indicando si la correlación de Spearman 
            es significativa (p < 0.05).
            resultados["mutual_information"]: Valor de información mutua.
            resultados["auc_roc_individual"]: Valor de AUC-ROC individual.
            resultados["poder_discriminativo"]: Categorización del poder discriminativo basado 
            en AUC-ROC.
            resultados["ttest_stat"]: Estadístico t del test de diferencia de medias.
            resultados["ttest_pvalue"]: Valor p del test t.
            resultados["dif_medias_significativa"]: Booleano indicando si la diferencia de medias es
            significativa (p < 0.05).
            resultados["diferencia_medias"]: Diferencia de medias entre las clases.
            resultados["cohens_d"]: Valor de Cohen's d.
        """
        data = self.df.select([col, self.target_col]).drop_nulls()

        if len(data) < 10:
            return {"error": "Muestra insuficiente"}

        x = data[col]
        y = data[self.target_col]
        resultados: dict = {}

        try:
            pearson_r, pearson_p = pearsonr(x, y)
            resultados["pearson_r"] = as_float(pearson_r)
            resultados["pearson_pvalue"] = as_float(pearson_p)
            resultados["pearson_significativo"] = as_float(pearson_p) < 0.05
        except Exception:
            resultados["pearson_r"] = 0.0
            resultados["pearson_pvalue"] = 1.0
            resultados["pearson_significativo"] = False

        try:
            spearman_r, spearman_p = spearmanr(x, y)
            resultados["spearman_r"] = as_float(spearman_r)
            resultados["spearman_pvalue"] = as_float(spearman_p)
            resultados["spearman_significativo"] = as_float(spearman_p) < 0.05
        except Exception:
            resultados["spearman_r"] = 0.0
            resultados["spearman_significativo"] = False

        try:
            mi = mutual_info_classif(x.to_numpy().reshape(-1, 1), y)[0]
            resultados["mutual_information"] = float(mi)
        except Exception:
            resultados["mutual_information"] = 0.0

        try:
            if len(np.unique(y)) > 1:
                auc = roc_auc_score(y, x)
                resultados["auc_roc_individual"] = float(auc)
                resultados["poder_discriminativo"] = (
                    "ALTO" if auc > 0.7 else ("MODERADO" if auc > 0.6 else "BAJO")
                )
            else:
                resultados["auc_roc_individual"] = 0.5
                resultados["poder_discriminativo"] = "SIN VARIABILIDAD"
        except Exception:
            resultados["auc_roc_individual"] = 0.5
            resultados["poder_discriminativo"] = "ERROR"

        try:
            class_0 = x.filter(y == 0)
            class_1 = x.filter(y == 1)
            if len(class_0) > 1 and len(class_1) > 1:
                t_stat, t_p = ttest_ind(class_0, class_1)
                resultados["ttest_stat"] = as_float(t_stat)
                resultados["ttest_pvalue"] = as_float(t_p)
                resultados["dif_medias_significativa"] = as_float(t_p) < 0.05
                diff =  as_float(class_1.mean()) - as_float(class_0.mean())
                resultados["diferencia_medias"] = diff
                pooled_std = np.sqrt(
                    (
                        len(class_0) * as_float(class_0.std()) ** 2
                        + len(class_1) * as_float(class_1.std()) ** 2
                    )
                    / (len(class_0) + len(class_1) - 2)
                )
                resultados["cohens_d"] = (
                    as_float(diff / pooled_std) if pooled_std > 0 else 0
                )
            else:
                resultados["dif_medias_significativa"] = False
                resultados["diferencia_medias"] = 0.0
                resultados["cohens_d"] = 0.0
        except Exception:
            resultados["dif_medias_significativa"] = False
            resultados["diferencia_medias"] = 0.0
            resultados["cohens_d"] = 0.0

        return resultados

    def calcular_vif(
        self, df_numeric: pl.DataFrame, col_excluir: str | None = None
    ) -> pl.DataFrame:
        """ Calcula VIF para detectar multicolinealidad
            
        VIF sirve para ver si las variables independientes (las que usas para predecir)
        están demasiado correlacionadas entre sí, lo que daña la precisión de tu
        modelo estadístico.

        Args:
            self: Instancia de la clase EVAriguroso.
            df_numeric: DataFrame con variables numéricas.
            col_excluir: Columna a excluir del cálculo de VIF. Valor por defecto es None.

        Returns:
            dict: Diccionario con los resultados del cálculo de VIF.
            returns["variable"]: Nombre de la variable.
            returns["VIF"]: Valor de VIF para la variable.
        """
        if col_excluir:
            df_numeric = df_numeric.drop([col_excluir])

        vif_values: list[float] = []
        for i in range(len(df_numeric.columns)):
            y_pl = df_numeric[:, i]
            X_pl = df_numeric.drop(df_numeric.columns[i])

            if X_pl.shape[1] == 0:
                vif_values.append(1.0)
            else:
                try:
                    X_np = X_pl.to_numpy()
                    y_np = y_pl.to_numpy().ravel()

                    model = LinearRegression().fit(X_np, y_np)
                    r2 = model.score(X_np, y_np)

                    vif = 1 / (1 - r2) if r2 != 1 else 1000
                    vif_values.append(as_float(vif))
                except Exception:
                    vif_values.append(1000)

        return pl.DataFrame({"variable": df_numeric.columns, "VIF": vif_values})

    def analizar_variable_categorica(self, col: str) -> dict:
        """
        Analiza variable categórica con objetivo de crisis_flag y calcula estadísticas relevantes.

        Args:
            self: Instancia de la clase EVAriguroso.
            col (str): Nombre de la columna categórica a analizar.

        Returns:
            dict: Diccionario con los resultados del análisis de la variable categórica.
            resultados["num_categorias"]: Número de categorías únicas.
            resultados["top_categorias"]: Diccionario de 10 categorías más frecuentes y sus conteos.
            resultados["categoria_dominante"]: Categoría con mayor frecuencia.
            resultados["pct_categoria_dominante"]: Porcentaje de la categoría dominante.
            resultados["crisis_por_categoria"]: Diccionario con estadísticas de crisis por categoría
            resultados["chi2_stat"]: Estadístico chi-cuadrado para independencia.
            resultados["chi2_pvalue"]: Valor p del test chi-cuadrado.
            resultados["chi2_significativo"]: Booleano indicando la independencia es significativa
            resultados["cramers_v"]: Valor de V de Cramer para medir la fuerza de la asociación.
        """
        resultados: dict = {}

        value_counts = self.df[col].value_counts()
        resultados["num_categorias"] = len(value_counts)
        resultados["top_categorias"] = value_counts.head(10).to_dict()
        resultados["categoria_dominante"] = (
            value_counts[col][0] if len(value_counts) > 0 else None
        )
        resultados["pct_categoria_dominante"] = (
            float(value_counts["count"][0] / len(self.df) * 100)
            if len(value_counts) > 0
            else 0
        )

        crisis_por_categoria = self.df.group_by(col).agg(
            [
                pl.col(self.target_col).mean().alias("mean"),
                pl.col(self.target_col).count().alias("count"),
                pl.col(self.target_col).std().alias("std"),
            ]
        )
        resultados["crisis_por_categoria"] = crisis_por_categoria.head(10).to_dict()

        try:
            ct = self.df.group_by([col, self.target_col]).len()
            ct = ct.pivot(index=col, on=self.target_col, values="len").fill_null(0)
            contingency_table = ct.select(pl.exclude(col)).to_numpy()
            chi2, p_value, _dof, _expected = chi2_contingency(contingency_table)
            resultados["chi2_stat"] = as_float(chi2)
            resultados["chi2_pvalue"] = as_float(p_value)
            resultados["chi2_significativo"] = as_float(p_value) < 0.05

            n = len(self.df)
            min_dim = min(contingency_table.shape) - 1
            if min_dim > 0:
                resultados["cramers_v"] = float(np.sqrt(chi2 / (n * min_dim)))
            else:
                resultados["cramers_v"] = 0.0
        except Exception:
            resultados["chi2_significativo"] = False
            resultados["cramers_v"] = 0.0

        return resultados

    def evaluar_completitud(self, col: str) -> dict:
        """
        Evalúa si los datos son completos y confiables

        Args:
            self: Instancia de la clase EVAriguroso.
            col (str): Nombre de la columna a evaluar.
        Results:
            dict: Diccionario con los resultados de la evaluación de completitud.
            resultados["completitud"]: Porcentaje de datos no nulos.
            resultados["valores_cero"]: Porcentaje de valores cero (solo para variables numéricas).
            resultados["valores_negativos"]: Porcentaje de valores negativos.
            resultados["inconsistentes_con_estado"]: Número de registros inconsistentes con 
            estado_credito (solo para tot_dias_mora y tot_num_moras).
            resultados["pct_inconsistentes"]: Porcentaje de registros inconsistentes con 
            estado_credito (solo para tot_dias_mora y tot_num_moras).
        """
        data = self.df[col]

        resultados: dict = {
            "completitud": 1 - as_float((data.is_null().mean())) * 100,
            "valores_cero": as_float((data == 0).mean()) * 100
            if data.dtype.is_numeric()
            else 0,
            "valores_negativos": as_float((data < 0).mean()) * 100
            if data.dtype.is_numeric()
            else 0,
        }

        if col in ["tot_dias_mora", "tot_num_moras"]:
            if "estado_credito" in self.df.columns:
                inconsistentes = self.df.filter(
                    (pl.col(col) > 0) & (pl.col("estado_credito").is_in(["A", "V"]))
                )
                resultados["inconsistentes_con_estado"] = len(inconsistentes)
                resultados["pct_inconsistentes"] = as_float(
                    len(inconsistentes) / len(self.df) * 100
                )

        return resultados

    def recomendar_variable(self, col: str, analisis: dict) -> tuple[str, str]:
        """
        Genera recomendación basada en todo el análisis,
        con los datos de correlación, completitud y distribución se determina si la variable
        es recomendable para incluir en el modelo.

        Args:
            self: Instancia de la clase EVAriguroso.
            col (str): Nombre de la columna a recomendar.
            analisis (dict): Diccionario con los resultados del análisis previo de la variable.

        Returns:
            tuple[str, str]: Recomendación y motivo.
            Los valores posibles para la recomendación son:
                - "MANTENER": La variable es identificadora o temporal necesaria.
                - "EVALUAR": No hay análisis previo, se requiere evaluación manual.
                - "✅ INCLUIR": La variable es recomendable para incluir en el modelo.
                - "❌ EXCLUIR": La variable no es recomendable para incluir en el modelo.
                - "⚠️ EVALUAR (conflicto)": Hay criterios de inclusión y exclusión conflictivos, 
                se requiere evaluación manual.
                - "⚠️ EXCLUIR (evidencia fuerte)": Hay evidencia fuerte para excluir la variable, 
                pero también hay criterios de inclusión.
                - "🔍 EVALUAR MANUALMENTE": No hay criterios automáticos concluyentes, 
                se requiere evaluación manual.

        """
        if col in [self.target_col, "numero_credito", "fecha_credito"]:
            return "MANTENER", "Variable identificadora o temporal necesaria"

        if not analisis:
            return "EVALUAR", "Sin análisis previo"

        motivos_inclusion: list[str] = []
        motivos_exclusion: list[str] = []

        if analisis.get("tipo") == "numerica" and "correlacion" in analisis:
            corr_data = analisis["correlacion"]

            if corr_data.get("pearson_significativo", False):
                pearson_r = corr_data.get("pearson_r", 0)
                motivos_inclusion.append(
                    f"Correlación Pearson significativa (r={pearson_r:.4f})"
                )

            if corr_data.get("mutual_information", 0) > 0.05:
                mi = corr_data["mutual_information"]
                motivos_inclusion.append(f"Información mutua relevante (MI={mi:.4f})")

            if corr_data.get("poder_discriminativo") in [
                "ALTO",
                "MODERADO",
            ]:
                auc = corr_data.get("auc_roc_individual", 0.5)
                motivos_inclusion.append(
                    f"Poder discriminativo {corr_data['poder_discriminativo']} (AUC={auc:.4f})"
                )

            if (
                corr_data.get("pearson_r", 0) is not None
                and abs(corr_data.get("pearson_r", 0)) < 0.01
            ):
                motivos_exclusion.append(
                    f"Correlación casi nula con target (r={corr_data['pearson_r']:.4f})"
                )

            if "error" in corr_data:
                motivos_exclusion.append(f"Error en correlación: {corr_data['error']}")

        if analisis.get("completitud"):
            completitud_data = analisis["completitud"]
            if completitud_data.get("completitud", 0) > 90:
                motivos_inclusion.append(
                    f"Alta completitud ({completitud_data['completitud']:.1f}%)"
                )
            if completitud_data.get("completitud", 100) < 50:
                motivos_exclusion.append(
                    f"Baja completitud ({completitud_data['completitud']:.1f}%)"
                )

        if analisis.get("tipo") == "numerica" and analisis.get("distribucion"):
            dist_data = analisis["distribucion"]
            if dist_data.get("pct_outliers", 0) > 20:
                motivos_exclusion.append(
                    f"Alto porcentaje de outliers ({dist_data['pct_outliers']:.1f}%)"
                )

        if col in [
            "tot_dias_mora",
            "tot_num_moras",
            "tot_dias_mora_promedio",
            "tot_num_moras_promedio",
        ]:
            motivos_exclusion.append(
                "CAMPO CON CÁLCULOS INCOMPLETOS (evidencia empírica)"
            )
            if analisis.get("completitud", {}).get("pct_inconsistentes", 0) > 5:
                motivos_exclusion.append(
                    f"{analisis['completitud']['pct_inconsistentes']:.1f}% "
                    f"registros inconsistentes con estado del crédito"
                )

        if motivos_exclusion and not motivos_inclusion:
            return "❌ EXCLUIR", "; ".join(motivos_exclusion)
        elif motivos_inclusion and not motivos_exclusion:
            return "✅ INCLUIR", "; ".join(motivos_inclusion)
        elif motivos_exclusion and motivos_inclusion:
            if any("INCOMPLETOS" in m for m in motivos_exclusion):
                return "⚠️ EXCLUIR (evidencia fuerte)", "; ".join(
                    motivos_exclusion + motivos_inclusion
                )
            return "⚠️ EVALUAR (conflicto)", (
                f"INCLUSIÓN: {'; '.join(motivos_inclusion)} | "
                f"EXCLUSIÓN: {'; '.join(motivos_exclusion)}"
            )
        else:
            return (
                "🔍 EVALUAR MANUALMENTE",
                "Sin criterios automáticos concluyentes",
            )
