##
## DAG de Produccion
##
## @author omar.velez@yachaytech.edu.ec
## @version junio 2026
##

from datetime import datetime, timedelta
from platform import python_branch
from sched import scheduler

from airflow import DAG
from airflow.exceptions import AirflowFailException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag_args = {
    "depends_on_past": False,
    "email":["omargo33@gmail.com"],
    "email_on_failure":False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    ## elementos base    
}

dag01 = DAG(
    'DAG-Produccion',
    description="DAG para dar paso a produccion un entrenamiento aprobado",
    default_args=dag_args,
    schedule=timedelta(days=16),
    start_date=datetime(2026, 6, 29),
    catchup=False,
    tags=['Riesgo Credito']    
)
