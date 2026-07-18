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

import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.models import Variable
from airflow.models.param import Param
from airflow.operators.python import PythonOperator

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ts_csv import capturar_datos_csv, crear_tablas_estructura
from src.ts_datamart import ejecutar_datamart
from src.ts_predicciones import ejecutar_predicciones

##
## DAG Arguments
dag_args = {
    "depends_on_past": False,
    "email": ["omargo33+airflow@gmail.com"],
    "email_on_failure": True,
    "email_on_retry": True,
    "email_on_success": True,
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
    path_trabajo = context["params"].get("path_trabajo", "/opt/airflow/data/salida")
    
    try:
        ejecutar_predicciones(
            string_conexion=string_conexion,
            path_trabajo=path_trabajo
        )
    except Exception as e:
        print(f"Error al ejecutar predicciones: {e}")
        raise RuntimeError(f"Error al ejecutar predicciones: {e}") from e

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
        "path_trabajo": Param(
            default="/opt/airflow/data/salida",
            type="string",
            title="Ruta de salida",
            description="Directorio base para artefactos del modelo",
        ),
        "experiment_id": Param(
            default="",
            type="string",
            title="MLflow Experiment ID",
            description="ID del experimento MLflow con el mejor modelo",
        ),
        "mlflow_uri": Param(
            default=Variable.get("mlflow_uri", default_var="http://192.168.0.97:5000"),
            type="string",
            title="MLflow Tracking URI",
        ),
        "mlflow_experiment": Param(
            default="jupy_predicciones",
            type="string",
            title="MLflow Experiment Name",
            description="Nombre del experimento MLflow para predicciones",
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
t1 = PythonOperator(task_id="crear_estructura", python_callable=crear_estructura_task, 
                    dag=dag_inferencia)
t2 = PythonOperator(task_id="cargar_csv", python_callable=cargar_csv_task, dag=dag_inferencia)
t3 = PythonOperator(task_id="datamart", python_callable=datamart_task, dag=dag_inferencia)
t4 = PythonOperator(task_id="prediccion", python_callable=prediccion_task, dag=dag_inferencia)
t5 = PythonOperator(task_id="superset", python_callable=superset_task, dag=dag_inferencia)

##
## Definicion del flujo de tareas
t1 >> t2 >> t3 >> t4 >> t5 # type: ignore
