##
## @file mlflowCustom.py
##
## Funciones personalizadas para MLflow en el modelo LightGBM.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import os

import joblib
import numpy as np
import pandas as pd
import src.ts_lightgbm as ts_lgbm
from sklearn.preprocessing import MinMaxScaler
from src.common import configurar_mlflow
from src.ts_lightgbm.dashboard import build_all_plots


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
        bloques_validos: list[str],
        X_train: np.ndarray,
        X_val: np.ndarray,
        X_test: np.ndarray,
        feature_names: list[str],
    ) -> None:
        """Loggea parámetros del modelo en MLflow."""
        self.mlflow.log_param("ventana_lgbm", ts_lgbm.VENTANA_LGBM)
        self.mlflow.log_param("max_horizonte", ts_lgbm.MAX_HORIZONTE)
        self.mlflow.log_param("num_boost_round", ts_lgbm.NUM_BOOST_ROUND)
        self.mlflow.log_param("early_stopping_rounds", ts_lgbm.EARLY_STOPPING_ROUNDS)
        self.mlflow.log_param("num_features_base", len(features_numericas))
        self.mlflow.log_param("num_features_lgbm", len(feature_names))
        self.mlflow.log_param("num_bloques", len(bloques_validos))
        self.mlflow.log_param("num_muestras_train", X_train.shape[0])
        self.mlflow.log_param("num_muestras_val", X_val.shape[0])
        self.mlflow.log_param("num_muestras_test", X_test.shape[0])

    def loggear_resultados_artefactos_mlflow(
        self,
        modelos: list,
        scaler: MinMaxScaler,
        metricas_por_horizonte: list[dict],
        feature_names: list[str],
        bloques_validos: list[str],
        features_numericas: list[str],
    ) -> None:
        """Loggea métricas, modelos, scaler y artefactos en MLflow."""

        df_metricas = pd.DataFrame(metricas_por_horizonte)

        self.mlflow.log_metric("accuracy_promedio", float(df_metricas["accuracy"].mean()))
        self.mlflow.log_metric("precision_promedio", float(df_metricas["precision"].mean()))
        self.mlflow.log_metric("recall_promedio", float(df_metricas["recall"].mean()))
        self.mlflow.log_metric("auc_roc_promedio", float(df_metricas["auc_roc"].mean()))

        for h_idx, modelo in enumerate(modelos):
            self.mlflow.lightgbm.log_model(modelo, f"modelo_h{h_idx + 1}")

        scaler_path = os.path.join(self.output_dir, "scaler_lgbm.pkl")
        joblib.dump(scaler, scaler_path)
        self.mlflow.log_artifact(scaler_path)

        image_paths = build_all_plots(
            modelos, metricas_por_horizonte, feature_names, output_dir=self.output_dir
        )
        for img_path in image_paths:
            self.mlflow.log_artifact(img_path, "plots")

        detail_data = _serialize_for_json(
            {
                "metricas_por_horizonte": metricas_por_horizonte,
                "metricas_promedio": {
                    "accuracy": float(df_metricas["accuracy"].mean()),
                    "precision": float(df_metricas["precision"].mean()),
                    "recall": float(df_metricas["recall"].mean()),
                    "auc_roc": float(df_metricas["auc_roc"].mean()),
                },
                "config": {
                    "ventana_lgbm": ts_lgbm.VENTANA_LGBM,
                    "max_horizonte": ts_lgbm.MAX_HORIZONTE,
                    "num_boost_round": ts_lgbm.NUM_BOOST_ROUND,
                    "early_stopping_rounds": ts_lgbm.EARLY_STOPPING_ROUNDS,
                    "num_features_base": len(features_numericas),
                    "num_features_lgbm": len(feature_names),
                    "num_bloques": len(bloques_validos),
                },
            }
        )
        detail_path = os.path.join(self.output_dir, "lightgbm_detail.json")
        with open(detail_path, "w") as f:
            json.dump(detail_data, f, indent=2, ensure_ascii=False)
        self.mlflow.log_artifact(detail_path)

        config = {
            "ventana_lgbm": ts_lgbm.VENTANA_LGBM,
            "max_horizonte": ts_lgbm.MAX_HORIZONTE,
            "features_numericas": features_numericas,
            "feature_names": feature_names,
            "bloques_validos": bloques_validos,
            "hiperparametros": ts_lgbm.LGBM_PARAMS,
            "num_boost_round": ts_lgbm.NUM_BOOST_ROUND,
            "early_stopping_rounds": ts_lgbm.EARLY_STOPPING_ROUNDS,
            "metricas_por_horizonte": metricas_por_horizonte,
            "metricas_promedio": {
                "accuracy": float(df_metricas["accuracy"].mean()),
                "precision": float(df_metricas["precision"].mean()),
                "recall": float(df_metricas["recall"].mean()),
                "auc_roc": float(df_metricas["auc_roc"].mean()),
            },
        }
        config_path = os.path.join(self.output_dir, "config_lgbm_18m.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2, default=str)

        print(
            f"MLflow: accuracy_prom={df_metricas['accuracy'].mean():.4f}, "
            f"precision_prom={df_metricas['precision'].mean():.4f}, "
            f"recall_prom={df_metricas['recall'].mean():.4f}"
        )

    def get_mlflow(self):
        """Devuelve el objeto mlflow configurado."""
        return self.mlflow
