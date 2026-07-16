##
## @file pipelineCNN.py
##
## Orquestador del modelo CNN. Contiene toda la logica de orquestacion:
##   - Entrenamiento del modelo CNN
##   - Generacion de plots individuales
##   - Salida a MLflow 3.x
##   - Se genera artefacto JSON con detalle de metricas del modelo
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import os
from contextlib import nullcontext
from datetime import datetime
from typing import Any

import joblib
import mlflow
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.preprocessing import MinMaxScaler
from src.ts_cnn.dashboard import build_all_plots
from tensorflow.keras import Model, layers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


def _serialize_for_json(obj):
    """Convierte objetos numpy a tipos serializables en JSON."""
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating,)):
        return float(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _serialize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_serialize_for_json(v) for v in obj]
    return obj


class PipelineCNN:
    """Orquestador del modelo CNN multi-horizonte."""

    VENTANA_CNN = 6
    MAX_HORIZONTE = 18
    EPOCHS = 100
    BATCH_SIZE = 32
    PATIENCE = 10

    def __init__(
        self,
        output_dir: str,
        mlflow_tracking_uri: str,
        mlflow_experiment_name: str,
    ):
        self.output_dir = output_dir
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.mlflow_experiment_name = mlflow_experiment_name
        os.makedirs(self.output_dir, exist_ok=True)

    def _preprocesar_datos(self, df):
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
        features_limpias = [f for f in features_existentes if df_features[f].std() > 0]
        for f in features_limpias:
            q01 = df_features[f].quantile(0.01)
            q99 = df_features[f].quantile(0.99)
            df_features[f] = df_features[f].clip(lower=q01, upper=q99)
        df_features = df_features.sort_values(["bloque_id", "mes"])
        return df_features, features_limpias

    def _crear_secuencias(self, df, bloque_id, features, target, ventana, max_horizonte):
        df_bloque = df[df["bloque_id"] == bloque_id].sort_values("mes")
        if len(df_bloque) < ventana + max_horizonte:
            return None, None, None
        X_seq, y_seq, fechas = [], [], []
        for i in range(len(df_bloque) - ventana - max_horizonte + 1):
            X_seq.append(df_bloque[features].iloc[i : i + ventana].values)
            y_vals = []
            for h in range(1, max_horizonte + 1):
                idx = i + ventana + h - 1
                y_vals.append(df_bloque[target].iloc[idx] if idx < len(df_bloque) else 0)
            y_seq.append(y_vals)
            fechas.append(df_bloque["mes"].iloc[i + ventana - 1])
        return np.array(X_seq), np.array(y_seq), np.array(fechas)

    def _generar_secuencias(self, df, features_numericas):
        X_all, y_all, fechas_all, bloques_validos = [], [], [], []
        for bloque in df["bloque_id"].unique():
            X_seq, y_seq, fechas_seq = self._crear_secuencias(
                df, bloque, features_numericas, "crisis_flag", self.VENTANA_CNN, self.MAX_HORIZONTE
            )
            if X_seq is not None and len(X_seq) > 0:
                X_all.extend(X_seq)
                y_all.extend(y_seq)
                fechas_all.extend(fechas_seq)
                bloques_validos.append(bloque)
        return np.array(X_all), np.array(y_all), np.array(fechas_all), bloques_validos

    def _crear_modelo(self, input_shape, num_horizontes):
        inputs = layers.Input(shape=input_shape)
        x = layers.Conv1D(64, 3, activation="relu", padding="same")(inputs)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Conv1D(128, 3, activation="relu", padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling1D(pool_size=2)(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Flatten()(x)
        x = layers.Dense(128, activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Dropout(0.4)(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(0.3)(x)
        outputs = [
            layers.Dense(1, activation="sigmoid", name=f"horizonte_{i + 1}")(x)
            for i in range(num_horizontes)
        ]
        model = Model(inputs=inputs, outputs=outputs)
        metrics_dict = {
            f"horizonte_{i + 1}": [
                "accuracy",
                tf.keras.metrics.Precision(name=f"precision_{i + 1}"),
                tf.keras.metrics.Recall(name=f"recall_{i + 1}"),
            ]
            for i in range(num_horizontes)
        }
        model.compile(optimizer="adam", loss="binary_crossentropy", metrics=metrics_dict)
        return model

    def _calcular_sample_weights(self, y_train, y_val):
        sw_train, sw_val = [], []
        for h in range(self.MAX_HORIZONTE):
            y_ht = y_train[h]
            n_pos = int(np.sum(y_ht == 1))
            n_neg = int(np.sum(y_ht == 0))
            total = n_pos + n_neg

            w_0 = total / (2.0 * n_neg) if n_neg > 0 else 1.0
            w_1 = total / (2.0 * n_pos) if n_pos > 0 else 1.0
            sw_train.append(np.where(y_ht == 1, w_1, w_0).astype(np.float32))

            y_hv = y_val[h]
            n_pos_v = int(np.sum(y_hv == 1))
            n_neg_v = int(np.sum(y_hv == 0))
            total_v = n_pos_v + n_neg_v

            w_0v = total_v / (2.0 * n_neg_v) if n_neg_v > 0 else 1.0
            w_1v = total_v / (2.0 * n_pos_v) if n_pos_v > 0 else 1.0
            sw_val.append(np.where(y_hv == 1, w_1v, w_0v).astype(np.float32))
        return sw_train, sw_val

    def run(self, input_path: str, run_name: str | None = None):
        """Ejecuta el pipeline completo de CNN."""
        print("Cargando datos...")
        df = pd.read_csv(input_path)
        df["mes"] = pd.to_datetime(df["mes"])

        print("Preprocesando...")
        df_features, features_numericas = self._preprocesar_datos(df)

        print("Generando secuencias...")
        X_cnn, y_cnn, fechas_cnn, bloques_validos = self._generar_secuencias(
            df_features, features_numericas
        )
        if X_cnn.size == 0:
            raise ValueError("No se generaron secuencias.")

        print(f"Secuencias: {X_cnn.shape}, Fechas: {fechas_cnn.min()} a {fechas_cnn.max()}")

        # Normalizar
        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X_cnn.reshape(-1, X_cnn.shape[-1])).reshape(X_cnn.shape)

        # Split temporal
        sort_idx = np.argsort(fechas_cnn)
        X_scaled = X_scaled[sort_idx]
        y_cnn = y_cnn[sort_idx]
        split_idx = int(len(X_scaled) * 0.7)
        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train_list = [y_cnn[:split_idx, i] for i in range(self.MAX_HORIZONTE)]
        y_test_list = [y_cnn[split_idx:, i] for i in range(self.MAX_HORIZONTE)]
        for i in range(len(y_train_list)):
            y_train_list[i] = np.asarray(y_train_list[i]).reshape(
                -1,
            )
        for i in range(len(y_test_list)):
            y_test_list[i] = np.asarray(y_test_list[i]).reshape(
                -1,
            )

        print(f"Train: {X_train.shape[0]}, Test: {X_test.shape[0]}")

        # Crear modelo
        modelo = self._crear_modelo(X_train.shape[1:], self.MAX_HORIZONTE)
        modelo.summary()

        # Split train/val
        val_frac = 0.2
        n_samples = X_train.shape[0]
        val_size = int(n_samples * val_frac)
        train_end = n_samples - val_size
        X_train_final = X_train[:train_end]
        X_val = X_train[train_end:]
        y_train_final = [arr[:train_end] for arr in y_train_list]
        y_val = [arr[train_end:] for arr in y_train_list]

        # Sample weights
        sw_train, sw_val = self._calcular_sample_weights(y_train_final, y_val)

        # Callbacks
        callbacks = [
            EarlyStopping(
                monitor="val_loss", patience=self.PATIENCE, restore_best_weights=True, verbose=1
            ),
            ModelCheckpoint(
                os.path.join(self.output_dir, "best_model_cnn.keras"),
                monitor="val_loss",
                save_best_only=True,
                verbose=1,
            ),
        ]

        # MLflow
        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        try:
            mlflow.set_experiment(self.mlflow_experiment_name)
        except Exception:
            mlflow.create_experiment(self.mlflow_experiment_name)
            mlflow.set_experiment(self.mlflow_experiment_name)

        if run_name is None:
            run_name = f"cnn_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        with mlflow.start_run(run_name=run_name):
            mlflow.log_param("ventana_cnn", self.VENTANA_CNN)
            mlflow.log_param("max_horizonte", self.MAX_HORIZONTE)
            mlflow.log_param("epochs", self.EPOCHS)
            mlflow.log_param("batch_size", self.BATCH_SIZE)
            mlflow.log_param("num_features", len(features_numericas))
            mlflow.log_param("num_bloques", len(bloques_validos))
            mlflow.log_param("num_muestras_train", X_train_final.shape[0])
            mlflow.log_param("num_muestras_val", X_val.shape[0])
            mlflow.log_param("num_muestras_test", X_test.shape[0])

            print("Entrenando...")
            historia = modelo.fit(
                X_train_final,
                y_train_final,
                validation_data=(X_val, y_val, sw_val),
                sample_weight=sw_train,
                epochs=self.EPOCHS,
                batch_size=self.BATCH_SIZE,
                callbacks=callbacks,
                verbose=1,
            )

            # Metricas
            y_pred_proba = modelo.predict(X_test, verbose=0)
            y_pred_1m = (y_pred_proba[0] > 0.5).astype(int).flatten()
            y_test_1m = y_test_list[0]
            test_acc = accuracy_score(y_test_1m, y_pred_1m)
            test_prec = precision_score(y_test_1m, y_pred_1m, zero_division=0)
            test_recall = recall_score(y_test_1m, y_pred_1m, zero_division=0)

            mlflow.log_metric("final_accuracy", float(test_acc))
            mlflow.log_metric("final_precision", float(test_prec))
            mlflow.log_metric("final_recall", float(test_recall))

            # Modelo
            mlflow.tensorflow.log_model(modelo, "modelo")

            # Guardar artifacts
            modelo_path = os.path.join(self.output_dir, "modelo_cnn_multi_18m.keras")
            modelo.save(modelo_path)
            mlflow.log_artifact(modelo_path)

            scaler_path = os.path.join(self.output_dir, "scaler_multi_18m.pkl")
            joblib.dump(scaler, scaler_path)
            mlflow.log_artifact(scaler_path)

            # Plots
            image_paths = build_all_plots(historia, output_dir=self.output_dir)
            for img_path in image_paths:
                mlflow.log_artifact(img_path, "plots")

            # Detail JSON
            detail_data = _serialize_for_json(
                {
                    "metricas": {
                        "accuracy": float(test_acc),
                        "precision": float(test_prec),
                        "recall": float(test_recall),
                    },
                    "config": {
                        "ventana_cnn": self.VENTANA_CNN,
                        "max_horizonte": self.MAX_HORIZONTE,
                        "epochs": self.EPOCHS,
                        "batch_size": self.BATCH_SIZE,
                        "num_features": len(features_numericas),
                        "num_bloques": len(bloques_validos),
                    },
                }
            )
            detail_path = os.path.join(self.output_dir, "cnn_detail.json")
            with open(detail_path, "w") as f:
                json.dump(detail_data, f, indent=2, ensure_ascii=False)
            mlflow.log_artifact(detail_path)

            print(
                f"MLflow: run={run_name}, accuracy={test_acc:.4f},"
                + " precision={test_prec:.4f}, recall={test_recall:.4f}"
            )

        return modelo, scaler, historia


def analizar_cnn(
    mlflow_tracking_uri,
    mlflow_experiment_name,
    path_salida,
    run_key=None,
):
    """Entry point para DAGs de Airflow."""
    path_input = f"{path_salida}/datasets/datos_preprocesados.csv"

    if not os.path.exists(path_input):
        raise FileNotFoundError(f"Dataset no encontrado: {path_input}")

    pipeline = PipelineCNN(
        output_dir=f"{path_salida}/modelos_cnn",
        mlflow_tracking_uri=mlflow_tracking_uri,
        mlflow_experiment_name=mlflow_experiment_name,
    )

    run_name = run_key or f"cnn_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    modelo, scaler, historia = pipeline.run(path_input, run_name=run_name)

    print("CNN completado.")
    return modelo, scaler
