##
## @file pipeline.py
##
## Orquestador del EVA. Contiene toda la lógica de orquestación:
##   - Loop de variables para analizar distribución, correlación y completitud
##   - Generación del dashboard 3×3
##   - Logging a consola
##   - Switch de salida: notebook vs MLflow 3.x
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
import logging
import os
import tempfile
import sys
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns
import mlflow

from typing import Any
from pathlib import Path
from datetime import datetime

## El paquete eva se puede ejecutar como script independiente o como módulo.
## Toco codificar esta lógica para que funcione en ambos casos, Notebook y MLflow.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from eva.analisis_riguroso import AnalisisRiguroso
    from eva.utilidades import (
        get_columnas_numericas,
        get_columnas_string,
        titulo,
        subtitulo,
        informar_razon,
    )
else:
    from .analisis_riguroso import AnalisisRiguroso
    from .utilidades import (
        get_columnas_numericas,
        get_columnas_string,
        titulo,
        subtitulo,
        informar_razon,
    )

logger = logging.getLogger(__name__)

logging.addLevelName(logging.DEBUG, "DEBUG")
logging.addLevelName(logging.INFO, "INFO ")
logging.addLevelName(logging.WARNING, "WARN ")
logging.addLevelName(logging.ERROR, "ERROR")  # Incluye un espacio al final
logging.addLevelName(logging.CRITICAL, "SEVER")

class Pipeline:
    """Clase para ejecutar el analisis riguroso y generar el dashboard de EVA.

    La clase permite escribir log para notebook o entradas a MLflow 3.x, y generar un
    dashboard 3x3 con las métricas más importantes.
    """

    ## Hay columnas que siempre se excluyen del análisis, en mi caso son:
    COLS_EXCLUIR_BASE = [
        "numero_credito",
        "ordencal",
        "codigo",
    ]

    def __init__(
        self,
        modo: str = "notebook",
        mlflow_tracking_uri: str = "http://localhost:5000",
        mlflow_experiment_name: str = "eva_crediticio",
        output_dir: str = "resultados",
    ):
        """Constructor de la clase Pipeline.

        Inicializa el modo de ejecución y configura MLflow si es necesario.

        Args:
            modo: Modo de ejecución, puede ser "notebook" o "mlflow", por defecto "notebook".
            mlflow_tracking_uri: URI de tracking de MLflow, requerido si modo es "mlflow", por defecto "http://localhost:5000".
            mlflow_experiment_name: Nombre del experimento de MLflow, requerido si modo es "mlflow", por defecto "eva_crediticio".
            output_dir: Directorio donde se guardarán los resultados del análisis, por defecto "resultados".
        """
        if modo not in ("notebook", "mlflow"):
            raise ValueError(f"modo debe ser 'notebook' o 'mlflow', no '{modo}'")
        self.modo = modo
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.mlflow_experiment_name = mlflow_experiment_name
        self.output_dir = output_dir

        if self.modo == "mlflow":
            if mlflow_tracking_uri is None:
                raise ValueError("mlflow_tracking_uri es requerido en modo 'mlflow'")
            self._init_mlflow()

        if self.modo == "notebook":
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir, exist_ok=True)
                logger.info("Directorio de salida creado: %s", self.output_dir)

    def _init_mlflow(self):
        """Inicializa la configuración de MLflow para el seguimiento de experimentos.

        Configura la URI de tracking y el experimento de MLflow. Si el experimento no existe, lo crea.

        Raises:
            Exception: Si ocurre un error al configurar MLflow.
        """

        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        try:
            mlflow.set_experiment(self.mlflow_experiment_name)
        except Exception:
            mlflow.create_experiment(self.mlflow_experiment_name)
            mlflow.set_experiment(self.mlflow_experiment_name)
        logger.info(
            "MLflow configurado — tracking: %s, experimento: %s",
            self.mlflow_tracking_uri,
            self.mlflow_experiment_name,
        )

    def run(
        self,
        df: pl.DataFrame,
        target_col: str = "crisis_flag",
    ) -> tuple[list[dict], dict]:
        """
        Ejecuta el pipeline completo de EVA.

        Args:
            self: Instancia de la clase Pipeline.
            df: DataFrame de entrada con todas las variables.
            target_col: nombre de la columna objetivo (target) para correlación y análisis.

        Returns:
            recomendaciones : list[dict]
            evidencias : dict  (incluye 'vif' si se calculó)
        """
        subtitulo(logger, "EVA — ANÁLISIS EXPLORATORIO DE VARIABLES")
        
        logger.info("📅 (%s)", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logger.info("📊 Modo: (%s)", self.modo)
        logger.info("📊 Registros: (%s)", len(df))
        
        eva = AnalisisRiguroso(df, target_col=target_col)

        # 1. Loop de variables
        reporte_numericas = self._analizar_variables_numericas(eva)
        reporte_categoricas = self._analizar_variables_categoricas(eva)
        reporte_completo = reporte_numericas + reporte_categoricas

        # 2. VIF
        evidencias = self._analizar_vif(eva)

        # 3. Recomendaciones
        recomendaciones = self._generar_recomendaciones(eva, reporte_completo)

        # 4. Dashboard
        fig = self._plot_dashboard(df, target_col, evidencias, recomendaciones)

        # 5. Despachar
        if self.modo == "notebook":
            self._salida_notebook(recomendaciones, fig)
        else:
            self._salida_mlflow(df, target_col, recomendaciones, evidencias, fig)

        plt.close(fig)

        return recomendaciones, evidencias

    def _analizar_variables_numericas(self, eva: AnalisisRiguroso) -> list[dict]:
        """Itera sobre todas las columnas y construye el reporte.

        Ejecuta los analiasis para cada variable numérica, incluyendo distribución, correlación y completitud.

        Args:
            eva: Instancia de AnalisisRiguroso con el DataFrame y la columna objetivo.
        """
        reporte: list[dict] = []
        cols_numeric = get_columnas_numericas(eva.df)
        excluir = self.COLS_EXCLUIR_BASE + [eva.target_col]

        # -- Numéricas --
        titulo(logger, "ANÁLISIS DE VARIABLES NUMÉRICAS (%d)" % len(cols_numeric))

        for col in cols_numeric:
            if col in excluir:
                continue
            subtitulo(logger, "📊 ANALIZANDO: %s" % col)

            analisis_var: dict = {"variable": col, "tipo": "numerica"}

            # Distribución
            logger.info("  📊 Distribución:")
            dist = eva.analizar_distribucion(col)
            analisis_var["distribucion"] = dist
            if "error" not in dist:
                logger.info(
                    "     Media=%.2f  Mediana=%.2f  Std=%.2f",
                    dist["mean"],
                    dist["median"],
                    dist["std"],
                )
                logger.info(
                    "     Skewness=%.2f  Kurtosis=%.2f  Outliers=%.1f%%  Nulos=%.1f%%",
                    dist["skew"],
                    dist["kurtosis"],
                    dist["pct_outliers"],
                    dist["pct_nulos"],
                )
                if dist.get("es_normal") is not None:
                    logger.info(
                        "     ¿Distribución normal? %s",
                        "SÍ" if dist["es_normal"] else "NO",
                    )

            # Correlación
            logger.info("  🔗 Correlación con %s:", eva.target_col)
            corr = eva.analizar_correlacion(col)
            analisis_var["correlacion"] = corr
            if "error" not in corr:
                if "pearson_r" in corr:
                    logger.info(
                        "     Pearson r=%.4f (p=%.4f) %s",
                        corr["pearson_r"],
                        corr.get("pearson_pvalue", 1),
                        "✅" if corr.get("pearson_significativo") else "❌",
                    )
                if "spearman_r" in corr:
                    logger.info(
                        "     Spearman ρ=%.4f (p=%.4f) %s",
                        corr["spearman_r"],
                        corr.get("spearman_pvalue", 1),
                        "✅" if corr.get("spearman_significativo") else "❌",
                    )
                if "mutual_information" in corr:
                    logger.info(
                        "     Información Mutua=%.4f", corr["mutual_information"]
                    )
                if "auc_roc_individual" in corr:
                    logger.info(
                        "     AUC-ROC individual=%.4f (%s)",
                        corr["auc_roc_individual"],
                        corr.get("poder_discriminativo", "N/A"),
                    )
                if "cohens_d" in corr:
                    logger.info(
                        "     Cohen's d=%.4f (Δmedias=%.2f)",
                        corr["cohens_d"],
                        corr.get("diferencia_medias", 0),
                    )
            else:
                logger.info("     ⚠️ %s", corr["error"])

            # Completitud
            logger.info("  ✅ Calidad del dato:")
            calidad = eva.evaluar_completitud(col)
            analisis_var["completitud"] = calidad
            logger.info("     Completitud=%.1f%%", calidad["completitud"])
            if "pct_inconsistentes" in calidad:
                logger.info(
                    "     ⚠️ Inconsistencias con estado: %.1f%%",
                    calidad["pct_inconsistentes"],
                )

            reporte.append(analisis_var)

        return reporte

    def _analizar_variables_categoricas(self, eva: AnalisisRiguroso) -> list[dict]:
        """Itera sobre todas las columnas y construye el reporte.

        Ejecuta los analiasis para cada variable categórica, incluyendo distribución, correlación y completitud.

        Args:
            eva: Instancia de AnalisisRiguroso con el DataFrame y la columna objetivo.
        """
        reporte: list[dict] = []
        cols_categoric = get_columnas_string(eva.df)
        excluir = self.COLS_EXCLUIR_BASE + [eva.target_col]

        # -- Categóricas --
        titulo(logger, "ANÁLISIS DE VARIABLES CATEGÓRICAS (%d)" % len(cols_categoric))

        for col in cols_categoric:
            if col in excluir:
                continue

            subtitulo(logging, "📊 ANALIZANDO: %s" % col)

            analisis_var: dict[str, Any] = {"variable": col, "tipo": "categorica"}

            cat = eva.analizar_variable_categorica(col)
            analisis_var["categorico"] = cat

            logger.info("     Categorías únicas: %d", cat["num_categorias"])
            logger.info(
                "     Categoría dominante: %s (%.1f%%)",
                cat.get("categoria_dominante", "N/A"),
                cat["pct_categoria_dominante"],
            )
            logger.info(
                "     Chi-cuadrado significativo: %s",
                "SÍ" if cat.get("chi2_significativo") else "NO",
            )
            if "cramers_v" in cat:
                logger.info("     V de Cramer: %.4f", cat["cramers_v"])

            calidad = eva.evaluar_completitud(col)
            analisis_var["completitud"] = calidad
            logger.info("     Completitud=%.1f%%", calidad["completitud"])

            reporte.append(analisis_var)

        return reporte

    def _analizar_vif(self, eva: AnalisisRiguroso) -> dict:
        """Calcula VIF y retorna evidencias.

        Args:
            eva: Instancia de AnalisisRiguroso con el DataFrame y la columna objetivo.

        Returns:
            evidencias: dict con el DataFrame de VIF si se calculó.

        """
        evidencias: dict = {}

        titulo(logger, "ANÁLISIS DE MULTICOLINEALIDAD (VIF)")

        try:
            numeric_for_vif = eva.df.select(get_columnas_numericas(eva.df)).fill_null(0)
            if len(numeric_for_vif.columns) > 1:
                vif_df = eva.calcular_vif(numeric_for_vif, col_excluir=eva.target_col)
                high_vif = vif_df.filter(pl.col("VIF") > 10).sort(
                    "VIF", descending=True
                )
                logger.info(
                    "Variables con VIF > 10 (alta multicolinealidad): %d",
                    len(high_vif),
                )
                for row in high_vif.iter_rows(named=True):
                    logger.warning("  ⚠️ %s: VIF=%.2f", row["variable"], row["VIF"])
                evidencias["vif"] = vif_df.to_dict()
            else:
                logger.warning("⚠️ No hay suficientes variables numéricas para VIF")
        except Exception as e:
            logger.warning("⚠️ Error en VIF: %s", e)

        return evidencias

    def _generar_recomendaciones(
        self, eva: AnalisisRiguroso, reporte: list[dict]
    ) -> list[dict]:
        """Genera recomendaciones a partir del reporte de análisis.

        Args:
            eva: Instancia de AnalisisRiguroso con el DataFrame y la columna objetivo.
            reporte: Lista de diccionarios con el análisis de cada variable.

        """
        recomendaciones: list[dict] = []

        titulo(logger, "RECOMENDACIONES FINALES")

        for analisis in reporte:
            col = analisis["variable"]
            recomendacion, razon = eva.recomendar_variable(col, analisis)

            recomendaciones.append(
                {
                    "variable": col,
                    "tipo": analisis["tipo"],
                    "recomendacion": recomendacion,
                    "razon": razon,
                }
            )

            logger.info("")
            if "INCLUIR" in recomendacion:
                logger.info("✅ %s: %s", col, recomendacion)
            elif "EXCLUIR" in recomendacion:
                logger.error("❌ %s: %s", col, recomendacion)
            else:
                logger.warning("⚠️ %s: %s", col, recomendacion)
            informar_razon(logger, razon)

        # Resumen
        resumen = pl.DataFrame(recomendaciones)

        titulo(logger, "RESUMEN DE RECOMENDACIONES")
        for row in resumen["recomendacion"].value_counts().iter_rows(named=True):
            logger.info("   %s: %s", row["recomendacion"], row["count"])

        # Variables problemáticas
        subtitulo(logger, "🔍 VERIFICACIÓN DE VARIABLES PROBLEMÁTICAS")
        for var in [
            "tot_dias_mora",
            "tot_num_moras",
            "tot_dias_mora_promedio",
            "tot_num_moras_promedio",
        ]:
            rec = next((r for r in recomendaciones if r["variable"] == var), None)
            if rec:
                logger.info("")
                logger.info("   %s: %s", var, rec["recomendacion"])
                informar_razon(logger, ("   Razón: %s" % rec["razon"]))

        return recomendaciones

    def _plot_dashboard(
        self,
        df: pl.DataFrame,
        target_col: str,
        evidencias: dict,
        recomendaciones: list[dict],
    ):
        """Genera el dashboard 3×3 del EVA. Retorna la Figure.
        
        Además de las gráficas, se incluyen los resultados de VIF y las recomendaciones finales.
        
        Args:
            df: DataFrame de entrada con todas las variables.
            target_col: nombre de la columna objetivo (target) para correlación y análisis.
            evidencias: dict con evidencias del análisis, incluyendo 'vif' si se calculó.
            recomendaciones: lista de diccionarios con las recomendaciones finales.        
        """
        
        titulo(logger, "GENERANDO DASHBOARD 3×3 DEL EVA")
        
        fig = plt.figure(figsize=(20, 15))
        numeric_cols = get_columnas_numericas(df)[:20]

        # 1. Heatmap de correlaciones
        ax1 = plt.subplot(3, 3, 1)
        if len(numeric_cols) > 1:
            corr_matrix = np.corrcoef(df.select(numeric_cols).to_numpy(), rowvar=False)
            sns.heatmap(
                corr_matrix,
                ax=ax1,
                cmap="RdBu_r",
                center=0,
                xticklabels=False,
                yticklabels=False,
            )
            ax1.set_title("Matriz de Correlación (primeras 20 vars)")
        else:
            ax1.text(
                0.5,
                0.5,
                "No hay suficientes variables numéricas",
                ha="center",
                va="center",
                transform=ax1.transAxes,
            )
            ax1.set_title("Matriz de Correlación - No disponible")

        # 2. Top correlaciones con target
        ax2 = plt.subplot(3, 3, 2)
        if len(numeric_cols) > 2 and target_col in df.columns:
            try:
                corr_target = df.select(
                    [
                        pl.col(c).corr(pl.col(target_col)).abs().alias(c)
                        for c in numeric_cols
                    ]
                ).row(0, named=True)
                corr_target = {k: v for k, v in corr_target.items() if v is not None}
                if target_col in corr_target:
                    del corr_target[target_col]
                corr_target = dict(
                    sorted(corr_target.items(), key=lambda x: x[1], reverse=True)[:15]
                )
                if corr_target:
                    colors = [
                        "green"
                        if df.select(pl.col(c).corr(pl.col(target_col))).item() > 0
                        else "red"
                        for c in corr_target
                    ]
                    ax2.barh(
                        list(corr_target.keys()),
                        list(corr_target.values()),
                        color=colors,
                    )
                    ax2.set_title("Top 15 Correlaciones (absolutas) con Target")
                    ax2.set_xlabel("|Correlación|")
                    ax2.invert_yaxis()
                else:
                    ax2.text(
                        0.5,
                        0.5,
                        "Sin correlaciones disponibles",
                        ha="center",
                        va="center",
                        transform=ax2.transAxes,
                    )
            except Exception:
                ax2.text(
                    0.5,
                    0.5,
                    "Error al calcular correlaciones",
                    ha="center",
                    va="center",
                    transform=ax2.transAxes,
                )
        else:
            ax2.text(
                0.5,
                0.5,
                "No hay suficientes datos",
                ha="center",
                va="center",
                transform=ax2.transAxes,
            )
            ax2.set_title("Top 15 Correlaciones - No disponible")

        # 3. Missing values
        ax3 = plt.subplot(3, 3, 3)
        missing_pct = {c: (df[c].is_null().sum() / len(df)) * 100 for c in df.columns}
        missing_pct = {k: v for k, v in missing_pct.items() if v > 0}
        missing_pct = dict(
            sorted(missing_pct.items(), key=lambda x: x[1], reverse=True)
        )
        if missing_pct:
            top_keys = list(missing_pct.keys())[: min(15, len(missing_pct))]
            top_vals = [missing_pct[k] for k in top_keys]
            ax3.barh(top_keys, top_vals, color="coral")
            ax3.set_title("Top 15 Variables con Mayor % de Nulos")
            ax3.set_xlabel("% Nulos")
        else:
            ax3.text(
                0.5,
                0.5,
                "No hay valores nulos en los datos",
                ha="center",
                va="center",
                transform=ax3.transAxes,
                fontsize=12,
            )
            ax3.set_title("% de Nulos - Sin datos nulos")

        # 4. Distribución del target
        ax4 = plt.subplot(3, 3, 4)
        if target_col in df.columns:
            value_counts = df[target_col].value_counts()
            if len(value_counts) > 0:
                ax4.bar(
                    value_counts[target_col].to_list(),
                    value_counts["count"].to_list(),
                    color=["#2ecc71", "#e74c3c"],
                )
                ax4.set_title("Distribución de Crisis Flag")
                ax4.set_xlabel("Crisis Flag")
                ax4.set_ylabel("Frecuencia")
                for i, v in enumerate(value_counts["count"].to_list()):
                    ax4.text(i, v + 50, f"{v:,}", ha="center")
            else:
                ax4.text(
                    0.5,
                    0.5,
                    "Sin datos del target",
                    ha="center",
                    va="center",
                    transform=ax4.transAxes,
                )
        else:
            ax4.text(
                0.5,
                0.5,
                "Target no disponible",
                ha="center",
                va="center",
                transform=ax4.transAxes,
            )
            ax4.set_title("Distribución de Crisis Flag - No disponible")

        # 5. tot_dias_mora vs target
        ax5 = plt.subplot(3, 3, 5)
        if "tot_dias_mora" in df.columns and target_col in df.columns:
            try:
                data_plot = df.select(["tot_dias_mora", target_col]).drop_nulls()
                if len(data_plot) > 0:
                    for grp_val, grp_data in data_plot.group_by(pl.col(target_col)):
                        ax5.boxplot(
                            grp_data["tot_dias_mora"].to_numpy(), positions=[grp_val]
                        )
                    ax5.set_title(
                        "tot_dias_mora por Crisis Flag\n(A EVALUAR: posible exclusión)"
                    )
                    ax5.set_xlabel("Crisis Flag")
                    ax5.set_ylabel("tot_dias_mora")
                else:
                    ax5.text(
                        0.5,
                        0.5,
                        "Sin datos suficientes",
                        ha="center",
                        va="center",
                        transform=ax5.transAxes,
                    )
            except Exception:
                ax5.text(
                    0.5,
                    0.5,
                    "Error al graficar",
                    ha="center",
                    va="center",
                    transform=ax5.transAxes,
                )
        else:
            ax5.text(
                0.5,
                0.5,
                "Variable no disponible",
                ha="center",
                va="center",
                transform=ax5.transAxes,
            )
            ax5.set_title("tot_dias_mora - No disponible")

        # 6. tot_num_moras vs target
        ax6 = plt.subplot(3, 3, 6)
        if "tot_num_moras" in df.columns and target_col in df.columns:
            try:
                data_plot = df.select(["tot_num_moras", target_col]).drop_nulls()
                if len(data_plot) > 0:
                    for grp_val, grp_data in data_plot.group_by(pl.col(target_col)):
                        ax6.boxplot(
                            grp_data["tot_num_moras"].to_numpy(),
                            positions=[grp_val],
                            patch_artist=True,
                            boxprops=dict(facecolor="lightblue"),
                            medianprops=dict(color="red", linewidth=2),
                        )
                    ax6.set_title(
                        "tot_num_moras por Crisis Flag\n(A EVALUAR: posible exclusión)"
                    )
                    ax6.set_xlabel("Crisis Flag")
                    ax6.set_ylabel("tot_num_moras")
                    stats_text = (
                        f"Media no crisis: {data_plot.filter(pl.col(target_col) == 0)['tot_num_moras'].mean():.2f}\n"
                        f"Media crisis: {data_plot.filter(pl.col(target_col) == 1)['tot_num_moras'].mean():.2f}"
                    )
                    ax6.text(
                        0.5,
                        -0.15,
                        stats_text,
                        transform=ax6.transAxes,
                        fontsize=9,
                        verticalalignment="top",
                        horizontalalignment="center",
                        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                    )
                else:
                    ax6.text(
                        0.5,
                        0.5,
                        "Sin datos suficientes",
                        ha="center",
                        va="center",
                        transform=ax6.transAxes,
                    )
            except Exception:
                ax6.text(
                    0.5,
                    0.5,
                    "Error al graficar",
                    ha="center",
                    va="center",
                    transform=ax6.transAxes,
                )
        else:
            ax6.text(
                0.5,
                0.5,
                "Variable no disponible",
                ha="center",
                va="center",
                transform=ax6.transAxes,
            )
            ax6.set_title("tot_num_moras - No disponible")

        # 7. Distribución temporal de crisis
        ax7 = plt.subplot(3, 3, 7)
        if "mes" in df.columns and target_col in df.columns:
            try:
                crisis_temp = (
                    df.group_by(df["mes"].alias("periodo"))
                    .agg(
                        [
                            pl.col(target_col).mean().alias("mean"),
                            pl.col(target_col).count().alias("count"),
                        ]
                    )
                    .sort("periodo")
                )
                if len(crisis_temp) > 0:
                    ax7.plot(
                        crisis_temp["periodo"].cast(pl.String).to_list(),
                        crisis_temp["mean"].to_list(),
                        color="darkred",
                        marker="o",
                        markersize=3,
                        linewidth=1,
                    )
                    ax7.set_title("Tasa de Crisis a lo Largo del Tiempo")
                    ax7.set_xlabel("Mes")
                    ax7.set_ylabel("Tasa de Crisis")
                    media = crisis_temp["mean"].to_numpy().mean()
                    ax7.axhline(
                        y=media,
                        color="blue",
                        linestyle="--",
                        alpha=0.7,
                        label=f"Media: {media:.3f}",
                    )
                    ax7.legend()
                    ax7.tick_params(axis="x", rotation=45)
                    for i, label in enumerate(ax7.get_xticklabels()):
                        if i % 12 != 0:
                            label.set_visible(False)
                else:
                    ax7.text(
                        0.5,
                        0.5,
                        "Sin datos temporales",
                        ha="center",
                        va="center",
                        transform=ax7.transAxes,
                    )
            except Exception:
                ax7.text(
                    0.5,
                    0.5,
                    "Error al graficar serie temporal",
                    ha="center",
                    va="center",
                    transform=ax7.transAxes,
                )
        else:
            ax7.text(
                0.5,
                0.5,
                "Variable temporal no disponible",
                ha="center",
                va="center",
                transform=ax7.transAxes,
            )
            ax7.set_title("Tasa de Crisis Temporal - No disponible")

        # 8. VIF Analysis
        ax8 = plt.subplot(3, 3, 8)
        if "vif" in evidencias and len(evidencias["vif"]) > 0:
            try:
                vif_data = pl.DataFrame(evidencias["vif"])
                vif_top = vif_data.sort("VIF", descending=True).head(10)
                if len(vif_top) > 0:
                    colors = [
                        "red" if v > 10 else "orange" if v > 5 else "green"
                        for v in vif_top["VIF"]
                    ]
                    ax8.barh(range(len(vif_top)), vif_top["VIF"], color=colors)
                    ax8.set_yticks(range(len(vif_top)))
                    ax8.set_yticklabels(vif_top["variable"].to_list(), fontsize=8)
                    ax8.set_title("Top 10 VIF (Multicolinealidad)")
                    ax8.set_xlabel("VIF")
                    ax8.axvline(
                        x=10, color="red", linestyle="--", alpha=0.7, label="VIF=10"
                    )
                    ax8.axvline(
                        x=5, color="orange", linestyle="--", alpha=0.7, label="VIF=5"
                    )
                    ax8.legend(fontsize=8)
                    for i, row in enumerate(vif_top.iter_rows(named=True)):
                        ax8.text(
                            row["VIF"] + 0.5,
                            i,
                            f"{row['VIF']:.1f}",
                            va="center",
                            fontsize=8,
                        )
                else:
                    ax8.text(
                        0.5,
                        0.5,
                        "Sin datos VIF",
                        ha="center",
                        va="center",
                        transform=ax8.transAxes,
                    )
            except Exception:
                ax8.text(
                    0.5,
                    0.5,
                    "Error al procesar VIF",
                    ha="center",
                    va="center",
                    transform=ax8.transAxes,
                )
        else:
            ax8.text(
                0.5,
                0.5,
                "VIF no disponible",
                ha="center",
                va="center",
                transform=ax8.transAxes,
            )
            ax8.set_title("VIF Analysis - No disponible")

        # 9. Resumen de recomendaciones
        ax9 = plt.subplot(3, 3, 9)
        if recomendaciones:
            df_rec = pl.DataFrame(recomendaciones)
            if len(df_rec) > 0:
                decision_counts = df_rec["recomendacion"].value_counts()
                color_map = {
                    "✅ INCLUIR": "#2ecc71",
                    "❌ EXCLUIR": "#e74c3c",
                    "MANTENER": "#3498db",
                    "⚠️ EXCLUIR": "#e67e22",
                    "⚠️ EVALUAR (conflicto)": "#f39c12",
                    "🔍 EVALUAR MANUALMENTE": "#95a5a6",
                    "⚠️ EVALUAR": "#f1c40f",
                }
                colors = [
                    color_map.get(idx, "#95a5a6")
                    for idx in decision_counts["recomendacion"].to_list()
                ]
                if len(decision_counts) > 0:
                    ax9.pie(
                        decision_counts["count"].to_list(),
                        labels=decision_counts["recomendacion"].to_list(),
                        colors=colors,
                        autopct="%1.1f%%",
                        startangle=90,
                        textprops={"fontsize": 8},
                    )
                    ax9.set_title("Resumen de Recomendaciones EVA")
                    ax9.text(
                        0,
                        -1.3,
                        f"Total variables analizadas: {len(df_rec)}",
                        ha="center",
                        va="center",
                        fontsize=10,
                        fontweight="bold",
                        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
                    )
                else:
                    ax9.text(
                        0.5,
                        0.5,
                        "Sin decisiones",
                        ha="center",
                        va="center",
                        transform=ax9.transAxes,
                    )
            else:
                ax9.text(
                    0.5,
                    0.5,
                    "Sin recomendaciones",
                    ha="center",
                    va="center",
                    transform=ax9.transAxes,
                )
        else:
            ax9.text(
                0.5,
                0.5,
                "Sin recomendaciones aún",
                ha="center",
                va="center",
                transform=ax9.transAxes,
            )
            ax9.set_title("Recomendaciones - Pendiente")

        plt.suptitle(
            "EVA - Análisis Exploratorio de Variables\nRiesgo Crediticio Multi-Horizonte",
            fontsize=14,
            fontweight="bold",
            y=1.02,
        )
        plt.tight_layout()
        return fig

    # ------------------------------------------------------------------
    # 5a. Salida modo notebook
    # ------------------------------------------------------------------

    def _salida_notebook(
        self,
        recomendaciones: list[dict],
        fig,
    ):
        """plt.show() + guarda .png y .csv en disco."""
        os.makedirs(f"{self.output_dir}/graficas", exist_ok=True)
        os.makedirs(f"{self.output_dir}/metricas", exist_ok=True)

        plt.show()

        png_path = f"{self.output_dir}/graficas/eda_completo.png"
        fig.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="white")
        logger.info("📊 Dashboard guardado en: %s", png_path)

        csv_path = f"{self.output_dir}/metricas/recomendaciones_eva.csv"
        pl.DataFrame(recomendaciones).write_csv(csv_path)
        logger.info(
            "📋 Recomendaciones guardadas (%d vars) en: %s",
            len(recomendaciones),
            csv_path,
        )

        logger.info("✅ EVA COMPLETADO (modo notebook)")

    def _salida_mlflow(
        self,
        df: pl.DataFrame,
        target_col: str,
        recomendaciones: list[dict],
        evidencias: dict,
        fig,
    ):
        """Envía métricas, figura y artefactos a MLflow 3.x."""
        import json

        import mlflow

        run_name = f"eva_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        with mlflow.start_run(run_name=run_name) as run:
            run_id = run.info.run_id
            logger.info("MLflow Run ID: %s", run_id)

            # Parámetros
            mlflow.log_params(
                {
                    "modo": self.modo,
                    "total_registros": len(df),
                    "total_variables": len(recomendaciones),
                    "target_col": target_col,
                }
            )

            # Métricas de recomendaciones
            resumen = pl.DataFrame(recomendaciones)
            counts = resumen["recomendacion"].value_counts()
            for row in counts.iter_rows(named=True):
                key = row["recomendacion"].strip("✅❌⚠️🔍 ").replace(" ", "_")
                mlflow.log_metric(f"eva_{key}", row["count"])

            vars_incluir = [
                r["variable"]
                for r in recomendaciones
                if "INCLUIR" in r["recomendacion"]
            ]
            vars_excluir = [
                r["variable"]
                for r in recomendaciones
                if "EXCLUIR" in r["recomendacion"]
            ]
            mlflow.log_metric("eva_vars_incluir", len(vars_incluir))
            mlflow.log_metric("eva_vars_excluir", len(vars_excluir))

            # Métricas VIF
            if "vif" in evidencias:
                vif_data = pl.DataFrame(evidencias["vif"])
                high_vif = vif_data.filter(pl.col("VIF") > 10)
                mlflow.log_metric("eva_vif_gt_10", len(high_vif))
                if len(vif_data) > 0:
                    mlflow.log_metric("eva_vif_max", vif_data["VIF"].max())
                    mlflow.log_metric("eva_vif_mean", vif_data["VIF"].mean())

            # Figura
            mlflow.log_figure(fig, "eva_dashboard.png")
            logger.info("📊 Dashboard enviado a MLflow")

            # Artefactos
            with tempfile.TemporaryDirectory() as tmpdir:
                csv_path = os.path.join(tmpdir, "recomendaciones_eva.csv")
                pl.DataFrame(recomendaciones).write_csv(csv_path)
                mlflow.log_artifact(csv_path, "artifacts")

                reporte_path = os.path.join(tmpdir, "reporte_eva.json")
                with open(reporte_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "recomendaciones": recomendaciones,
                            "evidencias": evidencias,
                            "vars_incluir": vars_incluir,
                            "vars_excluir": vars_excluir,
                        },
                        f,
                        indent=2,
                        ensure_ascii=False,
                        default=str,
                    )
                mlflow.log_artifact(reporte_path, "artifacts")
                logger.info("📋 Artefactos (CSV + JSON) enviados a MLflow")

            logger.info("✅ EVA COMPLETADO (modo MLflow) — Run: %s", run_id)
