##
## @file dashboard.py
##
## Generacion de plots individuales del EVA para MLflow y documentacion.
## Cada plot se genera como imagen separada con tamano optimizado.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns
from src.common.utilidades import as_float, get_columnas_numericas, save_figura


def _plot_heatmap_correlaciones(df, numeric_cols):
    """Crea el plot de heatmap de correlaciones para las variables numericas.

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        numeric_cols (list): Lista de nombres de columnas numéricas.

    Returns:
        matplotlib.figure.Figure: Figura del heatmap de correlaciones.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    if len(numeric_cols) > 1:
        corr_matrix = np.corrcoef(df.select(numeric_cols).to_numpy(), rowvar=False)
        sns.heatmap(corr_matrix, ax=ax, cmap="RdBu_r", center=0,
                    xticklabels=False, yticklabels=False)
    ax.set_title("Matriz de Correlacion (primeras 20 vars)", fontsize=11)
    return fig

def _plot_top_correlaciones(df, target_col, numeric_cols):
    """Crea el plot de las 10 variables con mayor correlacion absoluta con el target.

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.
        numeric_cols (list): Lista de nombres de columnas numéricas.

    Returns:
        matplotlib.figure.Figure: Figura del plot de top correlaciones.
        dict: Resumen de las top correlaciones.
    """

    fig, ax = plt.subplots(figsize=(8, 5))
    summary = {}
    if len(numeric_cols) > 2 and target_col in df.columns:
        try:
            corr_target = df.select(
                [pl.corr(pl.col(c), pl.col(target_col)).abs().alias(c) for c in numeric_cols]
            ).row(0, named=True)
            corr_target = {k: v for k, v in corr_target.items() if v is not None}
            if target_col in corr_target:
                del corr_target[target_col]
            corr_target = dict(sorted(corr_target.items(), key=lambda x: x[1], reverse=True)[:10])
            if corr_target:
                colors = []
                for c in corr_target:
                    cv = df.select(pl.corr(pl.col(c), pl.col(target_col))).item()
                    colors.append("green" if cv is not None and cv > 0 else "red")
                ax.barh(list(corr_target.keys()), list(corr_target.values()), color=colors)
                ax.set_xlabel("|r|")
                ax.invert_yaxis()
                ax.tick_params(labelsize=8)
                summary["top_correlaciones"] = [
                    {"variable": k, "corr_abs": float(v)} for k, v in corr_target.items()
                ]
        except Exception:
            ax.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax.transAxes)
    ax.set_title("Top 10 Correlaciones con Target", fontsize=11)
    return fig, summary

def _plot_vif(evidencias):
    """Crea el plot de VIF (Variance Inflation Factor) para evaluar la multicolinealidad.

    Args:
        evidencias (dict): Diccionario con la información de VIF.

    Returns:
        matplotlib.figure.Figure: Figura del plot de VIF.
        dict: Resumen de los VIFs.

    Returns:
        matplotlib.figure.Figure: Figura del plot de VIF.
        dict: Resumen de los VIFs.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    summary = {}
    if "vif" in evidencias and len(evidencias["vif"]) > 0:
        try:
            vif_data = pl.DataFrame(evidencias["vif"])
            vif_top = vif_data.sort("VIF", descending=True).head(8)
            if len(vif_top) > 0:
                colors = ["red" if v > 10 else "orange" if v > 5 else "green"
                          for v in vif_top["VIF"]]
                ax.barh(range(len(vif_top)), vif_top["VIF"], color=colors)
                ax.set_yticks(range(len(vif_top)))
                ax.set_yticklabels(vif_top["variable"].to_list(), fontsize=8)
                ax.axvline(x=10, color="red", linestyle="--", alpha=0.7, label="VIF=10")
                ax.axvline(x=5, color="orange", linestyle="--", alpha=0.7, label="VIF=5")
                ax.legend(fontsize=8)
                summary["vif_top"] = [
                    {"variable": r["variable"], "vif": float(r["VIF"])}
                    for r in vif_top.iter_rows(named=True)
                ]
        except Exception:
            ax.text(0.5, 0.5, "Error VIF", ha="center", va="center", transform=ax.transAxes)
    ax.set_title("VIF (Multicolinealidad)", fontsize=11)
    return fig, summary

def _plot_recomendaciones(recomendaciones):
    """Crea el plot de recomendaciones EVA (pie).

    Args:
        recomendaciones (list): Lista de recomendaciones.

    Returns:
        matplotlib.figure.Figure: Figura del plot de recomendaciones.
        dict: Resumen de las recomendaciones.
    """
    fig, ax = plt.subplots(figsize=(8, 6))
    summary = {}
    if recomendaciones:
        try:
            df_rec = pl.DataFrame(recomendaciones)
            decision_counts = df_rec["recomendacion"].value_counts()
            if len(decision_counts) > 0:
                color_map = {
                    "✅ INCLUIR": "#2ecc71", "❌ EXCLUIR": "#e74c3c",
                    "MANTENER": "#3498db", "⚠️ EXCLUIR": "#e67e22",
                    "⚠️ EVALUAR (conflicto)": "#f39c12",
                    "🔍 EVALUAR MANUALMENTE": "#95a5a6", "⚠️ EVALUAR": "#f1c40f",
                }
                colors = [color_map.get(idx, "#95a5a6")
                          for idx in decision_counts["recomendacion"].to_list()]
                ax.pie(
                    decision_counts["count"].to_list(),
                    labels=decision_counts["recomendacion"].to_list(),
                    colors=colors, autopct="%1.1f%%", startangle=90,
                    textprops={"fontsize": 8},
                )
                summary["recomendaciones"] = [
                    {"recomendacion": r["recomendacion"], "count": int(r["count"])}
                    for r in decision_counts.iter_rows(named=True)
                ]
        except Exception:
            ax.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax.transAxes)
    ax.set_title("Recomendaciones EVA", fontsize=11)
    return fig, summary

def _plot_variable_vs_target(df, target_col):
    """Crea el plot de variable vs target (boxplot).

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.

    Returns:
        matplotlib.figure.Figure: Figura del plot de variable vs target.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    plot_var = None
    for candidate in ["tasa_judicial", "creditos_judiciales", "total_costo_judicial",
                       "mora_promedio", "saldo_promedio"]:
        if candidate in df.columns:
            plot_var = candidate
            break
    if plot_var and target_col in df.columns:
        try:
            data_plot = df.select([plot_var, target_col]).drop_nulls()
            positions = sorted(data_plot[target_col].unique().to_list())
            box_data = [data_plot.filter(pl.col(target_col) == p)[plot_var].to_numpy()
                         for p in positions]
            ax.boxplot(box_data, positions=positions, patch_artist=True,
                       boxprops=dict(facecolor="lightblue"),
                       medianprops=dict(color="red", linewidth=2))
            ax.set_xlabel("Crisis Flag")
            ax.set_ylabel(plot_var)
        except Exception:
            ax.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax.transAxes)
    ax.set_title(f"{plot_var or 'N/D'} vs Target", fontsize=11)
    return fig

def _plot_distribucion_target(df, target_col):
    """Crea el plot de distribución del target (bar plot).

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.

    Returns:
        matplotlib.figure.Figure: Figura del plot de distribución del target.
        dict: Resumen de la distribución del target.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    summary = {}
    if target_col in df.columns:
        value_counts = df[target_col].value_counts()
        if len(value_counts) > 0:
            labels = value_counts[target_col].to_list()
            counts = value_counts["count"].to_list()
            ax.bar(labels, counts, color=["#2ecc71", "#e74c3c"])
            ax.set_xlabel("Crisis Flag")
            ax.set_ylabel("Frecuencia")
            for i, v in enumerate(counts):
                ax.text(i, v + 50, f"{v:,}", ha="center", fontsize=9)
            summary["target_dist"] = {
                "labels": [int(x) if isinstance(x, (int, float)) else str(x) for x in labels],
                "counts": [int(x) for x in counts],
            }
    ax.set_title("Distribucion Target", fontsize=11)
    return fig, summary

def _plot_tasa_crisis_temporal(df, target_col):
    """Crea el plot de tasa de crisis temporal (line plot).

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.

    Returns:
        matplotlib.figure.Figure: Figura del plot de tasa de crisis temporal.
        dict: Resumen de la tasa de crisis temporal.
    """
    fig, ax = plt.subplots(figsize=(11, 5))
    summary = {}
    if "mes" in df.columns and target_col in df.columns:
        try:
            crisis_temp = (
                df.group_by(df["mes"].alias("periodo"))
                .agg([pl.col(target_col).mean().alias("mean"),
                      pl.col(target_col).count().alias("count")])
                .sort("periodo")
            )
            if len(crisis_temp) > 0:
                x_vals = crisis_temp["periodo"].cast(pl.String).to_list()
                y_vals = crisis_temp["mean"].to_list()
                ax.plot(x_vals, y_vals, color="darkred", marker="o",
                        markersize=3, linewidth=1.5)
                media = crisis_temp["mean"].to_numpy().mean()
                ax.axhline(y=media, color="blue", linestyle="--", alpha=0.7,
                           label=f"Media: {media:.3f}")
                ax.legend(fontsize=9)
                ax.tick_params(axis="x", rotation=45, labelsize=7)
                for i, label in enumerate(ax.get_xticklabels()):
                    if i % 12 != 0:
                        label.set_visible(False)
                summary["tasa_crisis_temporal"] = {"media": float(media)}
        except Exception:
            ax.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax.transAxes)
    ax.set_title("Tasa Crisis Temporal", fontsize=11)
    return fig, summary

def _plot_resumen_estadistico(df, target_col, numeric_cols, recomendaciones, summary):
    """Crea el plot de resumen estadístico (texto).

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.
        numeric_cols (list): Lista de columnas numéricas.
        recomendaciones (list): Lista de recomendaciones.
        summary (dict): Resumen de análisis previos.

    Returns:
        matplotlib.figure.Figure: Figura del plot de resumen estadístico.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.axis("off")
    n_crisis = int(df[target_col].sum()) if target_col in df.columns else 0
    n_total = len(df)
    pct_crisis = as_float(df[target_col].mean()) * 100 if target_col in df.columns else 0
    n_vif = len([v for v in summary.get("vif_top", []) if v["vif"] > 10])
    n_inc = sum(1 for r in recomendaciones if "INCLUIR" in r.get("recomendacion", ""))
    n_exc = sum(1 for r in recomendaciones if "EXCLUIR" in r.get("recomendacion", ""))
    n_eva = sum(1 for r in recomendaciones if "EVALUAR" in r.get("recomendacion", ""))
    stats = (
        f"DATASET\n{'='*30}\n"
        f"Registros: {n_total:,}\n"
        f"Variables: {len(df.columns)}\n"
        f"Numericas: {len(numeric_cols)}\n"
        f"Target: {target_col}\n"
        f"Crisis: {n_crisis:,} ({pct_crisis:.1f}%)\n"
        f"No-crisis: {n_total - n_crisis:,}\n"
        f"{'='*30}\n"
        f"VIF>10: {n_vif}\n"
        f"INCLUIR: {n_inc}\n"
        f"EXCLUIR: {n_exc}\n"
        f"EVALUAR: {n_eva}"
    )
    ax.text(0.05, 0.95, stats, transform=ax.transAxes, fontsize=10,
            verticalalignment="top", fontfamily="monospace",
            bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    ax.set_title("Resumen Estadistico", fontsize=11)
    return fig

def _plot_auc_roc_variable(df, target_col, numeric_cols):
    """Crea el plot de AUC-ROC para cada variable numérica respecto al target.
    
    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.
        numeric_cols (list): Lista de columnas numéricas.
        
    Returns:
        matplotlib.figure.Figure: Figura del plot de AUC-ROC.
        dict: Resumen de los AUC-ROC por variable.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    summary = {}
    try:
        from sklearn.metrics import roc_auc_score
        auc_data = {}
        for col in numeric_cols:
            if col == target_col:
                continue
            vals = df.select([col, target_col]).drop_nulls()
            if len(vals) < 10:
                continue
            x = vals[col].to_numpy()
            y = vals[target_col].to_numpy()
            if len(np.unique(y)) < 2:
                continue
            try:
                auc = roc_auc_score(y, x)
                auc_data[col] = abs(auc - 0.5) * 2
            except Exception:
                pass
        if auc_data:
            sorted_auc = dict(sorted(auc_data.items(), key=lambda x: x[1], reverse=True)[:8])
            colors = ["#2ecc71" if v > 0.7 else "#f39c12" if v > 0.5 else "#e74c3c"
                      for v in sorted_auc.values()]
            ax.barh(list(sorted_auc.keys()), list(sorted_auc.values()), color=colors)
            ax.set_xlabel("|AUC-0.5|x2")
            ax.invert_yaxis()
            ax.axvline(x=0.5, color="gray", linestyle="--", alpha=0.5)
            ax.tick_params(labelsize=8)
            summary["auc_roc_variable"] = [
                {"variable": k, "auc_norm": float(v)} for k, v in sorted_auc.items()
            ]
    except Exception:
        ax.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax.transAxes)
    ax.set_title("Poder Discriminativo (AUC-ROC)", fontsize=11)
    return fig, summary

def _plot_densidad_comparativa(df, target_col):
    """Crea el plot de densidad comparativa para las variables seleccionadas.

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.

    Returns:
        matplotlib.figure.Figure: Figura del plot de densidad comparativa.
        dict: Resumen de la variable utilizada para la densidad.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    summary = {}
    plot_col = None
    for candidate in ["tasa_judicial", "creditos_judiciales",
                       "total_costo_judicial", "saldo_promedio"]:
        if candidate in df.columns and target_col in df.columns:
            plot_col = candidate
            break
    if plot_col:
        try:
            vals_0 = df.filter(pl.col(target_col) == 0)[plot_col].to_numpy()
            vals_1 = df.filter(pl.col(target_col) == 1)[plot_col].to_numpy()
            if len(vals_0) > 0 and len(vals_1) > 0:
                ax.hist(vals_0, bins=40, alpha=0.5, label="No crisis",
                        color="#2ecc71", density=True)
                ax.hist(vals_1, bins=40, alpha=0.5, label="Crisis",
                        color="#e74c3c", density=True)
                ax.set_xlabel(plot_col, fontsize=9)
                ax.set_ylabel("Densidad")
                ax.legend(fontsize=9)
                ax.set_yscale("log")
                summary["densidad_feature"] = plot_col
        except Exception:
            ax.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax.transAxes)
    ax.set_title(f"Densidad: {plot_col or 'N/D'}", fontsize=11)
    return fig, summary

def build_all_plots(
    df: pl.DataFrame,
    target_col: str,
    evidencias: dict,
    recomendaciones: list[dict],
    output_dir: str | None = None,
) -> tuple[list[str], dict]:
    """Genera los 10 plots individuales del EVA.

    Args:
        df (pl.DataFrame): DataFrame de Polars con los datos.
        target_col (str): Nombre de la columna objetivo.
        evidencias (dict): Diccionario con la información de VIF.
        recomendaciones (list): Lista de recomendaciones.
        output_dir (str | None): 
            Directorio de salida para guardar las imágenes. 
            Si es None, se guardan en un directorio temporal.

    Returns:
        tuple: (lista de paths de imagenes, summary dict)
    """
    print("GENERANDO PLOTS INDIVIDUALES DEL EVA")
    numeric_cols = get_columnas_numericas(df)[:20]
    image_paths = []
    summary: dict[str, Any] = {
        "target_col": target_col,
        "total_registros": len(df),
        "total_variables": len(df.columns),
    }

    plots = [
        ("01_heatmap_correlaciones",   lambda: _plot_heatmap_correlaciones(df, numeric_cols)),
        ("02_top_correlaciones",       lambda: _plot_top_correlaciones(df, target_col, 
                                                                      numeric_cols)),
        ("03_vif_multicolinealidad",   lambda: _plot_vif(evidencias)),
        ("04_recomendaciones_eva",     lambda: _plot_recomendaciones(recomendaciones)),
        ("05_variable_vs_target",      lambda: _plot_variable_vs_target(df, target_col)),
        ("06_distribucion_target",     lambda: _plot_distribucion_target(df, target_col)),
        ("07_tasa_crisis_temporal",    lambda: _plot_tasa_crisis_temporal(df, target_col)),
        ("08_resumen_estadistico",     lambda: _plot_resumen_estadistico(df, target_col, 
                                                                        numeric_cols,
                                                                        recomendaciones, summary)),
        ("09_auc_roc_variable",        lambda: _plot_auc_roc_variable(df, target_col, 
                                                                      numeric_cols)),
        ("10_densidad_comparativa",    lambda: _plot_densidad_comparativa(df, target_col)),
    ]

    for name, plot_fn in plots:
        result = plot_fn()
        if isinstance(result, tuple):
            fig, plot_summary = result
            summary.update(plot_summary)
        else:
            fig = result
        image_paths.append(save_figura(fig, name, output_dir))

    print(f"Generadas {len(image_paths)} imagenes individuales")
    return image_paths, summary
