# predict.py
# Script de inferencia batch para generar predicciones multi-horizonte
# y escribirlas en la tabla fact_predicciones_mensual del datamart.
# Diseñado para ejecutarse periódicamente via cron (diario/semanal).

import os
import numpy as np
import pandas as pd
import joblib
import json
import logging
import tensorflow as tf
from datetime import timedelta
from sqlalchemy import create_engine, text
from sklearn.preprocessing import MinMaxScaler

# -------------------------------
# Configuración de logging
# -------------------------------
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------
# Conexión a base de datos
# -------------------------------
DB_CONFIG = {
    "host": "192.168.0.97",
    "port": "5432",
    "database": "analisis_db",
    "user": "usuario",
    "password": "mi_clave_segura",
}
connection_string = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)
engine = create_engine(connection_string)

# -------------------------------
# Rutas de artefactos del modelo
# -------------------------------
MODEL_PATH = "/app/modelos_cnn/best_model_multi_18m.h5"
SCALER_PATH = "/app/modelos_cnn/scaler_multi_18m.pkl"
CONFIG_PATH = "/app/modelos_cnn/config_18m.json"

# -------------------------------
# Query: mismos datos agregados que train.py pero sin límite de fecha superior
# -------------------------------
QUERY_DATOS = """
WITH datos_mensuales AS (
    SELECT 
        DATE_TRUNC('month', cp.fecha_credito) as mes,
        COALESCE(cp.codigo_riesgo, 'SIN_RIESGO') as riesgo,
        COALESCE(cp.act_economica_nvl1, 'SIN_SECTOR') as sector,
        cp.codigo_provincia,
        cp.codigo_sucursal,
        COUNT(*) as num_creditos,
        SUM(cp.monto_acreditado) as monto_total,
        AVG(cp.monto_acreditado) as monto_promedio,
        AVG(cp.tot_dias_mora) as dias_mora_promedio,
        AVG(cp.tot_num_moras) as num_moras_promedio,
        COUNT(CASE WHEN cp.tot_dias_mora > 90 THEN 1 END) as creditos_mora_90,
        COUNT(CASE WHEN cp.judicial = 'S' THEN 1 END) as creditos_judiciales,
        SUM(cp.gestion_cobro) as total_gestion_cobro,
        SUM(cp.costo_judicial) as total_costo_judicial,
        AVG(cp.tasa_interes) as tasa_interes_promedio,
        AVG(COALESCE(cp.saldo_capital, 0)) as saldo_promedio,
        COUNT(CASE WHEN cp.estado_cred IN ('C', 'L') THEN 1 END) as creditos_cerrados,
        COUNT(DISTINCT cp.codigo_socio) as num_clientes_unicos,
        EXTRACT(MONTH FROM cp.fecha_credito) as mes_del_ano,
        AVG(cp.num_cuotas) as plazo_promedio,
        STDDEV(cp.monto_acreditado) as desviacion_montos,
        AVG(EXTRACT(MONTH FROM AGE(CURRENT_DATE, cp.fecha_credito))) as antiguedad_promedio_meses
    FROM cabecera_prestamos cp
    WHERE cp.fecha_credito >= '2015-07-01' 
    GROUP BY DATE_TRUNC('month', cp.fecha_credito), cp.codigo_riesgo, cp.act_economica_nvl1, 
             cp.codigo_provincia, cp.codigo_sucursal, EXTRACT(MONTH FROM cp.fecha_credito)
),
datos_con_lag AS (
    SELECT 
        *,
        LAG(num_creditos, 1) OVER (
            PARTITION BY riesgo, sector 
            ORDER BY mes
        ) as num_creditos_mes_anterior,
        LAG(monto_total, 1) OVER (
            PARTITION BY riesgo, sector 
            ORDER BY mes
        ) as monto_mes_anterior
    FROM datos_mensuales
)
SELECT 
    mes,
    riesgo,
    sector,
    codigo_provincia,
    codigo_sucursal,
    num_creditos,
    monto_total,
    monto_promedio,
    dias_mora_promedio,
    num_moras_promedio,
    ROUND((creditos_mora_90::numeric / NULLIF(num_creditos, 0)) * 100, 2) as tasa_mora_90,
    ROUND((creditos_judiciales::numeric / NULLIF(num_creditos, 0)) * 100, 2) as tasa_judicial,
    ROUND((creditos_cerrados::numeric / NULLIF(num_creditos, 0)) * 100, 2) as tasa_cierre,
    total_gestion_cobro,
    total_costo_judicial,
    tasa_interes_promedio,
    saldo_promedio,
    creditos_cerrados,
    num_clientes_unicos,
    ROUND(num_creditos::numeric / NULLIF(num_clientes_unicos, 0), 2) as creditos_por_cliente,
    mes_del_ano,
    ROUND(plazo_promedio::numeric, 2) as plazo_promedio,
    ROUND(desviacion_montos::numeric, 2) as desviacion_montos,
    ROUND((desviacion_montos::numeric / NULLIF(monto_promedio, 0)) * 100, 2) as coef_variacion_montos,
    ROUND(antiguedad_promedio_meses::numeric, 2) as antiguedad_promedio_meses,
    num_creditos_mes_anterior,
    ROUND(((num_creditos::numeric - COALESCE(num_creditos_mes_anterior, num_creditos)) / 
           NULLIF(num_creditos_mes_anterior, 0)) * 100, 2) as tasa_crecimiento_creditos,
    monto_mes_anterior,
    ROUND(((monto_total::numeric - COALESCE(monto_mes_anterior, monto_total)) / 
           NULLIF(monto_mes_anterior, 0)) * 100, 2) as tasa_crecimiento_monto
FROM datos_con_lag
WHERE num_creditos >= 10
ORDER BY mes, riesgo, sector
"""


def cargar_artefactos():
    """Carga el modelo entrenado, scaler y configuración desde disco."""
    logger.info("Cargando artefactos del modelo...")
    modelo = tf.keras.models.load_model(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    logger.info(
        "Artefactos cargados: ventana=%d, horizonte=%d, features=%d",
        config["ventana_cnn"],
        config["max_horizonte"],
        len(config["features_numericas"]),
    )
    return modelo, scaler, config


def extraer_datos():
    """Extrae los datos agregados desde PostgreSQL."""
    logger.info("Extrayendo datos desde PostgreSQL...")
    df = pd.read_sql_query(QUERY_DATOS, engine)
    logger.info("Datos extraidos: %d registros", len(df))
    return df


def preprocesar(df):
    """Preprocesa los datos crudos: crea bloque_id, rellena nulos, features."""
    df["mes"] = pd.to_datetime(df["mes"])
    df["bloque_id"] = (
        df["riesgo"]
        + "_"
        + df["sector"]
        + "_"
        + df["codigo_sucursal"].astype(str)
    )
    df["tasa_crecimiento_creditos"] = df["tasa_crecimiento_creditos"].fillna(0)
    df["tasa_crecimiento_monto"] = df["tasa_crecimiento_monto"].fillna(0)
    df["num_creditos_mes_anterior"] = df["num_creditos_mes_anterior"].fillna(
        df["num_creditos"]
    )
    df["monto_mes_anterior"] = df["monto_mes_anterior"].fillna(df["monto_total"])
    df["desviacion_montos"] = df["desviacion_montos"].fillna(0)
    df["coef_variacion_montos"] = df["coef_variacion_montos"].fillna(0)
    return df


def generar_secuencia_inferencia(df_bloque, features, ventana):
    """
    Extrae la ÚLTIMA ventana de meses de un bloque para inferencia.
    Retorna un array de shape (1, ventana, n_features) o None si no hay datos suficientes.
    """
    df_bloque = df_bloque.sort_values("mes")
    if len(df_bloque) < ventana:
        return None, None

    ultimos = df_bloque[features].iloc[-ventana:].values
    ultimo_mes = df_bloque["mes"].iloc[-1]
    return ultimos[np.newaxis, :, :], ultimo_mes


def upsert_dimensiones(df):
    """Asegura que todos los bloques tengan sus dimensiones en el datamart."""
    with engine.connect() as conn:
        for riesgo in df["riesgo"].unique():
            conn.execute(
                text(
                    "INSERT INTO dim_riesgo (codigo_riesgo, descripcion) "
                    "VALUES (:cod, :desc) ON CONFLICT (codigo_riesgo) DO NOTHING"
                ),
                {"cod": str(riesgo), "desc": str(riesgo)},
            )
        for sector in df["sector"].unique():
            conn.execute(
                text(
                    "INSERT INTO dim_sector (codigo_sector, descripcion) "
                    "VALUES (:cod, :desc) ON CONFLICT (codigo_sector) DO NOTHING"
                ),
                {"cod": str(sector), "desc": str(sector)},
            )
        sucursales = df[["codigo_sucursal", "codigo_provincia"]].drop_duplicates()
        for _, row in sucursales.iterrows():
            conn.execute(
                text(
                    "INSERT INTO dim_sucursal (codigo_sucursal, codigo_provincia) "
                    "VALUES (:suc, :prov) "
                    "ON CONFLICT (codigo_sucursal, codigo_provincia) DO NOTHING"
                ),
                {
                    "suc": int(row["codigo_sucursal"]),
                    "prov": int(row["codigo_provincia"])
                    if pd.notna(row["codigo_provincia"])
                    else None,
                },
            )
        conn.commit()
    logger.info("Dimensiones actualizadas")


def obtener_ids_dimensiones():
    """Lee las tablas de dimensiones y retorna DataFrames con los IDs."""
    dim_riesgo = pd.read_sql_query(
        "SELECT id_riesgo, codigo_riesgo FROM dim_riesgo", engine
    )
    dim_sector = pd.read_sql_query(
        "SELECT id_sector, codigo_sector FROM dim_sector", engine
    )
    dim_sucursal = pd.read_sql_query(
        "SELECT id_sucursal, codigo_sucursal, codigo_provincia FROM dim_sucursal",
        engine,
    )
    return dim_riesgo, dim_sector, dim_sucursal


def guardar_predicciones(df_pred, dim_riesgo, dim_sector, dim_sucursal):
    """Resuelve FKs y escribe las predicciones en fact_predicciones_mensual."""
    if df_pred.empty:
        logger.warning("No hay predicciones para guardar")
        return

    df_out = df_pred.merge(
        dim_riesgo, left_on="riesgo", right_on="codigo_riesgo", how="left"
    )
    df_out = df_out.merge(
        dim_sector, left_on="sector", right_on="codigo_sector", how="left"
    )
    df_out = df_out.merge(
        dim_sucursal,
        left_on=["codigo_sucursal", "codigo_provincia"],
        right_on=["codigo_sucursal", "codigo_provincia"],
        how="left",
    )

    cols_necesarias = ["id_riesgo", "id_sector", "id_sucursal"]
    df_out = df_out.dropna(subset=cols_necesarias)

    insertados = 0
    with engine.connect() as conn:
        for _, row in df_out.iterrows():
            conn.execute(
                text(
                    "INSERT INTO fact_predicciones_mensual "
                    "(id_riesgo, id_sector, id_sucursal, bloque_id, "
                    "mes_base, mes_predicho, horizonte_meses, "
                    "prob_crisis, flag_crisis_predicha, fecha_prediccion) "
                    "VALUES (:idr, :ids, :idsu, :bloq, :mb, :mp, :h, "
                    ":prob, :flag, :fp) "
                    "ON CONFLICT (bloque_id, mes_predicho, fecha_prediccion) DO UPDATE SET "
                    "prob_crisis = EXCLUDED.prob_crisis, "
                    "flag_crisis_predicha = EXCLUDED.flag_crisis_predicha"
                ),
                {
                    "idr": int(row["id_riesgo"]),
                    "ids": int(row["id_sector"]),
                    "idsu": int(row["id_sucursal"]),
                    "bloq": row["bloque_id"],
                    "mb": row["mes_base"],
                    "mp": row["mes_predicho"],
                    "h": int(row["horizonte_meses"]),
                    "prob": float(row["prob_crisis"]),
                    "flag": int(row["flag_crisis_predicha"]),
                    "fp": row["fecha_prediccion"],
                },
            )
            insertados += 1
        conn.commit()

    logger.info("Predicciones guardadas: %d registros en fact_predicciones_mensual", insertados)


def main():
    # 1. Cargar artefactos del modelo
    modelo, scaler, config = cargar_artefactos()
    features = config["features_numericas"]
    ventana = config["ventana_cnn"]
    max_horizonte = config["max_horizonte"]

    # 2. Extraer y preprocesar datos
    df = extraer_datos()
    if df is None or len(df) == 0:
        logger.error("No se pudieron extraer datos. Abortando.")
        return

    df = preprocesar(df)

    # 3. Asegurar dimensiones en el datamart
    upsert_dimensiones(df)

    # 4. Generar predicciones bloque por bloque
    registros = []
    bloques = df["bloque_id"].unique()
    fecha_pred = pd.Timestamp.now()

    for bloque_id in bloques:
        df_bloque = df[df["bloque_id"] == bloque_id]

        # Extraer metadatos del bloque
        riesgo = df_bloque["riesgo"].iloc[0]
        sector = df_bloque["sector"].iloc[0]
        codigo_sucursal = df_bloque["codigo_sucursal"].iloc[0]
        codigo_provincia = df_bloque["codigo_provincia"].iloc[0]

        # Generar secuencia de inferencia (últimos N meses)
        X_seq, ultimo_mes = generar_secuencia_inferencia(
            df_bloque, features, ventana
        )
        if X_seq is None:
            logger.debug(
                "Bloque %s: datos insuficientes (< %d meses), omitido",
                bloque_id,
                ventana,
            )
            continue

        # Escalar con el scaler del entrenamiento
        n_samples, n_steps, n_feats = X_seq.shape
        X_flat = X_seq.reshape(-1, n_feats)
        X_scaled = scaler.transform(X_flat).reshape(n_samples, n_steps, n_feats)

        # Predecir
        y_pred_proba = modelo.predict(X_scaled, verbose=0)

        # Construir registros: uno por horizonte
        for h in range(max_horizonte):
            prob = float(y_pred_proba[h].flatten()[0])
            mes_pred = ultimo_mes + pd.DateOffset(months=h + 1)
            registros.append(
                {
                    "riesgo": riesgo,
                    "sector": sector,
                    "codigo_sucursal": codigo_sucursal,
                    "codigo_provincia": codigo_provincia,
                    "bloque_id": bloque_id,
                    "mes_base": ultimo_mes.date(),
                    "mes_predicho": mes_pred.date(),
                    "horizonte_meses": h + 1,
                    "prob_crisis": prob,
                    "flag_crisis_predicha": 1 if prob > 0.5 else 0,
                    "fecha_prediccion": fecha_pred,
                }
            )

        logger.debug(
            "Bloque %s: predicciones generadas para %d horizontes",
            bloque_id,
            max_horizonte,
        )

    if not registros:
        logger.warning("Ningún bloque generó predicciones")
        return

    df_pred = pd.DataFrame(registros)
    logger.info(
        "Predicciones generadas: %d bloques x %d horizontes = %d registros",
        len(df_pred) // max_horizonte,
        max_horizonte,
        len(df_pred),
    )

    # 5. Estadísticas rápidas
    n_alerta = (df_pred["flag_crisis_predicha"] == 1).sum()
    logger.info(
        "Alertas de crisis (prob > 0.5): %d de %d (%.1f%%)",
        n_alerta,
        len(df_pred),
        100 * n_alerta / len(df_pred),
    )

    # 6. Guardar en el datamart
    dim_riesgo, dim_sector, dim_sucursal = obtener_ids_dimensiones()
    guardar_predicciones(df_pred, dim_riesgo, dim_sector, dim_sucursal)

    logger.info("Predict.py finalizado exitosamente")


if __name__ == "__main__":
    main()
