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

import gc
import glob
import json
import os
import re
import tempfile
from contextlib import nullcontext
from datetime import date
from typing import Any

import mlflow
import numpy as np
import polars as pl
from sqlalchemy import create_engine
from src.common.utilidades import get_columnas_numericas, get_columnas_string
from src.ts_eva.analisis_riguroso import AnalisisRiguroso
from src.ts_eva.dashboard import build_all_plots
from src.ts_eva.utilidades import espacio_tiempo
from src.ts_sql.queries import consultar_creditos_mensuales


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
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_for_json(v) for v in obj]
    return obj


class PipelineEVA:
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
        output_dir: str,
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
        self.output_dir = output_dir

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
                reporte_serializable = _serialize_for_json(
                    {
                        "recomendaciones": recomendaciones,
                        "evidencias": evidencias,
                        "vars_incluir": vars_incluir,
                        "vars_excluir": vars_excluir,
                    }
                )
                with open(reporte_path, "w", encoding="utf-8") as f:
                    json.dump(reporte_serializable, f, indent=2, ensure_ascii=False)
                    
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

        # Se lanzan el analisis riguroso de las variables.
        eva = AnalisisRiguroso(df, target_col=target_col)

        reporte_numericas = self._analizar_variables_numericas(eva)
        reporte_categoricas = self._analizar_variables_categoricas(eva)
        reporte_completo = reporte_numericas + reporte_categoricas
        evidencias = self._analizar_vif(eva)
        recomendaciones = self._generar_recomendaciones(eva, reporte_completo)

        graficas_dir = os.path.join(self.output_dir, "graficas")
        image_paths, dashboard_summary = build_all_plots(
            df, target_col, evidencias, recomendaciones, output_dir=graficas_dir
        )

        # Guardar detail JSON
        detale_path = os.path.join(self.output_dir, "evidencia_eva", "eva_dashboard_detail.json")
        os.makedirs(os.path.dirname(detale_path), exist_ok=True)
        serializable_data = _serialize_for_json(
            {
                "recomendaciones": recomendaciones,
                "reporte": reporte_completo,
                "evidencias": evidencias,
                "dashboard_summary": dashboard_summary,
            }
        )
        with open(detale_path, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

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


def _preprocesar_datos(df_raw):
    """Recibe datos de la MV. Ajusta tipos y ordena.

    La MV ya calcula: agregacion, tasas, 21 features y crisis_flag.

    Args:
        df_raw: DataFrame crudo de la MV (polars)

    Returns:
        df: DataFrame preprocesado, listo para EVA.
    """
    df = df_raw.clone()

    # Castear columnas Decimal a Float64 para evitar overflow
    for col in df.columns:
        if df[col].dtype == pl.Decimal:
            df = df.with_columns(pl.col(col).cast(pl.Float64))

    df = df.with_columns(pl.col("mes").cast(pl.Date))

    return df.sort(["bloque_id", "mes"])


def _ejecutar_pipeline(
    df_features,
    archivos_lotes,
    total_raw,
    run_key,
    anio_inicio,
    anio_fin,
    meses_por_lote,
    path_salida,
):
    """Ejecuta el pipeline consolidado de EDA + EVA.

    Args:
        df_features: DataFrame consolidado de features (polars)
        archivos_lotes: Lista de archivos de lotes procesados
        total_raw: Total de registros crudos procesados
        run_key: Clave de ejecución para MLflow
        anio_inicio: Año de inicio del análisis
        anio_fin: Año de fin del análisis
        meses_por_lote: Número de meses por lote
        path_salida: Ruta de salida para resultados y artefactos

    Returns:
        tuple: DataFrame de features y recomendaciones generadas por el pipeline.
    """

    if run_key is None:
        run_key = f"{anio_inicio}_{anio_fin}_{meses_por_lote}m"

    run_name = f"eva_{run_key}"
    evidencias_path = f"{path_salida}/evidencia_eva/reporte_eva.json"
    recomendaciones_path = f"{path_salida}/metricas/recomendaciones_eva.csv"

    with mlflow.start_run(run_name=run_name):
        mlflow.set_tag("eva_key", run_key)
        mlflow.set_tag("pipeline", "eda_eva_consolidado")
        mlflow.log_params(
            {
                "anio_inicio": anio_inicio,
                "anio_fin": anio_fin,
                "meses_por_lote": meses_por_lote,
                "run_key": run_key,
            }
        )

        pipeline = PipelineEVA(output_dir = path_salida)
        recomendaciones, evidencias = pipeline.run(
            df_features,
            target_col="crisis_flag",
            run_name=run_name,
        )

        crisis_ratio = float(df_features["crisis_flag"].mean())  # type: ignore
        filas_dataset = len(df_features)
        columnas_dataset = len(df_features.columns)
        lotes_procesados = len(archivos_lotes)

        with open(evidencias_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "recomendaciones": recomendaciones,
                    "evidencias": evidencias,
                    "filas_dataset": filas_dataset,
                    "columnas_dataset": columnas_dataset,
                    "registros_raw_total": total_raw,
                    "lotes_procesados": lotes_procesados,
                    "crisis_ratio": crisis_ratio,
                    "run_name": run_name,
                    "run_key": run_key,
                },
                f,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

        mlflow.log_metrics(
            {
                "filas_dataset": float(filas_dataset),
                "columnas_dataset": float(columnas_dataset),
                "registros_raw_total": float(total_raw),
                "lotes_procesados": float(lotes_procesados),
                "crisis_ratio": crisis_ratio,
            }
        )
        if os.path.exists(evidencias_path):
            mlflow.log_artifact(evidencias_path)
        if os.path.exists(recomendaciones_path):
            mlflow.log_artifact(recomendaciones_path)
    print(f"run_name unificado en MLflow: {run_name}," + 
          f" crisis_ratio registrado en MLflow: {crisis_ratio:.6f}")

    return df_features, recomendaciones

def _procesar_eva(run_key, path_lotes, engine, anio_inicio, anio_fin, meses_por_lote):
    """Procesa los datos de la MV, genera features y ejecuta el pipeline consolidado de EDA + EVA.

    Args:
        run_key: Clave de ejecución para MLflow
        path_lotes: Ruta de salida para resultados y artefactos
        engine: Motor de base de datos para consultas SQL
        anio_inicio: Año de inicio del análisis
        anio_fin: Año de fin del análisis
        meses_por_lote: Número de meses por lote

    Raises:
        ValueError: Se lanza si no se generaron lotes con datos.

    Returns:
        tuple: DataFrame de features y recomendaciones generadas por el pipeline.
    """

    for f in glob.glob(f"{path_lotes}/features_*.parquet"):
        os.remove(f)

    archivos_lotes = []
    total_raw = 0

    fecha_inicio = date(anio_inicio, 1, 1)
    fecha_fin = date(anio_fin + 1, 1, 1)

    for ini, fin in espacio_tiempo(fecha_inicio, fecha_fin, meses_por_lote):
        query_lote = consultar_creditos_mensuales(ini, fin)

        df_raw = pl.read_database(query=query_lote, connection=engine, infer_schema_length=None)
        n_raw = len(df_raw)
        total_raw += n_raw

        if n_raw == 0:
            del df_raw
            gc.collect()
            continue

        df_feat = _preprocesar_datos(df_raw)

        out_parquet = f"{path_lotes}/features_{ini.strftime('%Y%m')}_{fin.strftime('%Y%m')}.parquet"
        df_feat.write_parquet(out_parquet)
        archivos_lotes.append(out_parquet)

        del df_raw, df_feat
        gc.collect()

    if not archivos_lotes:
        raise ValueError("No se generaron lotes con datos.")

    df_features = pl.scan_parquet(f"{path_lotes}/features_*.parquet").collect()
    df_features = df_features.sort(["bloque_id", "mes"])
    datasets_dir = f"{path_lotes}/datasets"
    os.makedirs(datasets_dir, exist_ok=True)
    dataset_path = f"{datasets_dir}/datos_preprocesados.csv"
    df_features.write_csv(dataset_path)
    print(f"Dataset: {len(df_features):,} registros, {len(df_features.columns)} columnas")

    return _ejecutar_pipeline(
        df_features,
        archivos_lotes=archivos_lotes,
        total_raw=total_raw,
        run_key=run_key,
        anio_inicio=anio_inicio,
        anio_fin=anio_fin,
        meses_por_lote=meses_por_lote,
        path_salida=path_lotes,
    )

def analizar_eda_eva(
    string_conexion,
    mlflow_tracking_uri,
    mlflow_experiment_name,
    path_salida,
    anio_inicio=2015,
    anio_fin=2026,
    meses_por_lote=1,
    run_key=None,
):
    """Ejecuta el pipeline consolidado de EDA + EVA.

    Args:
        string_conexion (str): Cadena de conexion a la base de datos.
        mlflow_tracking_uri (str): URI de tracking de MLflow.
        mlflow_experiment_name (str): Nombre del experimento en MLflow.
        path_salida (str): Ruta de salida para resultados y artefactos.
        anio_inicio (int): Ano de inicio del analisis (por defecto 2015).
        anio_fin (int): Ano de fin del analisis (por defecto 2026).
        meses_por_lote (int): Numero de meses por lote (por defecto 1).
        run_key (str, optional): Clave de ejecucion para MLflow.
    """
    path_lotes = f"{path_salida}/lotes"

    for d in ["evidencia_eva", "datasets", "graficas", "metricas", "logs", "lotes"]:
        os.makedirs(f"{path_salida}/{d}", exist_ok=True)

    engine = create_engine(string_conexion)

    mlflow.set_tracking_uri(mlflow_tracking_uri)
    try:
        mlflow.set_experiment(mlflow_experiment_name)
    except Exception:
        mlflow.create_experiment(mlflow_experiment_name)
        mlflow.set_experiment(mlflow_experiment_name)
    print(f"MLflow configurado — tracking: {mlflow_tracking_uri},"+
          f" experiment: {mlflow_experiment_name}")

    df_features, recomendaciones = _procesar_eva(
        run_key, path_lotes, engine, anio_inicio, anio_fin, meses_por_lote
    )
