##
## @file dashboard.py
##
## Generacion de plots individuales del modelo cnn.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from typing import Any

import matplotlib.pyplot as plt
from src.common.utilidades import save_figura


def _plot_loss(historia):
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
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(historia.history["horizonte_1_accuracy"], label="Train")
    ax.plot(historia.history["val_horizonte_1_accuracy"], label="Validation")
    ax.set_title("Accuracy (Horizonte 1 mes)")
    ax.set_xlabel("Época")
    ax.set_ylabel("Accuracy")
    ax.legend()
    ax.grid(True)

    return fig

def build_all_plots(
    historia: Any,
    output_dir: str | None = None,
) -> list[str]:

    print("GENERANDO PLOTS INDIVIDUALES DEL MODELO CNN")
    image_paths = []

    plots = [
        ("01_loss", lambda: _plot_loss(historia)),
        ("02_accuracy", lambda: _plot_accuracy(historia)),
    ]

    for name, plot_func in plots:
        result = plot_func()
        if isinstance(result, dict):
            plot_summary = result
            image_paths.append(plot_summary["image_path"])
            del plot_summary["image_path"]
        else:
            fig = result
            image_paths.append(save_figura(fig, name, output_dir))

    print(f"Generadas {len(image_paths)} imagenes individuales")
    return image_paths