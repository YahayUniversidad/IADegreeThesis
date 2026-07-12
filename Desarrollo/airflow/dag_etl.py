##
## DAG en ETL para la carga de data en el sistema crediticio
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import sys

sys.path.insert(0, '..')

from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.models import Variable
from airflow.models.param import Param
from airflow.operators.python import PythonOperator
from src.sql import capturar_datos_csv, crear_tablas_estructura
from src.datamart import ejecutar as ejecutar_datamart

## Agrega la raiz de Desarrollo al PYTHONPATH para importar src.sql
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

dag_args = {
    "depends_on_past": False,
    "email": ["omargo33@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
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
    ejecutar_datamart(string_conexion)
    
dag_etl = DAG(
    dag_id="DAG-ETL-CSV",
    description="Carga ETL de archivos CSV desde carpeta local hacia base de datos",
    default_args=dag_args,
    schedule="0 8-23 * * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    max_active_runs=1,     # Si se demora solo ejecuta una sola vez
    max_active_tasks=1,    # Fuerza una sola tarea activa en este DAG, es para no saturar servidores
    tags=["ETL", "CSV", "Riesgo Crediticio"],
    params={
        "string_conexion": Param(
            default=Variable.get("string_conexion", default_var=""),
            type="string",
            title="Cadena de conexión DB",
            description="Cadena psycopg2 de conexión a la base de datos (guardada en Variable 'string_conexion')"
        ),
        "path_carpeta_csv": Param(
            default="/opt/airflow/data/csv",
            type="string",
            minLength=1,
            title="Ruta carpeta CSV",
            description="Carpeta donde se detectan archivos .csv para procesar"
        ),
    },
)

t1_crear_estructura = PythonOperator(
    task_id="crear_estructura_tablas",
    python_callable=crear_estructura_task,
    dag=dag_etl,
)

t2_cargar_csv = PythonOperator(
    task_id="capturar_y_cargar_csv",
    python_callable=cargar_csv_task,
    dag=dag_etl,
)

t3_datamart = PythonOperator(
    task_id="ejecutar_datamart",
    python_callable=datamart_task,
    dag=dag_etl,
)

t1_crear_estructura >> t2_cargar_csv >> t3_datamart # type: ignore
