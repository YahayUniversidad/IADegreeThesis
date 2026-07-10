##
## DAG de Datamart
## Refresca la vista materializada, dimensiones y tabla de hechos.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

dag_args = {
    "depends_on_past": False,
    "email": ["omargo33@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

dag_datamart = DAG(
    "DAG-Datamart",
    description="Refresca vista materializada, dimensiones y fact table del datamart",
    default_args=dag_args,
    schedule="0 2 * * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["Datamart", "BI"],
)


def refresh_mv(**kwargs):
    hook = PostgresHook(postgres_conn_id="datamart_db")
    hook.run("REFRESH MATERIALIZED VIEW CONCURRENTLY mv_creditos_mensuales", autocommit=True)
    count = hook.get_first("SELECT COUNT(*) FROM mv_creditos_mensuales")[0]
    kwargs["ti"].xcom_push(key="mv_rows", value=count)
    print(f"mv_creditos_mensuales refrescada: {count:,} registros")


def poblar_dim_tiempo(**kwargs):
    hook = PostgresHook(postgres_conn_id="datamart_db")
    hook.run(
        """
        INSERT INTO dim_tiempo (mes, anio, trimestre, mes_del_anio, nombre_mes)
        SELECT DISTINCT
            mes,
            EXTRACT(YEAR FROM mes)::INTEGER,
            EXTRACT(QUARTER FROM mes)::INTEGER,
            EXTRACT(MONTH FROM mes)::INTEGER,
            TO_CHAR(mes, 'TMMonth')
        FROM mv_creditos_mensuales
        ON CONFLICT (mes) DO NOTHING
        """,
        autocommit=True,
    )
    print("dim_tiempo poblada")


def poblar_dim_riesgo(**kwargs):
    hook = PostgresHook(postgres_conn_id="datamart_db")
    hook.run(
        """
        INSERT INTO dim_riesgo (codigo_riesgo, descripcion)
        SELECT DISTINCT riesgo, riesgo
        FROM mv_creditos_mensuales
        ON CONFLICT (codigo_riesgo) DO NOTHING
        """,
        autocommit=True,
    )
    print("dim_riesgo poblada")


def poblar_dim_sector(**kwargs):
    hook = PostgresHook(postgres_conn_id="datamart_db")
    hook.run(
        """
        INSERT INTO dim_sector (codigo_sector, descripcion)
        SELECT DISTINCT sector, sector
        FROM mv_creditos_mensuales
        ON CONFLICT (codigo_sector) DO NOTHING
        """,
        autocommit=True,
    )
    print("dim_sector poblada")


def poblar_dim_sucursal(**kwargs):
    hook = PostgresHook(postgres_conn_id="datamart_db")
    hook.run(
        """
        INSERT INTO dim_sucursal (codigo_sucursal, codigo_provincia)
        SELECT DISTINCT codigo_sucursal, 0
        FROM mv_creditos_mensuales
        ON CONFLICT (codigo_sucursal) DO NOTHING
        """,
        autocommit=True,
    )
    print("dim_sucursal poblada")


def poblar_fact(**kwargs):
    hook = PostgresHook(postgres_conn_id="datamart_db")
    hook.run(
        """
        INSERT INTO fact_creditos_mensual (
            id_tiempo, id_riesgo, id_sector, id_sucursal,
            num_creditos, monto_total, monto_promedio,
            dias_mora_promedio, num_moras_promedio,
            tasa_mora_90, tasa_judicial, tasa_cierre,
            total_gestion_cobro, total_costo_judicial,
            tasa_interes_promedio, saldo_promedio,
            creditos_cerrados, num_clientes_unicos,
            creditos_por_cliente, plazo_promedio,
            desviacion_montos, coef_variacion_montos,
            antiguedad_promedio_meses,
            tasa_crecimiento_creditos, tasa_crecimiento_monto,
            crisis_flag, bloque_id
        )
        SELECT
            dt.id_tiempo, dr.id_riesgo, ds.id_sector, dsu.id_sucursal,
            mv.num_creditos, mv.monto_total, mv.monto_promedio,
            mv.dias_mora_promedio, mv.num_moras_promedio,
            mv.tasa_mora_90, mv.tasa_judicial, mv.tasa_cierre,
            mv.total_gestion_cobro, mv.total_costo_judicial,
            mv.tasa_interes_promedio, mv.saldo_promedio,
            mv.creditos_cerrados, mv.num_clientes_unicos,
            mv.creditos_por_cliente, mv.plazo_promedio,
            mv.desviacion_montos, mv.coef_variacion_montos,
            mv.antiguedad_promedio_meses,
            mv.tasa_crecimiento_creditos, mv.tasa_crecimiento_monto,
            mv.crisis_flag, mv.bloque_id
        FROM mv_creditos_mensuales mv
        JOIN dim_tiempo dt ON dt.mes = mv.mes
        JOIN dim_riesgo dr ON dr.codigo_riesgo = mv.riesgo
        JOIN dim_sector ds ON ds.codigo_sector = mv.sector
        JOIN dim_sucursal dsu ON dsu.codigo_sucursal = mv.codigo_sucursal
        ON CONFLICT (id_tiempo, id_riesgo, id_sector, id_sucursal) DO UPDATE SET
            num_creditos              = EXCLUDED.num_creditos,
            monto_total               = EXCLUDED.monto_total,
            monto_promedio            = EXCLUDED.monto_promedio,
            dias_mora_promedio        = EXCLUDED.dias_mora_promedio,
            num_moras_promedio        = EXCLUDED.num_moras_promedio,
            tasa_mora_90              = EXCLUDED.tasa_mora_90,
            tasa_judicial             = EXCLUDED.tasa_judicial,
            tasa_cierre               = EXCLUDED.tasa_cierre,
            total_gestion_cobro       = EXCLUDED.total_gestion_cobro,
            total_costo_judicial      = EXCLUDED.total_costo_judicial,
            tasa_interes_promedio     = EXCLUDED.tasa_interes_promedio,
            saldo_promedio            = EXCLUDED.saldo_promedio,
            creditos_cerrados         = EXCLUDED.creditos_cerrados,
            num_clientes_unicos       = EXCLUDED.num_clientes_unicos,
            creditos_por_cliente      = EXCLUDED.creditos_por_cliente,
            plazo_promedio            = EXCLUDED.plazo_promedio,
            desviacion_montos         = EXCLUDED.desviacion_montos,
            coef_variacion_montos     = EXCLUDED.coef_variacion_montos,
            antiguedad_promedio_meses = EXCLUDED.antiguedad_promedio_meses,
            tasa_crecimiento_creditos = EXCLUDED.tasa_crecimiento_creditos,
            tasa_crecimiento_monto    = EXCLUDED.tasa_crecimiento_monto,
            crisis_flag               = EXCLUDED.crisis_flag,
            bloque_id                 = EXCLUDED.bloque_id
        """,
        autocommit=True,
    )
    count = hook.get_first("SELECT COUNT(*) FROM fact_creditos_mensual")[0]
    kwargs["ti"].xcom_push(key="fact_rows", value=count)
    print(f"fact_creditos_mensual poblada: {count:,} registros")


def validar_datamart(**kwargs):
    hook = PostgresHook(postgres_conn_id="datamart_db")

    mv_rows = kwargs["ti"].xcom_pull(task_ids="refresh_mv", key="mv_rows")
    fact_rows = kwargs["ti"].xcom_pull(task_ids="poblar_fact", key="fact_rows")

    nulls = hook.get_first(
        "SELECT COUNT(*) FROM fact_creditos_mensual "
        "WHERE id_tiempo IS NULL OR id_riesgo IS NULL OR id_sector IS NULL OR id_sucursal IS NULL"
    )[0]

    dups = hook.get_first(
        "SELECT COUNT(*) FROM ("
        "  SELECT id_tiempo, id_riesgo, id_sector, id_sucursal "
        "  FROM fact_creditos_mensual "
        "  GROUP BY id_tiempo, id_riesgo, id_sector, id_sucursal HAVING COUNT(*) > 1"
        ") t"
    )[0]

    print(f"MV: {mv_rows:,} registros")
    print(f"Fact: {fact_rows:,} registros")
    print(f"FKs nulas: {nulls}")
    print(f"Duplicados: {dups}")

    if nulls > 0:
        raise ValueError(f"Se encontraron {nulls} filas con FK nula")
    if dups > 0:
        raise ValueError(f"Se encontraron {dups} filas duplicadas")
    if fact_rows == 0:
        raise ValueError("fact_creditos_mensual esta vacia")

    print("Validacion exitosa")


refresh_mv = PythonOperator(
    task_id="refresh_mv",
    python_callable=refresh_mv,
    dag=dag_datamart,
)

dim_tiempo = PythonOperator(
    task_id="poblar_dim_tiempo",
    python_callable=poblar_dim_tiempo,
    dag=dag_datamart,
)

dim_riesgo = PythonOperator(
    task_id="poblar_dim_riesgo",
    python_callable=poblar_dim_riesgo,
    dag=dag_datamart,
)

dim_sector = PythonOperator(
    task_id="poblar_dim_sector",
    python_callable=poblar_dim_sector,
    dag=dag_datamart,
)

dim_sucursal = PythonOperator(
    task_id="poblar_dim_sucursal",
    python_callable=poblar_dim_sucursal,
    dag=dag_datamart,
)

poblar_fact = PythonOperator(
    task_id="poblar_fact",
    python_callable=poblar_fact,
    dag=dag_datamart,
)

validar = PythonOperator(
    task_id="validar_datamart",
    python_callable=validar_datamart,
    dag=dag_datamart,
)

refresh_mv >> [dim_tiempo, dim_riesgo, dim_sector, dim_sucursal] >> poblar_fact >> validar
