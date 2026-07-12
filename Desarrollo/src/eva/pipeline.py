##
## @file pipeline.py
##
## Orquestador del EVA. Contiene toda la lógica de orquestación:
##   - Loop de variables para analizar distribución, correlación y completitud
##   - Loop de variables para generar recomendaciones
##   - Generación de plots individuales
##   - Salida a MLflow 3.x
##   - Se genera artefacto JSON con detalle de recomendaciones, evidencias y métricas del dashboard
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

import mlflow
import numpy as np
import polars as pl


def _serialize_for_json(obj):
    """Convierte objetos Polars/numpy a tipos serializables en JSON.
    
    Se toma el valor de polars que son Series o DataFrames y se convierten a listas, hay un JSON
    tiene problemas que ponia los datos continuos.
    
    Args:
        obj: Objeto a serializar (puede ser polars Series, DataFrame, numpy types, dict, list, etc.)
    
    Returns:
        Objeto serializable en JSON (list, dict, int, float, etc.)
    
    """
    if isinstance(obj, pl.Series):
        return obj.to_list()
    if isinstance(obj, pl.DataFrame):
        return obj.to_dict()
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_for_json(v) for v in obj]
    return obj


## El paquete eva se puede ejecutar como script independiente o como módulo.
## Toco codificar esta lógica para que funcione en ambos casos, Notebook y MLflow.
if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from eva.analisis_riguroso import AnalisisRiguroso
    from eva.dashboard import build_all_plots
    from eva.utilidades import (
        get_columnas_numericas,
        get_columnas_string,
    )
else:
    from .analisis_riguroso import AnalisisRiguroso
    from .dashboard import build_all_plots
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
        """Analisis de variables numericas: distribucion, correlacion, completitud.

        Args:
            eva: Instancia de AnalisisRiguroso que contiene el DataFrame y métodos de análisis.

        Returns:
            reporte: Lista de diccionarios con el análisis de cada variable numérica.

        """
        reporte: list[dict] = []
        cols_numeric = get_columnas_numericas(eva.df)
        excluir = self.COLS_EXCLUIR_BASE + [eva.target_col]

        for col in cols_numeric:
            if col in excluir:
                continue

            analisis_var: dict = {"variable": col, "tipo": "numerica"}
            analisis_var["distribucion"] = eva.analizar_distribucion(col)
            analisis_var["correlacion"] = eva.analizar_correlacion(col)
            analisis_var["completitud"] = eva.evaluar_completitud(col)

            reporte.append(analisis_var)

        return reporte

    def _analizar_variables_categoricas(self, eva: AnalisisRiguroso) -> list[dict]:
        """Analisis de variables categoricas: distribucion, correlacion, completitud.

        Args:
            eva: Instancia de AnalisisRiguroso que contiene el DataFrame y métodos de análisis.

        Returns:
            reporte: Lista de diccionarios con el análisis de cada variable categórica.

        """
        reporte: list[dict] = []
        cols_categoric = get_columnas_string(eva.df)
        excluir = self.COLS_EXCLUIR_BASE + [eva.target_col]

        for col in cols_categoric:
            if col in excluir:
                continue

            analisis_var: dict[str, Any] = {"variable": col, "tipo": "categorica"}
            analisis_var["categorico"] = eva.analizar_variable_categorica(col)
            analisis_var["completitud"] = eva.evaluar_completitud(col)

            reporte.append(analisis_var)

        return reporte

    def _analizar_vif(self, eva: AnalisisRiguroso) -> dict:
        """Calcula VIF y retorna evidencias.

        Args:
            eva: Instancia de AnalisisRiguroso que contiene el DataFrame y métodos de análisis.

        """
        evidencias: dict = {}
        try:
            numeric_for_vif = eva.df.select(get_columnas_numericas(eva.df)).fill_null(0)
            if len(numeric_for_vif.columns) > 1:
                vif_df = eva.calcular_vif(numeric_for_vif, col_excluir=eva.target_col)
                evidencias["vif"] = vif_df.to_dict()
        except Exception:
            pass
        return evidencias

    def _generar_recomendaciones(self, eva: AnalisisRiguroso, reporte: list[dict]) -> list[dict]:
        """Genera recomendaciones a partir del reporte de analisis.

        Args:
            eva: Instancia de AnalisisRiguroso que contiene el DataFrame y métodos de análisis.
            reporte: Lista de diccionarios con el análisis de cada variable.

        Returns:
            recomendaciones: Lista de diccionarios con las recomendaciones para cada variable.

        """
        recomendaciones: list[dict] = []

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

        return recomendaciones

    def _plot_dashboard(
        self,
        df: pl.DataFrame,
        target_col: str,
        evidencias: dict,
        recomendaciones: list[dict],
    ) -> tuple[Any, dict]:
        """Genera los plots individuales del EVA.
        
        Args:
            df: DataFrame de entrada con todas las variables.
            target_col: nombre de la columna objetivo (target) para correlación y análisis.
            evidencias: Diccionario con evidencias del análisis, incluyendo VIF si se calculó.
            recomendaciones: Lista de diccionarios con las recomendaciones para cada variable.
            
        Returns:
            image_paths: Lista de rutas de los plots generados.
            dashboard_summary: Diccionario con resumen de métricas del dashboard.
        
        """
        graficas_dir = os.path.join(self.output_dir, "graficas")
        return build_all_plots(df, target_col, evidencias, recomendaciones, output_dir=graficas_dir)

    def _salida_notebook(
        self,
        recomendaciones: list[dict],
    ):
        """Guarda CSV de recomendaciones en disco.
        
        Args:
            recomendaciones: Lista de diccionarios con las recomendaciones para cada variable.
            
        Returns:
            None. Guarda el archivo CSV en el directorio de salida especificado.
        
        """
        os.makedirs(f"{self.output_dir}/metricas", exist_ok=True)
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
        image_paths: list[str],
        run_name: str | None,
        dashboard_summary: dict | None = None,
        detale_path: str | None = None,
    ):
        """Log a MLflow: params, metrics, plots individuales y artefactos.
        
        Args:
            df: DataFrame de entrada con todas las variables.
            target_col: nombre de la columna objetivo (target) para correlación y análisis.
            recomendaciones: Lista de diccionarios con las recomendaciones para cada variable.
            evidencias: Diccionario con evidencias del análisis, incluyendo VIF si se calculó.
            image_paths: Lista de rutas de los plots generados.
            run_name: Nombre de la ejecución de MLflow.
            dashboard_summary: Diccionario con resumen de métricas del dashboard.
            detale_path: Ruta al archivo JSON con detalles adicionales.
            
        Returns:
            None. Loggea los artefactos y métricas en MLflow.
        """
        try:
            if not mlflow.get_tracking_uri():
                return
        except Exception:
            return

        active_run = mlflow.active_run()
        run_ctx = (
            mlflow.start_run(run_name=run_name) if active_run is None else nullcontext(active_run)
        )

        with run_ctx as run:
            run_id = run.info.run_id
            if active_run is None:
                print("MLflow Run ID: %s" % run_id)
            else:
                print("MLflow Run activo reutilizado: %s" % run_id)

            # Parametros
            mlflow.log_params(
                {
                    "total_registros": len(df),
                    "total_variables": len(recomendaciones),
                    "target_col": target_col,
                }
            )

            # Metricas
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

            # Plots individuales Graficos 
            for img_path in image_paths:
                mlflow.log_artifact(img_path, "plots")

            # Detalle JSON
            if detale_path and os.path.exists(detale_path):
                mlflow.log_artifact(detale_path)

            # Sube el dashboard_summary como un artefacto JSON si está disponible, EXITO!!
            if dashboard_summary is not None:
                mlflow.log_dict(dashboard_summary, "eva_dashboard_summary.json")

            # Crea la recomendaciones como CSV y lo sube como artefacto
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
                        default=_serialize_for_json,
                    )

            print(f"MLflow: {len(image_paths)} plots + artefactos registrados — Run: {run_id}")

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

        # Se lanzan el analisis riguroso de las variables.
        eva = AnalisisRiguroso(df, target_col=target_col)

        reporte_numericas = self._analizar_variables_numericas(eva)
        reporte_categoricas = self._analizar_variables_categoricas(eva)
        reporte_completo = reporte_numericas + reporte_categoricas
        evidencias = self._analizar_vif(eva)
        recomendaciones = self._generar_recomendaciones(eva, reporte_completo)

        image_paths, dashboard_summary = self._plot_dashboard(
            df, target_col, evidencias, recomendaciones
        )

        # Guardar detail JSON
        detale_path = os.path.join(self.output_dir, "evidencia_eva", "eva_dashboard_detail.json")
        os.makedirs(os.path.dirname(detale_path), exist_ok=True)
        with open(detale_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "recomendaciones": recomendaciones,
                    "reporte": reporte_completo,
                    "evidencias": evidencias,
                    "dashboard_summary": dashboard_summary,
                },
                f,
                indent=2,
                ensure_ascii=False, # Error caracteres Unicode en el JSON problemas con mis "emojis"
                default=_serialize_for_json,
            )

        self._log_mlflow(
            df,
            target_col,
            recomendaciones,
            evidencias,
            image_paths,
            run_name=run_name,
            dashboard_summary=dashboard_summary,
            detale_path=detale_path,
        )

        return recomendaciones, evidencias
