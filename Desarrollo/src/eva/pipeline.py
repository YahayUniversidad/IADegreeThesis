##
## @file pipeline.py
##
## Orquestador del EVA. Contiene toda la lógica de orquestación:
##   - Loop de variables para analizar distribución, correlación y completitud
##   - Generación del dashboard 5×2
##   - Logging a consola
##   - Switch de salida: notebook vs MLflow 3.x
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
import json
import os
import re
import sys
import tempfile
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import mlflow
import polars as pl

## El paquete eva se puede ejecutar como script independiente o como módulo.
## Toco codificar esta lógica para que funcione en ambos casos, Notebook y MLflow.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from eva.analisis_riguroso import AnalisisRiguroso
    from eva.dashboard import build_dashboard
    from eva.utilidades import (
        get_columnas_numericas,
        get_columnas_string,
    )
else:
    from .analisis_riguroso import AnalisisRiguroso
    from .dashboard import build_dashboard
    from .utilidades import (
        get_columnas_numericas,
        get_columnas_string,
    )


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
        mlflow_experiment_name: str,
        output_dir: str,
        mlflow_tracking_uri: str = "http://localhost:5000",
    ):
        """Constructor de la clase Pipeline.

        Inicializa la ejecución y configura MLflow si es necesario.

        Args:
            mlflow_tracking_uri:
                URI de tracking de MLflow, requerido si se desea usar MLflow, por defecto "http://localhost:5000".
            mlflow_experiment_name:
                Nombre del experimento de MLflow, requerido si se desea usar MLflow.
            output_dir:
                Directorio donde se guardarán los resultados del análisis, por defecto "resultados".
        """
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.mlflow_experiment_name = mlflow_experiment_name
        self.output_dir = output_dir

        if self.mlflow_tracking_uri is not None:
            self._init_mlflow()

    def _init_mlflow(self):
        """Inicializa la configuración de MLflow para el seguimiento de experimentos.

        Configura la URI de tracking y el experimento de MLflow.
        Si el experimento no existe, lo crea.

        Raises:
            Exception: Si ocurre un error al configurar MLflow.
        """

        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        try:
            mlflow.set_experiment(self.mlflow_experiment_name)
        except Exception:
            mlflow.create_experiment(self.mlflow_experiment_name)
            mlflow.set_experiment(self.mlflow_experiment_name)
        print(
            f"MLflow configurado — tracking: {self.mlflow_tracking_uri},\n"
            f"            experimento: {self.mlflow_experiment_name}"
        )

    def _analizar_variables_numericas(self, eva: AnalisisRiguroso) -> list[dict]:
        """Itera sobre todas las columnas y construye el reporte.

        Ejecuta los analiasis para cada variable numérica, incluyendo distribución,
        correlación y completitud.

        Args:
            eva: Instancia de AnalisisRiguroso con el DataFrame y la columna objetivo.
        """
        reporte: list[dict] = []
        cols_numeric = get_columnas_numericas(eva.df)
        excluir = self.COLS_EXCLUIR_BASE + [eva.target_col]

        # -- Numéricas --
        print("ANÁLISIS DE VARIABLES NUMÉRICAS (%d)" % len(cols_numeric))

        for col in cols_numeric:
            if col in excluir:
                continue
            print("📊 ANALIZANDO: %s" % col)

            analisis_var: dict = {"variable": col, "tipo": "numerica"}

            # Distribución
            print("  📊 Distribución:")
            dist = eva.analizar_distribucion(col)
            analisis_var["distribucion"] = dist
            if "error" not in dist:
                print(
                    "     Media=%.2f  Mediana=%.2f  Std=%.2f"
                    % (dist["mean"], dist["median"], dist["std"])
                )
                print(
                    "     Skewness=%.2f  Kurtosis=%.2f  Outliers=%.1f%%  Nulos=%.1f%%"
                    % (
                        dist["skew"],
                        dist["kurtosis"],
                        dist["pct_outliers"],
                        dist["pct_nulos"],
                    )
                )
                if dist.get("es_normal") is not None:
                    print("     ¿Distribución normal? %s" % ("SÍ" if dist["es_normal"] else "NO"))

            # Correlación
            print("  🔗 Correlación con %s:" % eva.target_col)
            corr = eva.analizar_correlacion(col)
            analisis_var["correlacion"] = corr
            if "error" not in corr:
                if "pearson_r" in corr:
                    print(
                        "     Pearson r=%.4f (p=%.4f) %s"
                        % (
                            corr["pearson_r"],
                            corr.get("pearson_pvalue", 1),
                            "✅" if corr.get("pearson_significativo") else "❌",
                        )
                    )
                if "spearman_r" in corr:
                    print(
                        "     Spearman ρ=%.4f (p=%.4f) %s"
                        % (
                            corr["spearman_r"],
                            corr.get("spearman_pvalue", 1),
                            "✅" if corr.get("spearman_significativo") else "❌",
                        )
                    )
                if "mutual_information" in corr:
                    print("     Información Mutua=%.4f" % corr["mutual_information"])
                if "auc_roc_individual" in corr:
                    print(
                        "     AUC-ROC individual=%.4f (%s)"
                        % (
                            corr["auc_roc_individual"],
                            corr.get("poder_discriminativo", "N/A"),
                        )
                    )
                if "cohens_d" in corr:
                    print(
                        "     Cohen's d=%.4f (Δmedias=%.2f)"
                        % (
                            corr["cohens_d"],
                            corr.get("diferencia_medias", 0),
                        )
                    )
            else:
                print("     ⚠️ %s" % corr["error"])

            # Completitud
            print("  ✅ Calidad del dato:")
            calidad = eva.evaluar_completitud(col)
            analisis_var["completitud"] = calidad
            print("     Completitud=%.1f%%" % calidad["completitud"])
            if "pct_inconsistentes" in calidad:
                print("     ⚠️ Inconsistencias con estado: %.1f%%" % calidad["pct_inconsistentes"])

            reporte.append(analisis_var)

        return reporte

    def _analizar_variables_categoricas(self, eva: AnalisisRiguroso) -> list[dict]:
        """Itera sobre todas las columnas y construye el reporte.

        Ejecuta los analiasis para cada variable categórica, incluyendo distribución,
        correlación y completitud.

        Args:
            eva: Instancia de AnalisisRiguroso con el DataFrame y la columna objetivo.
        """
        reporte: list[dict] = []
        cols_categoric = get_columnas_string(eva.df)
        excluir = self.COLS_EXCLUIR_BASE + [eva.target_col]

        # -- Categóricas --
        print("ANÁLISIS DE VARIABLES CATEGÓRICAS (%d)" % len(cols_categoric))

        for col in cols_categoric:
            if col in excluir:
                continue

            print("📊 ANALIZANDO: %s" % col)

            analisis_var: dict[str, Any] = {"variable": col, "tipo": "categorica"}

            cat = eva.analizar_variable_categorica(col)
            analisis_var["categorico"] = cat

            print("     Categorías únicas: %d" % cat["num_categorias"])
            print(
                "     Categoría dominante: %s (%.1f%%)"
                % (
                    cat.get("categoria_dominante", "N/A"),
                    cat["pct_categoria_dominante"],
                )
            )
            print(
                "     Chi-cuadrado significativo: %s"
                % ("SÍ" if cat.get("chi2_significativo") else "NO")
            )
            if "cramers_v" in cat:
                print("     V de Cramer: %.4f" % cat["cramers_v"])

            calidad = eva.evaluar_completitud(col)
            analisis_var["completitud"] = calidad
            print("     Completitud=%.1f%%" % calidad["completitud"])

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

        print("Calculando VIF para variables numéricas (excluyendo target)...")

        try:
            numeric_for_vif = eva.df.select(get_columnas_numericas(eva.df)).fill_null(0)
            if len(numeric_for_vif.columns) > 1:
                vif_df = eva.calcular_vif(numeric_for_vif, col_excluir=eva.target_col)
                high_vif = vif_df.filter(pl.col("VIF") > 10).sort("VIF", descending=True)
                print("Variables con VIF > 10 (alta multicolinealidad): %d" % len(high_vif))
                for row in high_vif.iter_rows(named=True):
                    print("  ⚠️ %s: VIF=%.2f" % (row["variable"], row["VIF"]))
                evidencias["vif"] = vif_df.to_dict()
            else:
                print("⚠️ No hay suficientes variables numéricas para VIF")
        except Exception as e:
            print("⚠️ Error en VIF: %s" % e)

        return evidencias

    def _generar_recomendaciones(self, eva: AnalisisRiguroso, reporte: list[dict]) -> list[dict]:
        """Genera recomendaciones a partir del reporte de análisis.

        Args:
            eva: Instancia de AnalisisRiguroso con el DataFrame y la columna objetivo.
            reporte: Lista de diccionarios con el análisis de cada variable.

        """
        recomendaciones: list[dict] = []

        print("RECOMENDACIONES FINALES")

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

            print("")
            if "INCLUIR" in recomendacion:
                print("✅ %s: %s" % (col, recomendacion))
            elif "EXCLUIR" in recomendacion:
                print("❌ %s: %s" % (col, recomendacion))
            else:
                print("⚠️ %s: %s" % (col, recomendacion))
                print("   Razón: %s" % razon)

        # Resumen
        resumen = pl.DataFrame(recomendaciones)

        print("RESUMEN DE RECOMENDACIONES")
        for row in resumen["recomendacion"].value_counts().iter_rows(named=True):
            print("   %s: %s" % (row["recomendacion"], row["count"]))

        # Variables problemáticas
        print("🔍 VERIFICACIÓN DE VARIABLES PROBLEMÁTICAS")
        for var in [
            "tot_dias_mora",
            "tot_num_moras",
            "tot_dias_mora_promedio",
            "tot_num_moras_promedio",
        ]:
            rec = next((r for r in recomendaciones if r["variable"] == var), None)
            if rec:
                print("")
                print("   %s: %s" % (var, rec["recomendacion"]))
                print("   Razón: %s" % rec["razon"])

        return recomendaciones

    def _plot_dashboard(
        self,
        df: pl.DataFrame,
        target_col: str,
        evidencias: dict,
        recomendaciones: list[dict],
    ) -> tuple[Any, dict]:
        """Delega la construccion del dashboard EVA al modulo de visualizacion."""
        return build_dashboard(df, target_col, evidencias, recomendaciones)
        
    def _salida_notebook(
        self,
        recomendaciones: list[dict],
        fig,
    ):
        """plt.show() + guarda .png y .csv en disco (consola)."""
        os.makedirs(f"{self.output_dir}/graficas", exist_ok=True)
        os.makedirs(f"{self.output_dir}/metricas", exist_ok=True)

        plt.show()

        png_path = f"{self.output_dir}/graficas/eda_completo.png"
        fig.savefig(png_path, dpi=150, bbox_inches="tight", facecolor="white")
        print("Dashboard guardado en: %s" % png_path)

        csv_path = f"{self.output_dir}/metricas/recomendaciones_eva.csv"
        pl.DataFrame(recomendaciones).write_csv(csv_path)
        print("Recomendaciones guardadas (%d vars) en: %s" % (len(recomendaciones), csv_path))
        print("EVA COMPLETADO")

    def _log_mlflow(
        self,
        df: pl.DataFrame,
        target_col: str,
        recomendaciones: list[dict],
        evidencias: dict,
        fig,
        run_name: str | None,
        dashboard_summary: dict | None = None,
    ):
        """Log a MLflow si el tracking URI esta configurado. Dual output: consola + MLflow."""
        try:
            if not mlflow.get_tracking_uri():
                return
        except Exception:
            return

        active_run = mlflow.active_run()
        run_ctx = (
            mlflow.start_run(run_name=run_name)
            if active_run is None
            else nullcontext(active_run)
        )

        with run_ctx as run:
            run_id = run.info.run_id
            if active_run is None:
                print("MLflow Run ID: %s" % run_id)
            else:
                print("MLflow Run activo reutilizado: %s" % run_id)

            mlflow.log_params(
                {
                    "total_registros": len(df),
                    "total_variables": len(recomendaciones),
                    "target_col": target_col,
                }
            )

            resumen = pl.DataFrame(recomendaciones)
            counts = resumen["recomendacion"].value_counts()
            for row in counts.iter_rows(named=True):
                clean_key = re.sub(r"[^a-zA-Z0-9_\s]", "", row["recomendacion"].strip("✅❌⚠️🔍 "))
                key = re.sub(r"\s+", "_", clean_key).strip("_")
                mlflow.log_metric(f"eva_{key}", row["count"])

            vars_incluir = [
                r["variable"] for r in recomendaciones if "INCLUIR" in r["recomendacion"]
            ]
            vars_excluir = [
                r["variable"] for r in recomendaciones if "EXCLUIR" in r["recomendacion"]
            ]
            mlflow.log_metric("eva_vars_incluir", len(vars_incluir))
            mlflow.log_metric("eva_vars_excluir", len(vars_excluir))

            if "vif" in evidencias:
                vif_data = pl.DataFrame(evidencias["vif"])
                high_vif = vif_data.filter(pl.col("VIF") > 10)
                mlflow.log_metric("eva_vif_gt_10", len(high_vif))
                if len(vif_data) > 0:
                    vif_max = vif_data.select(pl.col("VIF").cast(pl.Float64).max()).item()
                    vif_mean = vif_data.select(pl.col("VIF").cast(pl.Float64).mean()).item()
                    if isinstance(vif_max, (int, float)):
                        mlflow.log_metric("eva_vif_max", float(vif_max))
                    if isinstance(vif_mean, (int, float)):
                        mlflow.log_metric("eva_vif_mean", float(vif_mean))

            mlflow.log_figure(fig, "eva_dashboard.png")
            if dashboard_summary is not None:
                mlflow.log_dict(dashboard_summary, "eva_dashboard_summary.json")
                
            with tempfile.TemporaryDirectory() as tmpdir:
                csv_path = os.path.join(tmpdir, "recomendaciones_eva.csv")
                pl.DataFrame(recomendaciones).write_csv(csv_path)
                mlflow.log_artifact(csv_path)

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
                mlflow.log_artifact(reporte_path)

            print(f"MLflow: artefactos registrados — Run: {run_id}")

    def run(
        self,
        df: pl.DataFrame,
        target_col: str = "crisis_flag",
        run_name: str | None = None,
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
        print("EVA — ANÁLISIS EXPLORATORIO DE VARIABLES")
        print("📊 Registros: (%s)" % len(df))

        eva = AnalisisRiguroso(df, target_col=target_col)

        reporte_numericas = self._analizar_variables_numericas(eva)
        reporte_categoricas = self._analizar_variables_categoricas(eva)
        reporte_completo = reporte_numericas + reporte_categoricas

        evidencias = self._analizar_vif(eva)
        recomendaciones = self._generar_recomendaciones(eva, reporte_completo)

        fig, dashboard_summary = self._plot_dashboard(df, target_col, evidencias, recomendaciones)

        self._salida_notebook(recomendaciones, fig)
        self._log_mlflow(
            df,
            target_col,
            recomendaciones,
            evidencias,
            fig,
            run_name=run_name,
            dashboard_summary=dashboard_summary,
        )

        plt.close(fig)
        return recomendaciones, evidencias
