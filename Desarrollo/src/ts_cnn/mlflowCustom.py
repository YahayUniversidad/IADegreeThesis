##
## @file mlflowCustom.py
##
## Funciones personalizadas para el registro de parámetros, métricas y artefactos en MLflow.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import os
from typing import Any

import joblib
import numpy as np
import src.ts_cnn as ts_cnn
from sklearn.preprocessing import MinMaxScaler
from src.common import configurar_mlflow
from src.ts_cnn.dashboard import build_all_plots
from tensorflow.keras.models import Model


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


class MLflowCustom:
    def __init__(
        self,
        mlflow_tracking_uri: str,
        mlflow_experiment_name: str,
        output_dir: str,
    ) -> None:
        self.output_dir = output_dir
        self.mlflow = configurar_mlflow(mlflow_tracking_uri, mlflow_experiment_name)
        print("MLflowCustom initialized.")

    def loggear_parametros_mlflow(
        self,
        features_numericas: list[str],
        bloques_validos: list[int],
        X_train_final: np.ndarray,
        X_val: np.ndarray,
        X_test: np.ndarray,
    ) -> None:
        """Loggea los parámetros del modelo y del dataset en MLflow.

        Args:
            features_numericas (list[str]): Lista de características numéricas utilizadas
                en el modelo.
            bloques_validos (list[int]): Lista de bloques válidos utilizados en el modelo.
            X_train_final (np.ndarray): Conjunto de datos de entrenamiento final.
            X_val (np.ndarray): Conjunto de datos de validación.
            X_test (np.ndarray): Conjunto de datos de prueba.
            ventana_cnn (int): Tamaño de la ventana para las secuencias.
            max_horizonte (int): Horizonte máximo de predicción.
            epochs (int): Número de épocas de entrenamiento.
            batch_size (int): Tamaño del batch.
        """
        self.mlflow.log_param("ventana_cnn", ts_cnn.VENTANA_CNN)
        self.mlflow.log_param("max_horizonte", ts_cnn.MAX_HORIZONTE)
        self.mlflow.log_param("epochs", ts_cnn.EPOCHS)
        self.mlflow.log_param("batch_size", ts_cnn.BATCH_SIZE)
        self.mlflow.log_param("num_features", len(features_numericas))
        self.mlflow.log_param("num_bloques", len(bloques_validos))
        self.mlflow.log_param("num_muestras_train", X_train_final.shape[0])
        self.mlflow.log_param("num_muestras_val", X_val.shape[0])
        self.mlflow.log_param("num_muestras_test", X_test.shape[0])

    def loggear_resultados_artefactos_mlflow(
        self,
        modelo: Model,
        scaler: MinMaxScaler,
        historia: Any,
        test_acc: float,
        test_prec: float,
        test_f1: float,
        test_recall: float,
        features_numericas: list[str],
        bloques_validos: list[int],
    ) -> None:
        """Loggea métricas, modelo, scaler y artefactos en MLflow.

        Args:
            modelo (Model): Modelo entrenado.
            scaler (MinMaxScaler): Escalador utilizado para normalizar los datos.
            historia (Any): Objeto de historia del entrenamiento del modelo.
            test_acc (float): Precisión del modelo en el conjunto de prueba.
            test_f1 (float): F1-score del modelo en el conjunto de prueba.
            test_prec (float): Precisión del modelo en el conjunto de prueba.
            test_recall (float): Recall del modelo en el conjunto de prueba.
            features_numericas (list[str]): Lista de características numéricas utilizadas
                en el modelo.
            bloques_validos (list[int]): Lista de bloques válidos utilizados en el modelo.

        """

        self.mlflow.log_metric("final_accuracy", test_acc)
        self.mlflow.log_metric("final_f1", test_f1)
        self.mlflow.log_metric("final_precision", test_prec)
        self.mlflow.log_metric("final_recall", test_recall)

        self.mlflow.tensorflow.log_model(modelo, "modelo")  # type: ignore

        modelo_path = os.path.join(self.output_dir, "modelo_cnn_multi_18m.keras")
        modelo.save(modelo_path)
        self.mlflow.log_artifact(modelo_path)

        scaler_path = os.path.join(self.output_dir, "scaler_multi_18m.pkl")
        joblib.dump(scaler, scaler_path)
        self.mlflow.log_artifact(scaler_path)

        image_paths = build_all_plots(historia, output_dir=self.output_dir)
        for img_path in image_paths:
            self.mlflow.log_artifact(img_path, "plots")

        detail_data = _serialize_for_json(
            {
                "metricas": {
                    "accuracy": test_acc,
                    "precision": test_prec,
                    "recall": test_recall,
                },
                "config": {
                    "ventana_cnn": ts_cnn.VENTANA_CNN,
                    "max_horizonte": ts_cnn.MAX_HORIZONTE,
                    "epochs": ts_cnn.EPOCHS,
                    "batch_size": ts_cnn.BATCH_SIZE,
                    "num_features": len(features_numericas),
                    "num_bloques": len(bloques_validos),
                },
            }
        )
        detail_path = os.path.join(self.output_dir, "cnn_detail.json")
        with open(detail_path, "w") as f:
            json.dump(detail_data, f, indent=2, ensure_ascii=False)
        self.mlflow.log_artifact(detail_path)

        print(
            f"MLflow: accuracy={test_acc:.4f}, f1={test_f1:.4f}, "
            + " precision={test_prec:.4f}, recall={test_recall:.4f}"
        )

    def get_mlflow(self):
        """Devuelve el objeto mlflow configurado.

        Returns:
            mlflow: Objeto mlflow configurado.
        """
        return self.mlflow
