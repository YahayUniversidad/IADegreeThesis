##
## @file pipeline.py
##
## Pipeline de predicciones multi-modelo.
## Genera predicciones historicas (backtest) y futuras (18 meses)
## usando el modelo seleccionado desde MLflow.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import os
import tempfile
from datetime import datetime

import lightgbm as lgb
import mlflow
import numpy as np
import pandas as pd
import psycopg2
import src.ts_predicciones as ts_predi
from src.ts_sql import (
    SCRIPT_CREA_FACT_PREDICCIONES,
    SQL_INSERT_PREDICCIONES,
    SQL_REFRESH_DIM_RIESGO,
    SQL_REFRESH_DIM_SECTOR,
    SQL_REFRESH_DIM_SUCURSAL,
    SQL_REFRESH_DIM_TIEMPO,
    SQL_REFRESH_MV_PREDICCIONES,
    ejeucta_script_generico,
)


def _cargar_modelo_mlflow(mlflow_uri, mlflow_experiment_id) -> tuple:
    """Carga el modelo desde MLflow segun el experimento.

    Args:
        mlflow_uri: URI de MLflow tracking.
        mlflow_experiment_id: ID del experimento MLflow.

    Returns:
        tuple: (tipo_modelo, modelos, config)
            tipo_modelo: 'lightgbm', 'cnn', o 'mlp'
            modelos: lista de modelos (18 para LGBM, 1 para CNN/MLP)
            config: dict con features_numericas y otros metadatos
    """
    mlflow.set_tracking_uri(mlflow_uri)

    runs = mlflow.search_runs(
        experiment_ids=[mlflow_experiment_id],
        order_by=["metrics.auc_roc DESC"],
        max_results=1,
    )
    if runs.empty: # type: ignore
        raise ValueError(f"No hay runs en el experimento '{mlflow_experiment_id}'")

    run_id = runs.iloc[0]["run_id"] # type: ignore
    print(f"Mejor run: {run_id}")

    exp_id = str(runs.iloc[0].get("experiment_id", mlflow_experiment_id)) # type: ignore
    experiment = mlflow.get_experiment(exp_id)
    if experiment is None:
        experiment = mlflow.get_experiment_by_name(str(mlflow_experiment_id))
    experiment_name = experiment.name if experiment else str(mlflow_experiment_id)
    print(f"Experimento: {experiment_name}")

    # Detectar tipo de modelo por nombre del experimento
    if "lightgbm" in experiment_name.lower():
        tipo = "lightgbm"
    elif "cnn" in experiment_name.lower():
        tipo = "cnn"
    elif "mlp" in experiment_name.lower():
        tipo = "mlp"
    else:
        tipo = "lightgbm"

    with tempfile.TemporaryDirectory() as tmpdir:
        # Descargar artefactos del run
        client = mlflow.MlflowClient(mlflow_uri)
        artifacts = client.list_artifacts(run_id)
        for art in artifacts:
            if art.path.endswith(".json") and "config" in art.path:
                client.download_artifacts(run_id, art.path, tmpdir)
            elif tipo == "lightgbm" and art.path.startswith("modelo_h"):
                client.download_artifacts(run_id, art.path, tmpdir)
            elif tipo in ("cnn", "mlp") and art.path.endswith((".keras", ".h5")):
                client.download_artifacts(run_id, art.path, tmpdir)

        if tipo == "lightgbm":
            modelos = []
            for h in range(1, ts_predi.MAX_HORIZONTE + 1):
                model_path = os.path.join(tmpdir, f"modelo_h{h}", "model.lgb")
                if not os.path.exists(model_path):
                    # Buscar en subdirectorios
                    for root, dirs, files in os.walk(tmpdir):
                        for f in files:
                            if f.endswith(".txt") or f.endswith(".lgb"):
                                model_path = os.path.join(root, f)
                                break
                modelos.append(lgb.Booster(model_file=model_path))
            print(f"LightGBM: {len(modelos)} modelos cargados")

            # Cargar config
            config_path = None
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    if f.endswith(".json") and "config" in f:
                        config_path = os.path.join(root, f)
                        break
            if config_path:
                with open(config_path) as f:
                    config = json.load(f)
            else:
                config = {"features_numericas": []}

        elif tipo in ("cnn", "mlp"):
            import tensorflow as tf

            model_path = None
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    if f.endswith(".keras") or f.endswith(".h5"):
                        model_path = os.path.join(root, f)
                        break
            modelos = [tf.keras.models.load_model(model_path)]
            print(f"{tipo.upper()}: modelo cargado desde {model_path}")

            config_path = None
            for root, dirs, files in os.walk(tmpdir):
                for f in files:
                    if f.endswith(".json") and "config" in f:
                        config_path = os.path.join(root, f)
                        break
            if config_path:
                with open(config_path) as f:
                    config = json.load(f)
            else:
                config = {"features_numericas": []}

    return tipo, modelos, config


def _cargar_modelo_local(path_trabajo):
    """Carga modelo desde disco local (fallback sin MLflow).

    Carga modelos LightGBM desde path_trabajo/modelos_lightgbm y config_lgbm_18m.json.

    Returns:
        tuple: (tipo_modelo, modelos, config)
    """
    path_lgbm = f"{path_trabajo}/modelos_lightgbm"
    config_path = os.path.join(path_lgbm, "config_lgbm_18m.json")

    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
        features = config.get("features_numericas", [])

        print(f"Cargando modelos LightGBM desde {path_lgbm} con {len(features)} features")

        modelos = []
        for h in range(1, ts_predi.MAX_HORIZONTE + 1):
            for ext in [".txt", ".lgb"]:
                model_path = os.path.join(path_lgbm, f"modelo_lgbm_h{h}{ext}")
                if os.path.exists(model_path):
                    modelos.append(lgb.Booster(model_file=model_path))
                    break
        if modelos:
            return "lightgbm", modelos, config

    raise FileNotFoundError(
        f"No se encontro modelo en {path_trabajo}. "
        "Configure mlflow_uri y mlflow_experiment en el DAG."
    )


def _crear_secuencias_prediccion(df, bloque_id, features, ventana):
    """Genera secuencias estadisticas para prediccion (sin targets).

    Args:
        df: DataFrame con datos historicos.
        bloque_id: ID del bloque a procesar.
        features: Lista de nombres de columnas numericas.
        ventana: Numero de meses a usar para generar features.

    Returns:
        tuple: (X_seq, meses, df_b) donde X_seq es un array de secuencias,
               meses es la lista de meses correspondientes, y df_b es el
               DataFrame filtrado por bloque_id.
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
            feats.extend(
                [
                    np.mean(v),
                    np.std(v),
                    np.min(v),
                    np.max(v),
                    np.median(v),
                    v[-1],
                    v[-1] - v[0],
                ]
            )
        X_seq.append(feats)
        meses.append(df_b["mes"].iloc[i + ventana - 1])
    return np.array(X_seq), meses, df_b


def _predecir_con_modelo(modelo, tipo, x_in):
    """Ejecuta prediccion con el modelo segun su tipo.

    Args:
        modelo: Modelo entrenado (LightGBM o Keras).
        tipo: Tipo de modelo ('lightgbm', 'cnn', 'mlp').
        x_in: Array de entrada para prediccion.

    Returns:
        float: Prediccion generada por el modelo.
    """
    if tipo == "lightgbm":
        return float(modelo.predict(x_in)[0])
    elif tipo in ("cnn", "mlp"):
        pred = modelo.predict(x_in, verbose=0)
        if isinstance(pred, list):
            return float(pred[0][0])
        return float(pred[0][0])
    return 0.0


def _refrescar_dims(conn, df):
    """Actualiza dimensiones desde el DataFrame CSV.

    Args:
        conn: Conexion a la base de datos.
        df: DataFrame con datos historicos.

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
    conn.commit()
    cur.close()
    print(
        f"Dimensiones actualizadas: {len(fechas_csv)} fechas, "
        f"{df['riesgo'].nunique()} riesgos, {df['sector'].nunique()} sectores, "
        f"{df['codigo_sucursal'].nunique()} sucursales"
    )


def _refrescar_dims_futuros(conn, fechas_futuras):
    """Inserta fechas futuras en dim_tiempo.

    Es importante optener las fechas futuras pues es parte principal de la prediccion y se requiere
    para poblar fact_predicciones.

    Args:
        conn: Conexion a la base de datos.
        fechas_futuras: Lista de fechas futuras a insertar.

    """
    cur = conn.cursor()
    for fecha in fechas_futuras:
        cur.execute(
            SQL_REFRESH_DIM_TIEMPO,
            (fecha, fecha.year, (fecha.month - 1) // 3 + 1, fecha.month, fecha.strftime("%B")),
        )
    conn.commit()
    cur.close()
    print(f"Dimensiones futuras: {len(fechas_futuras)} meses insertados")


def _generar_predicciones_historicas(
    df, modelos, tipo, features, ventana, max_horizonte
) -> pd.DataFrame:
    """Genera predicciones historicas (backtest) para todos los bloques.

    Estas pueden ser usadas para evaluar el desempeño del modelo y generar métricas de backtest.

    Args:
        df: DataFrame con datos historicos.
        modelos: Lista de modelos entrenados.
        tipo: Tipo de modelo ('lightgbm', 'cnn', 'mlp').
        features: Lista de nombres de columnas numericas.
        ventana: Numero de meses a usar para generar features.
        max_horizonte: Numero de meses a predecir (1 a 18).

    Returns:
        DataFrame con predicciones historicas agregadas.
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
                "mes_prediccion": meses_seq[idx],  # type: ignore
                "tipo": "historico",
            }
            x_in = X_seq[idx : idx + 1]
            for h in range(max_horizonte):
                if tipo == "lightgbm":
                    p = _predecir_con_modelo(modelos[h], tipo, x_in)
                else:
                    pred = modelos[0].predict(x_in, verbose=0)
                    p = float(pred[h][0]) if isinstance(pred, list) else float(pred[0][h])
                row[f"prob_h{h + 1}"] = round(p, 6)
                row[f"pred_h{h + 1}"] = int(p > 0.5)
            predicciones.append(row)

    return _calcular_agregados(predicciones)


def _generar_predicciones_futuras(df, modelos, tipo, features, ventana, max_horizonte):
    """Genera predicciones futuras: 18 meses desde la ultima fecha disponible.

    Cada fila tiene mes_prediccion = fecha futura real (no la fecha de referencia).
    Esto permite que cada predicción se asocie al mes correcto en dim_tiempo.

    Args:
        df: DataFrame con datos historicos.
        modelos: Lista de modelos entrenados.
        tipo: Tipo de modelo ('lightgbm', 'cnn', 'mlp').
        features: Lista de nombres de columnas numericas.
        ventana: Numero de meses a usar para generar features.
        max_horizonte: Numero de meses a predecir (1 a 18).

    Returns:
        tuple: (df_predicciones, fechas_futuras)
            df_predicciones: DataFrame con predicciones futuras.
            fechas_futuras: Lista de fechas futuras generadas.
    """
    predicciones = []
    fechas_futuras = set()

    for bloque in df["bloque_id"].unique():
        info = df[df["bloque_id"] == bloque].sort_values("mes")
        if len(info) < ventana:
            continue

        riesgo = info["riesgo"].iloc[0]
        sector = info["sector"].iloc[0]
        sucursal = int(info["codigo_sucursal"].iloc[0])
        ultimo_mes = info["mes"].iloc[-1]

        # Tomar ultima ventana
        ultima_ventana = info[features].iloc[-ventana:]
        feats = []
        for col in features:
            v = ultima_ventana[col].values
            feats.extend(
                [
                    np.mean(v),
                    np.std(v),
                    np.min(v),
                    np.max(v),
                    np.median(v),
                    v[-1],
                    v[-1] - v[0],
                ]
            )
        x_in = np.array([feats])

        # Una fila POR cada horizonte futuro
        for h in range(1, max_horizonte + 1):
            fecha_futura = ultimo_mes + pd.DateOffset(months=h)
            fechas_futuras.add(fecha_futura)

            if tipo == "lightgbm":
                p = _predecir_con_modelo(modelos[h - 1], tipo, x_in)
            else:
                pred = modelos[0].predict(x_in, verbose=0)
                p = float(pred[h - 1][0]) if isinstance(pred, list) else float(pred[0][h - 1])

            row = {
                "bloque_id": bloque,
                "riesgo": riesgo,
                "sector": sector,
                "codigo_sucursal": sucursal,
                "mes_prediccion": fecha_futura,  # Fecha futura REAL
                "tipo": "futuro",
            }
            # Solo el horizonte correspondiente tiene valor, los demas son None
            for hh in range(1, max_horizonte + 1):
                if hh == h:
                    row[f"prob_h{hh}"] = round(p, 6)
                    row[f"pred_h{hh}"] = int(p > 0.5)
                else:
                    row[f"prob_h{hh}"] = None
                    row[f"pred_h{hh}"] = None

            predicciones.append(row)

    return _calcular_agregados(predicciones), sorted(fechas_futuras)


def _calcular_agregados(predicciones):
    """Calcula prob_media, pred_media, crisis_count."""
    if not predicciones:
        return pd.DataFrame()

    df_pred = pd.DataFrame(predicciones)
    prob_cols = [f"prob_h{i + 1}" for i in range(ts_predi.MAX_HORIZONTE)]
    pred_cols = [f"pred_h{i + 1}" for i in range(ts_predi.MAX_HORIZONTE)]

    df_pred["prob_media"] = df_pred[prob_cols].apply(
        lambda row: round(row.dropna().mean(), 6) if row.dropna().any() else 0.0, axis=1
    )
    df_pred["pred_media"] = (df_pred["prob_media"] > 0.5).astype(int)
    df_pred["crisis_count"] = df_pred[pred_cols].apply(
        lambda row: int(row.dropna().sum()) if row.dropna().any() else 0, axis=1
    )
    df_pred["fecha_ejecucion"] = datetime.now()

    return df_pred

def _poblar_fact_predicciones(conn, df_pred, max_horizonte):
    """Inserta predicciones en fact_predicciones (UPSERT)."""
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
            val = row[f"prob_h{h}"]
            params += (float(val) if val is not None and not pd.isna(val) else None,)
        for h in range(1, max_horizonte + 1):
            val = row[f"pred_h{h}"]
            params += (int(val) if val is not None and not pd.isna(val) else None,)
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
    """Valida la tabla fact_predicciones."""
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM fact_predicciones")
    total = cur.fetchone()[0]
    print(f"Total registros: {total:,}")

    cur.execute(
        "SELECT pred_media, COUNT(*) FROM fact_predicciones GROUP BY pred_media ORDER BY pred_media"
    )
    for r in cur.fetchall():
        label = "Sin crisis" if r[0] == 0 else "Crisis"
        print(f"  {label}: {r[1]:,}")

    # Contar predicciones futuras
    cur.execute(
        "SELECT COUNT(DISTINCT bloque_id) FROM fact_predicciones fp "
        "JOIN dim_tiempo dt ON fp.id_tiempo = dt.id_tiempo "
        "WHERE dt.mes > (SELECT MAX(mes) FROM dim_tiempo WHERE mes < '2026-01-01')"
    )
    # Simple count of future rows
    cur.execute("SELECT COUNT(*) FROM fact_predicciones")    
    print (f"Predicciones Validadas: {cur.fetchone()[0]:,}")
    cur.close()


def ejecutar_predicciones(
    string_conexion,
    path_trabajo,
    mlflow_uri=None,
    mlflow_experiment_id=None,
):
    """Entry point: ejecuta el pipeline completo de predicciones.

    Args:
        string_conexion: Cadena de conexion a PostgreSQL.
        path_trabajo: Directorio base para artefactos.
        mlflow_uri: URI de MLflow tracking.
        mlflow_experiment_id: ID del experimento MLflow.
    """
    path_predicciones = f"{path_trabajo}/predicciones"
    os.makedirs(path_predicciones, exist_ok=True)

    # 1. Cargar datos
    path_datasets = f"{path_trabajo}/lotes/datasets/datos_preprocesados.csv"
    print("Cargando datos...")
    df = pd.read_csv(path_datasets)
    df["mes"] = pd.to_datetime(df["mes"])

    # 2. Cargar modelo desde MLflow o disco local
    if mlflow_uri and mlflow_experiment_id:
        print(f"Cargando modelo desde MLflow: {mlflow_experiment_id}")
        tipo, modelos, config = _cargar_modelo_mlflow(mlflow_uri, mlflow_experiment_id)
    else:
        print("Cargando modelo desde disco local...")
        tipo, modelos, config = _cargar_modelo_local(path_trabajo)

    features_numericas = config.get("features_numericas", [])
    if not features_numericas:
        raise ValueError("No se encontraron features_numericas en la config del modelo")

    print(f"Tipo: {tipo}, Modelos: {len(modelos)}, Features: {len(features_numericas)}")

    conn = psycopg2.connect(string_conexion)
    conn.autocommit = True
    try:
        # 3. Refrescar dimensiones historicas
        print("Refrescando dimensiones historicas...")
        _refrescar_dims(conn, df)

        # 4. Generar predicciones historicas (backtest)
        print("Generando predicciones historicas...")
        df_hist = _generar_predicciones_historicas(
            df,
            modelos,
            tipo,
            features_numericas,
            ts_predi.VENTANA,
            ts_predi.MAX_HORIZONTE,
        )
        print(f"Predicciones historicas: {len(df_hist):,}")

        # 5. Generar predicciones futuras
        print("Generando predicciones futuras...")
        df_fut, fechas_futuras = _generar_predicciones_futuras(
            df,
            modelos,
            tipo,
            features_numericas,
            ts_predi.VENTANA,
            ts_predi.MAX_HORIZONTE,
        )
        print(f"Predicciones futuras: {len(df_fut):,}, Fechas: {len(fechas_futuras)}")

        # 6. Insertar fechas futuras en dim_tiempo
        if fechas_futuras:
            print("Insertando fechas futuras en dim_tiempo...")
            _refrescar_dims_futuros(conn, fechas_futuras)

        # 7. Crear tabla y poblar
        print("Creando fact_predicciones...")
        ejeucta_script_generico(string_conexion, SCRIPT_CREA_FACT_PREDICCIONES, "fact_predicciones")
        
        # Combinar historico + futuro
        df_total = pd.concat([df_hist, df_fut], ignore_index=True)

        print("Poblando fact_predicciones...")
        _poblar_fact_predicciones(conn, df_total, ts_predi.MAX_HORIZONTE)

        # 8. Validar
        _validar_predicciones(conn)

        # 9. Refrescar MV de predicciones
        print("Refrescando mv_predicciones...")
        cur = conn.cursor()
        cur.execute(SQL_REFRESH_MV_PREDICCIONES)
        conn.commit()
        cur.close()
        print("mv_predicciones refrescada.")

        # 10. Guardar CSV
        csv_path = os.path.join(path_predicciones, "predicciones.csv")
        df_total.to_csv(csv_path, index=False)
        print(f"CSV guardado: {csv_path}")

    except Exception as e:
        print(f"Error en pipeline de predicciones: {e}")
        raise RuntimeError(f"Error en pipeline de predicciones: {e}") from e

    finally:
        conn.close()

    print("Predicciones completadas.")
