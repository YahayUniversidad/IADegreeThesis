##
## @file pipeline.py
##
## Pipeline de predicciones LightGBM multi-horizonte.
## Genera predicciones con 18 modelos LightGBM y crea/actualiza
## la tabla fact_predicciones en PostgreSQL.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import os
from datetime import datetime

import lightgbm as lgb
import numpy as np
import pandas as pd
import psycopg2
from src.ts_sql import (
    SQL_CREA_FACT_PREDICCIONES,
    SQL_INSERT_PREDICCIONES,
    SQL_REFRESH_DIM_RIESGO,
    SQL_REFRESH_DIM_SECTOR,
    SQL_REFRESH_DIM_SUCURSAL,
    SQL_REFRESH_DIM_TIEMPO,
)

MAX_HORIZONTE = 18
VENTANA_LGBM = 6


def _crear_secuencias_prediccion(df, bloque_id, features, ventana):
    """Genera secuencias estadisticas para prediccion (sin targets).

    Args:
        df: DataFrame con los datos.
        bloque_id: Identificador del bloque.
        features: Lista de features numericas base.
        ventana: Tamano de la ventana temporal.

    Returns:
        tuple: (X_seq, meses, df_bloque) o (None, None, None).
    """
    df_b = df[df["bloque_id"] == bloque_id].sort_values("mes")
    if len(df_b) < ventana:
        return None, None, None

    X_seq, meses = [], []
    for i in range(len(df_b) - ventana + 1):
        hist = df_b[features].iloc[i : i + ventana]
        feats = []
        for col in features:
            v = hist[col].values
            feats.extend([
                np.mean(v),
                np.std(v),
                np.min(v),
                np.max(v),
                np.median(v),
                v[-1],
                v[-1] - v[0],
            ])
        X_seq.append(feats)
        meses.append(df_b["mes"].iloc[i + ventana - 1])
    return np.array(X_seq), meses, df_b


def _refrescar_dims(conn, df):
    """Actualiza dimensiones desde el CSV.

    Args:
        conn: Conexion psycopg2.
        df: DataFrame con los datos.
    """
    cur = conn.cursor()

    fechas_csv = df["mes"].sort_values().unique()
    for fecha in fechas_csv:
        cur.execute(
            SQL_REFRESH_DIM_TIEMPO,
            (fecha, fecha.year, (fecha.month - 1) // 3 + 1, fecha.month, fecha.strftime("%B")),
        )

    for riesgo in df["riesgo"].unique():
        cur.execute(SQL_REFRESH_DIM_RIESGO, (str(riesgo), str(riesgo)))

    for sector in df["sector"].unique():
        cur.execute(SQL_REFRESH_DIM_SECTOR, (str(sector), str(sector)))

    for suc in df["codigo_sucursal"].unique():
        cur.execute(SQL_REFRESH_DIM_SUCURSAL, (int(suc),))

    cur.close()
    print(
        f"Dimensiones actualizadas: {len(fechas_csv)} fechas, "
        f"{df['riesgo'].nunique()} riesgos, {df['sector'].nunique()} sectores, "
        f"{df['codigo_sucursal'].nunique()} sucursales"
    )


def _generar_predicciones(df, modelos, features, ventana, max_horizonte):
    """Genera predicciones para todos los bloques.

    Args:
        df: DataFrame con los datos.
        modelos: Lista de 18 modelos LightGBM.
        features: Lista de features numericas.
        ventana: Tamano de la ventana.
        max_horizonte: Numero de horizontes.

    Returns:
        pd.DataFrame: DataFrame con las predicciones.
    """
    predicciones = []

    for bloque in df["bloque_id"].unique():
        info = df[df["bloque_id"] == bloque]
        riesgo = info["riesgo"].iloc[0]
        sector = info["sector"].iloc[0]
        sucursal = int(info["codigo_sucursal"].iloc[0])

        X_seq, meses_seq, _ = _crear_secuencias_prediccion(df, bloque, features, ventana)
        if X_seq is None or len(X_seq) == 0:
            continue

        for idx in range(len(X_seq)):
            row = {
                "bloque_id": bloque,
                "riesgo": riesgo,
                "sector": sector,
                "codigo_sucursal": sucursal,
                "mes_prediccion": meses_seq[idx], #type: ignore
            }
            x_in = X_seq[idx : idx + 1]
            for h in range(max_horizonte):
                p = float(modelos[h].predict(x_in)[0])
                row[f"prob_h{h + 1}"] = round(p, 6)
                row[f"pred_h{h + 1}"] = int(p > 0.5)
            predicciones.append(row)

    df_pred = pd.DataFrame(predicciones)

    prob_cols = [f"prob_h{i + 1}" for i in range(max_horizonte)]
    pred_cols = [f"pred_h{i + 1}" for i in range(max_horizonte)]

    df_pred["prob_media"] = df_pred[prob_cols].mean(axis=1).round(6)
    df_pred["pred_media"] = (df_pred["prob_media"] > 0.5).astype(int)
    df_pred["crisis_count"] = df_pred[pred_cols].sum(axis=1).astype(int)
    df_pred["fecha_ejecucion"] = datetime.now()

    return df_pred


def _crear_fact_predicciones(conn):
    """Crea la tabla fact_predicciones (DROP + CREATE).

    Args:
        conn: Conexion psycopg2.
    """
    cur = conn.cursor()
    cur.execute(SQL_CREA_FACT_PREDICCIONES)
    cur.close()
    print("Tabla fact_predicciones creada.")


def _poblar_fact_predicciones(conn, df_pred, max_horizonte):
    """Inserta predicciones en fact_predicciones (UPSERT).

    Args:
        conn: Conexion psycopg2.
        df_pred: DataFrame con las predicciones.
        max_horizonte: Numero de horizontes.
    """
    cur = conn.cursor()
    inserted = 0

    for _, row in df_pred.iterrows():
        riesgo_s = str(row["riesgo"])
        sector_s = str(row["sector"])
        sucursal_i = int(row["codigo_sucursal"])

        params = (
            row["mes_prediccion"],
            riesgo_s,
            sector_s,
            sucursal_i,
            row["bloque_id"],
        )
        for h in range(1, max_horizonte + 1):
            params += (row[f"prob_h{h}"],)
        for h in range(1, max_horizonte + 1):
            params += (int(row[f"pred_h{h}"]),)
        params += (
            row["prob_media"],
            int(row["pred_media"]),
            int(row["crisis_count"]),
            row["fecha_ejecucion"],
        )

        cur.execute(SQL_INSERT_PREDICCIONES, params)
        inserted += cur.rowcount

    conn.commit()
    cur.close()
    print(f"Filas insertadas/actualizadas: {inserted:,}")


def _validar_predicciones(conn):
    """Valida la tabla fact_predicciones.

    Args:
        conn: Conexion psycopg2.
    """
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM fact_predicciones")
    total = cur.fetchone()[0]
    print(f"Total registros: {total:,}")

    cur.execute(
        "SELECT pred_media, COUNT(*) FROM fact_predicciones "
        "GROUP BY pred_media ORDER BY pred_media"
    )
    for r in cur.fetchall():
        label = "Sin crisis" if r[0] == 0 else "Crisis"
        print(f"  {label}: {r[1]:,}")

    cur.close()


def ejecutar_predicciones(
    string_conexion,
    path_trabajo
):
    """Entry point: ejecuta el pipeline completo de predicciones.

    Args:
        string_conexion: Cadena de conexion a PostgreSQL.
        path_trabajo: Directorio base para artefactos.
    """
    path_datasets = f"{path_trabajo}/lotes/datasets/datos_preprocesados.csv"
    path_lgbm = f"{path_trabajo}/modelos_lightgbm"
    path_predicciones = f"{path_trabajo}/predicciones"
    os.makedirs(path_predicciones, exist_ok=True)

    print("Cargando datos...")
    df = pd.read_csv(path_datasets)
    df["mes"] = pd.to_datetime(df["mes"])

    print("Cargando configuracion LightGBM...")
    with open(os.path.join(path_lgbm, "config_lgbm_18m.json")) as f:
        config = json.load(f)
    features_numericas = config["features_numericas"]

    print("Cargando modelos LightGBM...")
    modelos = []
    for h in range(1, MAX_HORIZONTE + 1):
        modelos.append(lgb.Booster(model_file=os.path.join(path_lgbm, f"modelo_lgbm_h{h}.txt")))
    print(f"Modelos cargados: {len(modelos)}")

    conn = psycopg2.connect(string_conexion)
    conn.autocommit = True
    try:
        print("Refrescando dimensiones...")
        _refrescar_dims(conn, df)

        print("Generando predicciones...")
        df_pred = _generar_predicciones(df, modelos, features_numericas, VENTANA_LGBM, MAX_HORIZONTE)
        print(f"Predicciones: {len(df_pred):,}")

        print("Creando fact_predicciones...")
        _crear_fact_predicciones(conn)

        print("Poblando fact_predicciones...")
        _poblar_fact_predicciones(conn, df_pred, MAX_HORIZONTE)

        print("Validando...")
        _validar_predicciones(conn)

        csv_path = os.path.join(path_predicciones, "predicciones.csv")
        df_pred.to_csv(csv_path, index=False)
        print(f"CSV guardado: {csv_path}")
    except Exception as e:
        print(f"Error en pipeline de predicciones: {e}")
        raise RuntimeError(f"Error en pipeline de predicciones: {e}") from e

    finally:
        conn.close()

    print("Predicciones completadas.")
