##
## @file mlflowCustom.py
##
## Funciones personalizadas para MLflow en el modelo MLP.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import os
from typing import Any

import joblib
import numpy as np
import src.ts_mlp as ts_mlp
from sklearn.preprocessing import MinMaxScaler
from src.common import configurar_mlflow
from src.ts_mlp.dashboard import build_all_plots
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

    def loggear_parametros_mlflow(
        self,
        features_numericas: list[str],
        bloques_validos: list[int],
        X_train: np.ndarray,
        X_val: np.ndarray,
        X_test: np.ndarray,
    ) -> None:
        """Loggea parámetros del modelo en MLflow."""
        self.mlflow.log_param("ventana_mlp", ts_mlp.VENTANA_MLP)
        self.mlflow.log_param("max_horizonte", ts_mlp.MAX_HORIZONTE)
        self.mlflow.log_param("epochs", ts_mlp.EPOCHS)
        self.mlflow.log_param("batch_size", ts_mlp.BATCH_SIZE)
        self.mlflow.log_param("num_features", len(features_numericas))
        self.mlflow.log_param("num_bloques", len(bloques_validos))
        self.mlflow.log_param("num_muestras_train", X_train.shape[0])
        self.mlflow.log_param("num_muestras_val", X_val.shape[0])
        self.mlflow.log_param("num_muestras_test", X_test.shape[0])

    def loggear_resultados_artefactos_mlflow(
        self,
        modelo: Model,
        scaler: MinMaxScaler,
        historia: Any,
        test_acc: float,
        test_prec: float,
        test_recall: float,
        test_f1: float,
        features_numericas: list[str],
        bloques_validos: list[int],
    ) -> None:
        """Loggea métricas, modelo, scaler y artefactos en MLflow."""
        self.mlflow.log_metric("final_accuracy", test_acc)
        self.mlflow.log_metric("final_f1", test_f1)
        self.mlflow.log_metric("final_precision", test_prec)
        self.mlflow.log_metric("final_recall", test_recall)

        self.mlflow.tensorflow.log_model(modelo, "modelo")

        modelo_path = os.path.join(self.output_dir, "modelo_mlp_multi_18m.keras")
        modelo.save(modelo_path)
        self.mlflow.log_artifact(modelo_path)

        scaler_path = os.path.join(self.output_dir, "scaler_mlp.pkl")
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
                    "ventana_mlp": ts_mlp.VENTANA_MLP,
                    "max_horizonte": ts_mlp.MAX_HORIZONTE,
                    "epochs": ts_mlp.EPOCHS,
                    "batch_size": ts_mlp.BATCH_SIZE,
                    "num_features": len(features_numericas),
                    "num_bloques": len(bloques_validos),
                },
            }
        )
        detail_path = os.path.join(self.output_dir, "mlp_detail.json")
        with open(detail_path, "w") as f:
            json.dump(detail_data, f, indent=2, ensure_ascii=False)
        self.mlflow.log_artifact(detail_path)

        print(
            f"MLflow: accuracy={test_acc:.4f}, f1={test_f1:.4f}, "
            f"precision={test_prec:.4f}, recall={test_recall:.4f}"
        )

    def get_mlflow(self):
        """Devuelve el objeto mlflow configurado."""
        return self.mlflow
