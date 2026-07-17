##
## @file pipelineMLP.py
##
## Orquestador del modelo MLP. Contiene toda la lógica de orquestación:
##   - Entrenamiento del modelo MLP
##   - Generación de plots individuales
##   - Salida a MLflow 3.x
##   - Se genera artefacto JSON con detalle de métricas del modelo
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import os
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
import src.ts_mlp as ts_mlp
import src.ts_mlp.mlflowCustom as mlflowCustom
import tensorflow as tf
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras import Model, layers
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint


class PipelineMLP:
    """Orquestador del modelo MLP multi-horizonte."""

    def __init__(
        self,
        output_dir: str,
        mlflow_tracking_uri: str,
        mlflow_experiment_name: str,
    ):
        """Constructor de la clase PipelineMLP.

        Args:
            output_dir: Directorio de salida para los artefactos del modelo.
            mlflow_tracking_uri: URI de seguimiento de MLflow.
            mlflow_experiment_name: Nombre del experimento en MLflow.
        """
        self.output_dir = output_dir
        self.run_name = f"mlp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.mlflow_custom = mlflowCustom.MLflowCustom(
            mlflow_tracking_uri, mlflow_experiment_name, output_dir=output_dir
        )

        os.makedirs(self.output_dir, exist_ok=True)

    def _preprocesar_datos(self, df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
        """Preprocesa los datos del DataFrame."""
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

    def _crear_secuencias(
        self, df, bloque_id, features, target, ventana, max_horizonte
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Crea secuencias de datos para entrenamiento y prueba."""
        df_bloque = df[df["bloque_id"] == bloque_id].sort_values("mes")
        if len(df_bloque) < ventana + max_horizonte:
            return None, None, None  # type: ignore
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
        """Genera secuencias de datos para todos los bloques."""
        X_all, y_all, fechas_all, bloques_validos = [], [], [], []
        for bloque in df["bloque_id"].unique():
            X_seq, y_seq, fechas_seq = self._crear_secuencias(
                df,
                bloque,
                features_numericas,
                "crisis_flag",
                ts_mlp.VENTANA_MLP,
                ts_mlp.MAX_HORIZONTE,
            )
            if X_seq is not None and len(X_seq) > 0:
                X_all.extend(X_seq)
                y_all.extend(y_seq)
                fechas_all.extend(fechas_seq)
                bloques_validos.append(bloque)
        return np.array(X_all), np.array(y_all), np.array(fechas_all), bloques_validos

    def _crear_modelo(self, input_shape, num_horizontes) -> Model:
        """Crea el modelo MLP multi-horizonte."""
        inputs = layers.Input(shape=input_shape)

        # Aplanar secuencia temporal
        x = layers.Flatten()(inputs)

        # Capas densas simples
        x = layers.Dense(128, activation="relu")(x)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(64, activation="relu")(x)
        x = layers.Dropout(0.2)(x)

        # Salidas múltiples (una por horizonte)
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
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss="binary_crossentropy",
            metrics=metrics_dict,
        )
        return model

    def _evaluar_horizonte_1(
        self, modelo: Model, X_test: np.ndarray, y_test_list: list[np.ndarray]
    ) -> tuple[float, float, float, float]:
        """Evalúa el modelo en el horizonte 1 y calcula métricas."""
        y_pred_proba = modelo.predict(X_test, verbose=0)
        y_pred_1m = (y_pred_proba[0] > 0.5).astype(int).flatten()
        y_test_1m = y_test_list[0]
        test_acc = accuracy_score(y_test_1m, y_pred_1m)
        test_prec = precision_score(y_test_1m, y_pred_1m, zero_division=0)
        test_recall = recall_score(y_test_1m, y_pred_1m, zero_division=0)
        test_f1 = f1_score(y_test_1m, y_pred_1m, zero_division=0)
        return float(test_acc), float(test_prec), float(test_recall), float(test_f1)

    def _preparar_splits(
        self, X_scaled: np.ndarray, y: np.ndarray, fechas: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, 
               list[np.ndarray], list[np.ndarray], list[np.ndarray]]:
        """Ordena temporalmente y divide en train/val/test."""
        sort_idx = np.argsort(fechas)
        X_scaled = X_scaled[sort_idx]
        y = y[sort_idx]

        split_idx = int(len(X_scaled) * 0.7)
        X_train, X_test = X_scaled[:split_idx], X_scaled[split_idx:]
        y_train_list = [y[:split_idx, i] for i in range(ts_mlp.MAX_HORIZONTE)]
        y_test_list = [y[split_idx:, i] for i in range(ts_mlp.MAX_HORIZONTE)]

        for i in range(len(y_train_list)):
            y_train_list[i] = np.asarray(y_train_list[i]).reshape(-1)
        for i in range(len(y_test_list)):
            y_test_list[i] = np.asarray(y_test_list[i]).reshape(-1)

        val_frac = 0.3
        n_samples = X_train.shape[0]
        val_size = int(n_samples * val_frac)
        train_end = n_samples - val_size

        X_train_final = X_train[:train_end]
        X_val = X_train[train_end:]
        y_train_final = [arr[:train_end] for arr in y_train_list]
        y_val = [arr[train_end:] for arr in y_train_list]

        return X_train_final, X_val, X_test, y_train_final, y_val, y_test_list

    def run(self, input_path: str) -> tuple[Model, MinMaxScaler, Any]:
        """Ejecuta el pipeline completo de MLP.

        Args:
            input_path: Ruta al archivo CSV de entrada.

        Returns:
            tuple[Model, MinMaxScaler, Any]: Modelo entrenado, escalador y historia.
        """
        print("Cargando datos...")
        df = pd.read_csv(input_path)
        df["mes"] = pd.to_datetime(df["mes"])

        print("Preprocesando...")
        df_features, features_numericas = self._preprocesar_datos(df)

        print("Generando secuencias...")
        X, y, fechas, bloques_validos = self._generar_secuencias(
            df_features, features_numericas
        )
        if X.size == 0:
            raise ValueError("No se generaron secuencias.")

        print(f"Secuencias: {X.shape}, Fechas: {fechas.min()} a {fechas.max()}")

        scaler = MinMaxScaler()
        X_scaled = scaler.fit_transform(X.reshape(-1, X.shape[-1])).reshape(X.shape)

        X_train, X_val, X_test, y_train, y_val, y_test_list = self._preparar_splits(
            X_scaled, y, fechas
        )

        print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")

        modelo = self._crear_modelo(X_train.shape[1:], ts_mlp.MAX_HORIZONTE)
        modelo.summary()

        callbacks = [
            EarlyStopping(
                monitor="val_loss",
                patience=ts_mlp.PATIENCE,
                restore_best_weights=True,
                verbose=1,
            ),
            ModelCheckpoint(
                os.path.join(self.output_dir, "best_model_mlp.keras"),
                monitor="val_loss",
                save_best_only=True,
                verbose=1,
            ),
        ]

        with self.mlflow_custom.get_mlflow().start_run(run_name=self.run_name):
            self.mlflow_custom.loggear_parametros_mlflow(
                features_numericas=features_numericas,
                bloques_validos=bloques_validos,
                X_train=X_train,
                X_val=X_val,
                X_test=X_test,
            )

            print("Entrenando...")

            historia = modelo.fit(
                X_train,
                y_train,
                validation_data=(X_val, y_val),
                epochs=ts_mlp.EPOCHS,
                batch_size=ts_mlp.BATCH_SIZE,
                callbacks=callbacks,
                verbose=1,
            )

            test_acc, test_prec, test_recall, test_f1 = self._evaluar_horizonte_1(
                modelo, X_test, y_test_list
            )

            self.mlflow_custom.loggear_resultados_artefactos_mlflow(
                modelo=modelo,
                scaler=scaler,
                historia=historia,
                test_acc=test_acc,
                test_prec=test_prec,
                test_recall=test_recall,
                test_f1=test_f1,
                features_numericas=features_numericas,
                bloques_validos=bloques_validos,
            )

            print(
                f"MLflow: run={self.run_name}, accuracy={test_acc:.4f}, "
                f"precision={test_prec:.4f}, recall={test_recall:.4f}"
            )

        return modelo, scaler, historia


def analizar_mlp(
    mlflow_tracking_uri,
    mlflow_experiment_name,
    path_trabajo,
):
    """Entry point para DAGs de Airflow.

    Args:
        mlflow_tracking_uri: URI de seguimiento de MLflow.
        mlflow_experiment_name: Nombre del experimento en MLflow.
        path_trabajo: Ruta de trabajo para los artefactos del modelo.

    Returns:
        tuple[Model, MinMaxScaler]: Modelo entrenado y escalador.
    """
    path_input = f"{path_trabajo}/lotes/datasets/datos_preprocesados.csv"

    if not os.path.exists(path_input):
        raise FileNotFoundError(f"Dataset no encontrado: {path_input}")

    pipeline = PipelineMLP(
        output_dir=f"{path_trabajo}/modelos_mlp",
        mlflow_tracking_uri=mlflow_tracking_uri,
        mlflow_experiment_name=mlflow_experiment_name,
    )

    modelo, scaler, historia = pipeline.run(path_input)

    print("MLP completado.")
    return modelo, scaler
