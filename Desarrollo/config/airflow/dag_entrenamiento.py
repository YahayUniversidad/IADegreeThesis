##
## DAG de Entrenamiento
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
    'DAG-Entrenamiento',
    description="DAG para realizar el entrenamiento en base a la data recopilida del sistema crediticio",
    default_args=dag_args,
    schedule=timedelta(days=15),
    start_date=datetime(2026, 6, 29),
    catchup=False,
    tags=['Riesgo Credito']    
)

def paso0_func(**kwargs):
    return { "ok" : 1 }

paso0 = PythonOperator(
    task_id='paso_0',
    python_callable=paso0_func,
    dag=dag01
)

paso1 = BashOperator(
    task_id="paso_1",
    bash_command='echo "Ahora es $(date)"',
    dag=dag01
)

def paso2_func(**kwargs):
    return { "ok": 2 }

paso2 = PythonOperator(
    task_id="paso_2",
    python_callable=paso2_func,
    dag=dag01
)

paso3 = BashOperator(
    task_id="paso_3",
    bash_command='echo "Ahora es $(date)"',
    dag=dag01
)


paso0 >> [paso1, paso2] >> paso3 