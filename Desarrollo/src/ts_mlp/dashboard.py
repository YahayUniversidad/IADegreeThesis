##
## @file dashboard.py
##
## Generación de plots individuales del modelo MLP.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from typing import Any

import matplotlib.pyplot as plt
from src.common.utilidades import save_figura


def _plot_loss(historia):
    """Grafica la pérdida del modelo durante entrenamiento y validación.

    Args:
        historia: Objeto History de Keras con el historial de entrenamiento.

    Returns:
        matplotlib.figure.Figure: Figura generada.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(historia.history["loss"], label="Train")
    ax.plot(historia.history["val_loss"], label="Validation")
    ax.set_title("Loss")
    ax.set_xlabel("Época")
    ax.set_ylabel("Loss")
    ax.legend()
    ax.grid(True)
    return fig


def _plot_accuracy(historia):
    """Grafica la precisión del modelo en el horizonte 1.

    Args:
        historia: Objeto History de Keras con el historial de entrenamiento.

    Returns:
        matplotlib.figure.Figure: Figura generada.
    """
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(historia.history["horizonte_1_accuracy"], label="Train")
    ax.plot(historia.history["val_horizonte_1_accuracy"], label="Validation")
    ax.set_title("Accuracy (Horizonte 1 mes)")
    ax.set_xlabel("Época")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.grid(True)
    return fig


def build_all_plots(historia: Any, output_dir: str | None = None) -> list[str]:
    """Genera todos los plots individuales del modelo MLP y los guarda.

    Args:
        historia: Objeto History de Keras con el historial de entrenamiento.
        output_dir: Directorio donde se guardarán las imágenes.

    Returns:
        list[str]: Lista con las rutas de las imágenes generadas.
    """
    print("GENERANDO PLOTS INDIVIDUALES DEL MODELO MLP")
    image_paths = []

    plots = [
        ("01_loss", lambda: _plot_loss(historia)),
        ("02_accuracy", lambda: _plot_accuracy(historia)),
    ]

    for name, plot_func in plots:
        fig = plot_func()
        image_paths.append(save_figura(fig, name, output_dir))

    print(f"Generadas {len(image_paths)} imágenes individuales")
    return image_paths
