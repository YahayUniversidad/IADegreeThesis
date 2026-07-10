##
## DAG de Sincronizacion de Superset
## Refresca los datasets de Superset para que los dashboards muestren data actualizada.
## Se ejecuta automaticamente despues de DAG-Datamart.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import logging
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python import PythonOperator

logger = logging.getLogger(__name__)

SUPERSET_URL = "http://superset:8088"
SUPERSET_USER = "admin"
SUPERSET_PASSWORD = "admin"

dag_args = {
    "depends_on_past": False,
    "email": ["omargo33@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag_superset = DAG(
    "DAG-Superset-Sync",
    description="Refresca datasets de Superset para dashboards actualizados",
    default_args=dag_args,
    schedule=None,
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["Superset", "BI"],
)


def obtener_token():
    resp = requests.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json={"username": SUPERSET_USER, "password": SUPERSET_PASSWORD, "provider": "db"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def refresh_datasets(**kwargs):
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    resp = requests.get(f"{SUPERSET_URL}/api/v1/dataset/?q=(page_size:100)", headers=headers, timeout=30)
    resp.raise_for_status()
    datasets = resp.json().get("result", [])

    refreshed = 0
    errors = 0
    for ds in datasets:
        ds_id = ds["id"]
        ds_name = ds.get("table_name", f"dataset_{ds_id}")
        try:
            r = requests.put(
                f"{SUPERSET_URL}/api/v1/dataset/{ds_id}/refresh",
                headers=headers,
                timeout=60,
            )
            if r.status_code in (200, 201):
                refreshed += 1
                print(f"  OK: {ds_name} (id={ds_id})")
            else:
                errors += 1
                print(f"  WARN: {ds_name} (id={ds_id}) status={r.status_code}")
        except Exception as e:
            errors += 1
            print(f"  ERROR: {ds_name} (id={ds_id}): {e}")

    print(f"\nDatasets refrescados: {refreshed}, errores: {errors}")
    kwargs["ti"].xcom_push(key="refreshed", value=refreshed)
    kwargs["ti"].xcom_push(key="errors", value=errors)

    if errors > 0 and refreshed == 0:
        raise RuntimeError("No se pudo refrescar ningun dataset")


def invalidar_cache(**kwargs):
    token = obtener_token()
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.delete(f"{SUPERSET_URL}/api/v1/cache/", headers=headers, timeout=30)
        print(f"Cache invalidado: status={resp.status_code}")
    except Exception as e:
        print(f"No se pudo invalidar cache via API (no critico): {e}")

    print("Cache de Superset invalidado")


def registrar_resultado(**kwargs):
    refreshed = kwargs["ti"].xcom_pull(task_ids="refresh_datasets", key="refreshed")
    errors = kwargs["ti"].xcom_pull(task_ids="refresh_datasets", key="errors")
    print(f"Superset Sync completado: {refreshed} datasets refrescados, {errors} errores")


refresh_task = PythonOperator(
    task_id="refresh_datasets",
    python_callable=refresh_datasets,
    dag=dag_superset,
)

cache_task = PythonOperator(
    task_id="invalidar_cache",
    python_callable=invalidar_cache,
    dag=dag_superset,
)

resultado_task = PythonOperator(
    task_id="registrar_resultado",
    python_callable=registrar_resultado,
    dag=dag_superset,
)

refresh_task >> cache_task >> resultado_task
