##
## @file pipelineLightGBM.py
##
## Orquestador del modelo LightGBM. Contiene toda la lógica de orquestación:
##   - Entrenamiento de 18 modelos LightGBM independientes
##   - Generación de plots individuales
##   - Salida a MLflow 3.x
##   - Se genera artefacto JSON con detalle de métricas del modelo
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import os
from datetime import datetime

import joblib
import pandas as pd
import src.ts_lightgbm as ts_lgbm
import src.ts_lightgbm.mlflowCustom as mlflowCustom
from sklearn.preprocessing import MinMaxScaler
from src.ts_lightgbm.model import (
    entrenar_modelos,
    generar_secuencias,
    preparar_splits,
    preprocesar_datos,
)


class PipelineLightGBM:
    """Orquestador del modelo LightGBM multi-horizonte."""

    def __init__(
        self,
        output_dir: str,
        mlflow_tracking_uri: str,
        mlflow_experiment_name: str,
    ):
        """Constructor de la clase PipelineLightGBM.

        Args:
            output_dir: Directorio de salida para los artefactos del modelo.
            mlflow_tracking_uri: URI de seguimiento de MLflow.
            mlflow_experiment_name: Nombre del experimento en MLflow.
        """
        self.output_dir = output_dir
        self.run_name = f"lgbm_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        self.mlflow_custom = mlflowCustom.MLflowCustom(
            mlflow_tracking_uri, mlflow_experiment_name, output_dir=output_dir
        )

        os.makedirs(self.output_dir, exist_ok=True)

    def run(self, input_path: str) -> tuple[list, MinMaxScaler, list[dict]]:
        """Ejecuta el pipeline completo de LightGBM.

        Args:
            input_path: Ruta al archivo CSV de entrada.

        Returns:
            tuple: Lista de modelos, escalador, métricas por horizonte.
        """
        print("Cargando datos...")
        df = pd.read_csv(input_path)
        df["mes"] = pd.to_datetime(df["mes"])

        print("Preprocesando...")
        df_features, features_numericas = preprocesar_datos(df)

        print("Generando secuencias...")
        X, y, fechas, bloques_validos, feature_names = generar_secuencias(
            df_features, features_numericas
        )
        print(f"Secuencias: {X.shape}, Fechas: {fechas.min()} a {fechas.max()}")

        X_train, X_val, X_test, y_train, y_val, y_test = preparar_splits(X, y, fechas)

        print(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")

        scaler = MinMaxScaler()
        scaler.fit(X_train)

        print("Entrenando modelos...")
        modelos, metricas_por_horizonte = entrenar_modelos(
            X_train, X_val, X_test, y_train, y_val, y_test,
            feature_names, self.output_dir,
        )

        print("Guardando scaler...")
        scaler_path = os.path.join(self.output_dir, "scaler_lgbm.pkl")
        
        joblib.dump(scaler, scaler_path)
        print(f"Scaler guardado en: {scaler_path}")

        print("Guardando configuración...")
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
        }
        
        config_path = os.path.join(self.output_dir, "config_lgbm_18m.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2, default=str)
        print(f"Configuración guardada en: {config_path}")

        with self.mlflow_custom.get_mlflow().start_run(run_name=self.run_name):
            self.mlflow_custom.loggear_parametros_mlflow(
                features_numericas=features_numericas,
                bloques_validos=bloques_validos,
                X_train=X_train,
                X_val=X_val,
                X_test=X_test,
                feature_names=feature_names,
            )

            self.mlflow_custom.loggear_resultados_artefactos_mlflow(
                modelos=modelos,
                scaler=scaler,
                metricas_por_horizonte=metricas_por_horizonte,
                feature_names=feature_names,
                bloques_validos=bloques_validos,
                features_numericas=features_numericas,
            )

            print(f"MLflow: run={self.run_name} completado.")

        return modelos, scaler, metricas_por_horizonte


def analizar_lightgbm(
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
        tuple: Lista de modelos y escalador.
    """
    path_input = f"{path_trabajo}/lotes/datasets/datos_preprocesados.csv"

    if not os.path.exists(path_input):
        raise FileNotFoundError(f"Dataset no encontrado: {path_input}")

    pipeline = PipelineLightGBM(
        output_dir=f"{path_trabajo}/modelos_lightgbm",
        mlflow_tracking_uri=mlflow_tracking_uri,
        mlflow_experiment_name=mlflow_experiment_name,
    )

    modelos, scaler, metricas = pipeline.run(path_input)

    print("LightGBM completado.")
    return modelos, scaler
