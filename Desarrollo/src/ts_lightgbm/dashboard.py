##
## @file dashboard.py
##
## Generación de plots individuales del modelo LightGBM.
##   - Métricas por horizonte (4 subplots)
##   - Importancia de features (top 20)
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from src.common.utilidades import save_figura


def plot_metricas_por_horizonte(metricas_por_horizonte: list[dict], output_dir: str) -> str:
    """Genera gráfica de métricas por horizonte (accuracy, precision, recall, AUC-ROC).

    Args:
        metricas_por_horizonte: Lista de diccionarios con métricas por horizonte.
        output_dir: Directorio donde guardar la imagen.

    Returns:
        str: Ruta de la imagen generada.
    """
    df_metricas = pd.DataFrame(metricas_por_horizonte)

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    axes[0, 0].bar(df_metricas["horizonte"], df_metricas["accuracy"], color="blue", alpha=0.7)
    axes[0, 0].set_title("Accuracy por Horizonte")
    axes[0, 0].set_xlabel("Horizonte (meses)")
    axes[0, 0].set_ylabel("Accuracy")
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].bar(df_metricas["horizonte"], df_metricas["precision"], color="green", alpha=0.7)
    axes[0, 1].set_title("Precision por Horizonte")
    axes[0, 1].set_xlabel("Horizonte (meses)")
    axes[0, 1].set_ylabel("Precision")
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].bar(df_metricas["horizonte"], df_metricas["recall"], color="orange", alpha=0.7)
    axes[1, 0].set_title("Recall por Horizonte")
    axes[1, 0].set_xlabel("Horizonte (meses)")
    axes[1, 0].set_ylabel("Recall")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].bar(df_metricas["horizonte"], df_metricas["auc_roc"], color="red", alpha=0.7)
    axes[1, 1].set_title("AUC-ROC por Horizonte")
    axes[1, 1].set_xlabel("Horizonte (meses)")
    axes[1, 1].set_ylabel("AUC-ROC")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    return save_figura(fig, "metricas_por_horizonte", output_dir)


def plot_importancia_features(
    modelos: list, feature_names: list[str], output_dir: str
) -> str:
    """Genera gráfica de importancia de features (promedio de todos los horizontes).

    Args:
        modelos: Lista de modelos LightGBM entrenados.
        feature_names: Nombres de las features.
        output_dir: Directorio donde guardar la imagen.

    Returns:
        str: Ruta de la imagen generada.
    """
    importancia_total = np.zeros(len(feature_names))
    for modelo in modelos:
        importancia_total += modelo.feature_importance()
    importancia_promedio = importancia_total / len(modelos)

    df_importancia = pd.DataFrame({
        "feature": feature_names,
        "importancia": importancia_promedio,
    }).sort_values("importancia", ascending=False)

    top_20 = df_importancia.head(20)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.barh(range(len(top_20)), top_20["importancia"], color="steelblue", alpha=0.7)
    ax.set_yticks(range(len(top_20)))
    ax.set_yticklabels(top_20["feature"])
    ax.set_xlabel("Importancia")
    ax.set_title("Top 20 Features Más Importantes (LightGBM)")
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    print("\nTop 20 features más importantes:")
    print(df_importancia.head(20).to_string(index=False))

    return save_figura(fig, "importancia_features", output_dir)


def build_all_plots(
    modelos: list,
    metricas_por_horizonte: list[dict],
    feature_names: list[str],
    output_dir: str,
) -> list[str]:
    """Genera todos los plots individuales del modelo LightGBM y los guarda.

    Args:
        modelos: Lista de modelos LightGBM entrenados.
        metricas_por_horizonte: Lista de métricas por horizonte.
        feature_names: Nombres de las features.
        output_dir: Directorio donde guardar las imágenes.

    Returns:
        list[str]: Lista con las rutas de las imágenes generadas.
    """
    print("GENERANDO PLOTS INDIVIDUALES DEL MODELO LIGHTGBM")
    image_paths = []

    image_paths.append(plot_metricas_por_horizonte(metricas_por_horizonte, output_dir))
    image_paths.append(plot_importancia_features(modelos, feature_names, output_dir))

    print(f"Generadas {len(image_paths)} imágenes individuales")
    return image_paths
