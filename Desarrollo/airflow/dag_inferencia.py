##
## DAG de Inferencia (Produccion)
## Toma datos recientes, actualiza datamart, ejecuta predicciones y actualiza Superset.
##
## Flujo:
##   ETL CSV (periodo reciente) → Datamart → Prediccion → Superset
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

import mlflow
import psycopg2
from airflow import DAG
from airflow.models import Variable
from airflow.models.param import Param
from airflow.operators.python import PythonOperator

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ts_datamart import ejecutar_datamart
from src.ts_csv import capturar_datos_csv, crear_tablas_estructura

##
## DAG Arguments
dag_args = {
    "depends_on_past": False,
    "email": ["omargo33+airflow@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": True,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

def crear_estructura_task(**context):
    string_conexion = context["params"]["string_conexion"]
    crear_tablas_estructura(string_conexion)

def cargar_csv_task(**context):
    string_conexion = context["params"]["string_conexion"]
    path_carpeta_csv = context["params"]["path_carpeta_csv"]
    capturar_datos_csv(string_conexion, path_carpeta_csv)

def datamart_task(**context):
    string_conexion = context["params"]["string_conexion"]
    try:
        ejecutar_datamart(string_conexion)
    except Exception as e:
        print(f"Error al ejecutar datamart: {e}")
        raise RuntimeError(f"Error al ejecutar datamart: {e}") from e
    
def prediccion_task(**context):

    string_conexion = context["params"]["string_conexion"]
    experiment_id = context["params"]["experiment_id"]
    periodo = context["params"]["periodo"]

    mlflow.set_tracking_uri(context["params"]["mlflow_uri"])

    # Obtener el mejor run del experimento
    experiment = mlflow.get_experiment(experiment_id)
    runs = mlflow.search_runs(
        experiment_ids=[experiment_id],
        order_by=["metrics.auc_roc DESC"],
        max_results=1,
    )
    if runs.empty:
        raise ValueError(f"No hay runs en el experimento {experiment_id}")

    best_run_id = runs.iloc[0]["run_id"]
    model_uri = f"runs:/{best_run_id}/modelo"
    print(f"Mejor modelo: run_id={best_run_id}")

    # Cargar modelo y ejecutar predicciones
    modelo = mlflow.pyfunc.load_model(model_uri)

    conn = psycopg2.connect(string_conexion)
    conn.autocommit = True
    try:
        # TODO: implementar logica de prediccion con el modelo cargado
        # modelo.predict(...)

        # Por ahora, registrar que se ejecuto
        print(f"Prediccion ejecutada para periodo: {periodo}")
        print(f"Modelo utilizado: {best_run_id}")
    finally:
        conn.close()

def superset_task(**context):
    # TODO: integrar con MCP de Superset para refrescar dashboards
    print("Superset: refresh pendiente de implementar")

##
## DAG Definition
dag_inferencia = DAG(
    dag_id="DAG-Inferencia",
    description="Pipeline de inferencia: datos recientes → datamart → prediccion → superset",
    default_args=dag_args,
    schedule="0 6 * * *",  # Diario a las 6am
    start_date=datetime(2026, 7, 1),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["Inferencia", "Produccion", "Riesgo Crediticio"],
    params={
        "string_conexion": Param(
            default=Variable.get("string_conexion", default_var=""),
            type="string",
            title="Cadena de conexion DB",
        ),
        "path_carpeta_csv": Param(
            default="/opt/airflow/data/csv",
            type="string",
            title="Ruta carpeta CSV",
        ),
        "experiment_id": Param(
            default="",
            type="string",
            title="MLflow Experiment ID",
            description="ID del experimento MLflow con el mejor modelo",
        ),
        "mlflow_uri": Param(
            default="http://localhost:5000",
            type="string",
            title="MLflow Tracking URI",
        ),
        "periodo": Param(
            default="mes",
            type="string",
            title="Periodo de datos",
            description="Ultimo mes, trimestre, semestre o anio",
        ),
    },
)

##
## Tareas del DAG
t1 = PythonOperator(task_id="crear_estructura", python_callable=crear_estructura_task, dag=dag_inferencia)
t2 = PythonOperator(task_id="cargar_csv", python_callable=cargar_csv_task, dag=dag_inferencia)
t3 = PythonOperator(task_id="datamart", python_callable=datamart_task, dag=dag_inferencia)
t4 = PythonOperator(task_id="prediccion", python_callable=prediccion_task, dag=dag_inferencia)
t5 = PythonOperator(task_id="superset", python_callable=superset_task, dag=dag_inferencia)

##
## Definicion del flujo de tareas
t1 >> t2 >> t3 >> t4 >> t5 # type: ignore