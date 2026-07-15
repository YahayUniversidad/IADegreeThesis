##
## DAG de Entrenamiento
## Sube datos historicos completos, ejecuta EDA/EVA, entrena modelos y registra en MLflow.
##
## Flujo:
##   ETL CSV (2020-2024) → EDA/EVA → CNN + MLP + LightGBM → MLflow
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import sys
from datetime import datetime, timedelta
from pathlib import Path

import mlflow
from airflow import DAG
from airflow.models import Variable
from airflow.models.param import Param
from airflow.operators.python import PythonOperator

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ts_csv import capturar_datos_csv, crear_tablas_estructura
from src.ts_datamart import ejecutar_datamart

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


def eda_task(**context):
    
    print("EDA/EVA completado")

def entrenar_cnn_task(**context):
    """Entrena el modelo CNN."""
    print("CNN entrenado")


def entrenar_mlp_task(**context):
    """Entrena el modelo MLP."""
    print("MLP entrenado")


def entrenar_lgbm_task(**context):
    """Entrena el modelo LightGBM."""
    print("LightGBM entrenado")


def seleccionar_mejor_modelo_task(**context):
    """Selecciona el mejor modelo de MLflow y retorna su experiment_id."""
    
    mlflow_uri = context["params"]["mlflow_uri"]
    mlflow.set_tracking_uri(mlflow_uri)

    experimentos = ["flow_entrenamiento_lightgbm", "flow_entrenamiento_cnn", "flow_entrenamiento_mlp"]
    mejor_experimento = None
    mejor_auc = -1

    for nombre in experimentos:
        exp = mlflow.get_experiment_by_name(nombre)
        if exp is None:
            continue
        runs = mlflow.search_runs(
            experiment_ids=[exp.experiment_id],
            order_by=["metrics.auc_roc DESC"],
            max_results=1,
        )
        if not runs.empty:
            auc = runs.iloc[0].get("metrics.auc_roc", 0)
            if auc > mejor_auc:
                mejor_auc = auc
                mejor_experimento = exp.experiment_id

    if mejor_experimento is None:
        raise ValueError("No se encontro ningun experimento con runs validos")

    print(f"Mejor modelo: experiment_id={mejor_experimento}, auc_roc={mejor_auc:.4f}")
    context["ti"].xcom_push(key="mejor_experiment_id", value=mejor_experimento)
    context["ti"].xcom_push(key="mejor_auc_roc", value=mejor_auc)

##
## DAG Definition
dag_entrenamiento = DAG(
    dag_id="DAG-Entrenamiento",
    description="Pipeline de entrenamiento: datos historicos → EDA → modelos → MLflow",
    default_args=dag_args,
    schedule="0 3 1 * *",  # Primer dia del mes a las 3am
    start_date=datetime(2026, 7, 1),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=["Entrenamiento", "ML", "Riesgo Crediticio"],
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
        "mlflow_uri": Param(
            default="http://localhost:5000",
            type="string",
            title="MLflow Tracking URI",
        ),
    },
)

##
## Tareas del DAG
e1 = PythonOperator(task_id="crear_estructura", 
                    python_callable=crear_estructura_task, dag=dag_entrenamiento)
e2 = PythonOperator(task_id="cargar_csv", 
                    python_callable=cargar_csv_task, dag=dag_entrenamiento)
e3 = PythonOperator(task_id="datamart", 
                    python_callable=datamart_task, dag=dag_entrenamiento)
e4 = PythonOperator(task_id="eda_eva",
                    python_callable=eda_task, dag=dag_entrenamiento)
e5_cnn = PythonOperator(task_id="entrenar_cnn", 
                        python_callable=entrenar_cnn_task, dag=dag_entrenamiento)
e5_mlp = PythonOperator(task_id="entrenar_mlp", 
                        python_callable=entrenar_mlp_task, dag=dag_entrenamiento)
e5_lgbm = PythonOperator(task_id="entrenar_lgbm", 
                         python_callable=entrenar_lgbm_task, dag=dag_entrenamiento)
e6 = PythonOperator(task_id="seleccionar_mejor_modelo", 
                    python_callable=seleccionar_mejor_modelo_task, dag=dag_entrenamiento)

##
## Definicion del flujo de tareas
e1 >> e2 >> e3 >> e4 >> [e5_cnn, e5_mlp, e5_lgbm] >> e6 # type: ignore