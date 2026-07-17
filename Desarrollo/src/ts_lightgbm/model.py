##
## @file model.py
##
## Lógica de entrenamiento de modelos LightGBM multi-horizonte.
## Contiene funciones para preprocesamiento, creación de secuencias,
## entrenamiento y evaluación de 18 modelos independientes.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import os

import lightgbm as lgb
import numpy as np
import pandas as pd
import src.ts_lightgbm as ts_lgbm
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

##from sklearn.preprocessing import MinMaxScaler


def preprocesar_datos(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Preprocesa los datos para LightGBM.

    Args:
        df: DataFrame con los datos originales.

    Returns:
        tuple: DataFrame preprocesado y lista de features numéricas.
    """
    df_features = df.copy()
    df_features["mes"] = pd.to_datetime(df_features["mes"])

    features_numericas = [
        "num_creditos",
        "monto_total",
        "monto_promedio",
        "plazo_promedio",
        "tasa_interes_promedio",
        "saldo_promedio",
        "total_costo_judicial",
        "total_gestion_cobro",
        "total_notificaciones",
        "tot_dias_mora_promedio",
        "tot_num_moras_promedio",
        "mora_promedio",
        "creditos_judiciales",
        "creditos_cerrados",
        "tasa_judicial",
        "tasa_cierre",
        "tasa_mora_90",
        "creditos_por_cliente",
        "coef_variacion_montos",
        "tasa_crecimiento_creditos",
        "tasa_crecimiento_monto",
    ]

    features_existentes = [f for f in features_numericas if f in df_features.columns]
    df_features = df_features.sort_values(["bloque_id", "mes"])

    return df_features, features_existentes


def crear_secuencias_lgbm(
    df: pd.DataFrame,
    bloque_id: str,
    features: list[str],
    ventana: int,
    max_horizonte: int,
) -> tuple[np.ndarray, np.ndarray, list]:
    """Genera secuencias temporales con features estadísticas para LightGBM.

    Para cada mes, crea 7 estadísticas (mean, std, min, max, median, last, trend)
    por cada feature base, resultando en 7 × len(features) features.

    Args:
        df: DataFrame con los datos.
        bloque_id: Identificador del bloque.
        features: Lista de features numéricas base.
        ventana: Tamaño de la ventana temporal.
        max_horizonte: Horizonte máximo de predicción.

    Returns:
        tuple: X (secuencias), y (targets), fechas_prediccion.
    """
    df_bloque = df[df["bloque_id"] == bloque_id].sort_values("mes")

    if len(df_bloque) < ventana + max_horizonte:
        return None, None, None  # type: ignore

    X_sequences = []
    y_sequences = []
    meses_target = []

    for i in range(len(df_bloque) - ventana - max_horizonte + 1):
        historial = df_bloque[features].iloc[i : i + ventana]

        features_seq = []
        for col in features:
            valores = historial[col].values
            features_seq.extend([
                np.mean(valores),
                np.std(valores),
                np.min(valores),
                np.max(valores),
                np.median(valores),
                valores[-1],
                valores[-1] - valores[0],
            ])

        y_seq = []
        for h in range(1, max_horizonte + 1):
            if i + ventana + h - 1 < len(df_bloque):
                y_val = df_bloque["crisis_flag"].iloc[i + ventana + h - 1]
                y_seq.append(y_val)
            else:
                y_seq.append(0)

        X_sequences.append(features_seq)
        y_sequences.append(y_seq)
        meses_target.append(df_bloque["mes"].iloc[i + ventana - 1])

    return np.array(X_sequences), np.array(y_sequences), meses_target


def generar_secuencias(df: pd.DataFrame, features_numericas: list[str]):
    """Genera secuencias para todos los bloques.

    Args:
        df: DataFrame preprocesado.
        features_numericas: Lista de features numéricas.

    Returns:
        tuple: X, y, fechas, bloques_validos, feature_names.
    """
    X_all, y_all, fechas_all, bloques_validos = [], [], [], []

    for bloque in df["bloque_id"].unique():
        X_seq, y_seq, fechas_seq = crear_secuencias_lgbm(
            df, bloque, features_numericas,
            ts_lgbm.VENTANA_LGBM, ts_lgbm.MAX_HORIZONTE,
        )
        if X_seq is not None and len(X_seq) > 0:
            X_all.extend(X_seq)
            y_all.extend(y_seq)
            fechas_all.extend(fechas_seq)
            bloques_validos.append(bloque)

    X_lgbm = np.array(X_all)
    y_lgbm = np.array(y_all)
    fechas_lgbm = np.array(fechas_all)

    if X_lgbm.shape[0] == 0:
        raise ValueError("No se generaron secuencias para entrenar.")

    feature_names = []
    for col in features_numericas:
        for stat in ["mean", "std", "min", "max", "median", "last", "trend"]:
            feature_names.append(f"{col}_{stat}")

    return X_lgbm, y_lgbm, fechas_lgbm, bloques_validos, feature_names


def preparar_splits(
    X: np.ndarray, y: np.ndarray, fechas: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Ordena temporalmente y divide en train/val/test.

    Returns:
        tuple: X_train, X_val, X_test, y_train, y_val, y_test, feature_names.
    """
    sort_idx = np.argsort(fechas)
    X = X[sort_idx]
    y = y[sort_idx]

    if X.shape[0] < 2:
        raise ValueError(f"Muestras insuficientes: {X.shape[0]}")

    split_idx = int(len(X) * 0.7)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    split_val_idx = int(len(X_train) * 0.8)
    X_val = X_train[split_val_idx:]
    y_val = y_train[split_val_idx:]
    X_train = X_train[:split_val_idx]
    y_train = y_train[:split_val_idx]

    return X_train, X_val, X_test, y_train, y_val, y_test # type: ignore


def entrenar_modelos(
    X_train: np.ndarray,
    X_val: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_val: np.ndarray,
    y_test: np.ndarray,
    feature_names: list[str],
    output_dir: str,
) -> tuple[list, list[dict]]:
    """Entrena 18 modelos LightGBM independientes (uno por horizonte).

    Args:
        X_train: Features de entrenamiento.
        X_val: Features de validación.
        X_test: Features de prueba.
        y_train: Targets de entrenamiento.
        y_val: Targets de validación.
        y_test: Targets de prueba.
        feature_names: Nombres de las features.
        output_dir: Directorio para guardar modelos.

    Returns:
        tuple: Lista de modelos y lista de métricas por horizonte.
    """

    modelos = []
    metricas_por_horizonte = []

    print("=" * 60)
    print("ENTRENAMIENTO DE MODELOS LIGHTGBM")
    print("=" * 60)

    for h in range(ts_lgbm.MAX_HORIZONTE):
        print(f"\n--- Horizonte {h + 1} meses ---")

        y_train_h = y_train[:, h]
        y_val_h = y_val[:, h]
        y_test_h = y_test[:, h]

        n_pos = int(np.sum(y_train_h == 1))
        n_neg = int(np.sum(y_train_h == 0))
        scale_pos_weight = n_neg / n_pos if n_pos > 0 else 1

        train_data = lgb.Dataset(X_train, label=y_train_h, feature_name=feature_names)
        val_data = lgb.Dataset(X_val, label=y_val_h, feature_name=feature_names, 
                               reference=train_data)

        params = ts_lgbm.LGBM_PARAMS.copy()
        params["scale_pos_weight"] = scale_pos_weight

        modelo = lgb.train(
            params,
            train_data,
            num_boost_round=ts_lgbm.NUM_BOOST_ROUND,
            valid_sets=[val_data],
            callbacks=[
                lgb.early_stopping(ts_lgbm.EARLY_STOPPING_ROUNDS),
                lgb.log_evaluation(100),
            ],
        )

        y_pred_proba = modelo.predict(X_test)
        y_pred = (y_pred_proba > 0.5).astype(int)

        acc = accuracy_score(y_test_h, y_pred)
        prec = precision_score(y_test_h, y_pred, zero_division=0)
        rec = recall_score(y_test_h, y_pred, zero_division=0)

        auc = 0.5
        if len(np.unique(y_test_h)) > 1:
            try:
                auc = roc_auc_score(y_test_h, y_pred_proba)
            except Exception:
                pass

        print(f"  Accuracy: {acc:.4f}")
        print(f"  Precision: {prec:.4f}")
        print(f"  Recall: {rec:.4f}")
        print(f"  AUC-ROC: {auc:.4f}")

        modelos.append(modelo)
        metricas_por_horizonte.append({
            "horizonte": h + 1,
            "accuracy": float(acc),
            "precision": float(prec),
            "recall": float(rec),
            "auc_roc": float(auc),
            "num_iteraciones": modelo.num_trees(),
            "scale_pos_weight": float(scale_pos_weight),
        })

        modelo_path = os.path.join(output_dir, f"modelo_lgbm_h{h + 1}.txt")
        modelo.save_model(modelo_path)

    return modelos, metricas_por_horizonte
