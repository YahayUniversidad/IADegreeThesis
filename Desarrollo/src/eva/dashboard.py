##
## @file dashboard.py
##
## Construccion del dashboard EVA y resumen estructurado por panel.
## Contiene toda la logica de visualizacion:
##   - Generacion del dashboard 5x2
##   - Resumen estructurado para MLflow
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns

from .utilidades import as_float, get_columnas_numericas


def build_dashboard(
    df: pl.DataFrame,
    target_col: str,
    evidencias: dict,
    recomendaciones: list[dict],
) -> tuple[Any, dict]:
    """Genera el dashboard EVA 5x2 y retorna un resumen entendible para MLflow.

    Además, retorna un diccionario con los datos resumidos de cada panel para su posterior
    registro en MLflow.

    Args:
        df (pl.DataFrame): DataFrame de entrada con las variables y el target.
        target_col (str): Nombre de la columna objetivo (target).
        evidencias (dict): Diccionario con evidencias generadas por EVA.
        recomendaciones (list[dict]): Lista de recomendaciones generadas por EVA.

    Returns:
        tuple: Una tupla que contiene:
            - fig (matplotlib.figure.Figure): Figura del dashboard 5x2.
            - summary (dict): Diccionario con el resumen estructurado de cada panel.
    """
    print("GENERANDO DASHBOARD 5x2 DEL EVA")

    fig = plt.figure(figsize=(16, 24))
    numeric_cols = get_columnas_numericas(df)[:20]

    summary: dict[str, Any] = {
        "target_col": target_col,
        "total_registros": len(df),
        "total_variables": len(df.columns),
        "panel_top_correlaciones": [],
        "panel_nulos": [],
        "panel_target": {},
        "panel_vif_top": [],
        "panel_recomendaciones": [],
    }

    # COLUMNA 1

    # 1. Heatmap de correlaciones
    ax1 = plt.subplot(5, 2, 1)
    if len(numeric_cols) > 1:
        corr_matrix = np.corrcoef(df.select(numeric_cols).to_numpy(), rowvar=False)
        sns.heatmap(
            corr_matrix,
            ax=ax1,
            cmap="RdBu_r",
            center=0,
            xticklabels=False,
            yticklabels=False,
        )
    ax1.set_title("Matriz de Correlacion", fontsize=11)

    # 3. VIF Analysis
    ax3 = plt.subplot(5, 2, 3)
    if "vif" in evidencias and len(evidencias["vif"]) > 0:
        try:
            vif_data = pl.DataFrame(evidencias["vif"])
            vif_top = vif_data.sort("VIF", descending=True).head(8)
            if len(vif_top) > 0:
                colors = [
                    "red" if v > 10 else "orange" if v > 5 else "green" for v in vif_top["VIF"]
                ]
                ax3.barh(range(len(vif_top)), vif_top["VIF"], color=colors)
                ax3.set_yticks(range(len(vif_top)))
                ax3.set_yticklabels(vif_top["variable"].to_list(), fontsize=8)
                ax3.axvline(x=10, color="red", linestyle="--", alpha=0.7, label="VIF=10")
                ax3.axvline(x=5, color="orange", linestyle="--", alpha=0.7, label="VIF=5")
                ax3.legend(fontsize=8)
                summary["panel_vif_top"] = [
                    {"variable": r["variable"], "vif": float(r["VIF"])}
                    for r in vif_top.iter_rows(named=True)
                ]
        except Exception:
            ax3.text(0.5, 0.5, "Error VIF", ha="center", va="center", transform=ax3.transAxes)
    ax3.set_title("VIF (Multicolinealidad)", fontsize=11)

    # 5. Variable vs target (boxplot)
    ax5 = plt.subplot(5, 2, 5)
    plot_var = None
    for candidate in [
        "tasa_judicial",
        "creditos_judiciales",
        "total_costo_judicial",
        "mora_promedio",
        "saldo_promedio",
    ]:
        if candidate in df.columns:
            plot_var = candidate
            break
    if plot_var and target_col in df.columns:
        try:
            data_plot = df.select([plot_var, target_col]).drop_nulls()
            positions = sorted(data_plot[target_col].unique().to_list())
            box_data = [
                data_plot.filter(pl.col(target_col) == p)[plot_var].to_numpy() for p in positions
            ]
            ax5.boxplot(
                box_data,
                positions=positions,
                patch_artist=True,
                boxprops=dict(facecolor="lightblue"),
                medianprops=dict(color="red", linewidth=2),
            )
            ax5.set_xlabel("Crisis Flag")
            ax5.set_ylabel(plot_var)
        except Exception:
            ax5.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax5.transAxes)
    ax5.set_title(f"{plot_var or 'N/D'} vs Target", fontsize=11)

    # 7. Distribucion temporal de crisis
    ax7 = plt.subplot(5, 2, 7)
    if "mes" in df.columns and target_col in df.columns:
        try:
            crisis_temp = (
                df.group_by(df["mes"].alias("periodo"))
                .agg(
                    [
                        pl.col(target_col).mean().alias("mean"),
                        pl.col(target_col).count().alias("count"),
                    ]
                )
                .sort("periodo")
            )
            if len(crisis_temp) > 0:
                x_vals = crisis_temp["periodo"].cast(pl.String).to_list()
                y_vals = crisis_temp["mean"].to_list()
                ax7.plot(x_vals, y_vals, color="darkred", marker="o", markersize=2, linewidth=1)
                media = crisis_temp["mean"].to_numpy().mean()
                ax7.axhline(
                    y=media, color="blue", linestyle="--", alpha=0.7, label=f"Media: {media:.3f}"
                )
                ax7.legend(fontsize=8)
                ax7.tick_params(axis="x", rotation=45, labelsize=6)
                for i, label in enumerate(ax7.get_xticklabels()):
                    if i % 12 != 0:
                        label.set_visible(False)
                summary["panel_tasa_crisis_temporal"] = {"media": float(media)}
        except Exception:
            ax7.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax7.transAxes)
    ax7.set_title("Tasa Crisis Temporal", fontsize=11)

    # 9. AUC-ROC por variable
    ax9 = plt.subplot(5, 2, 9)
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
            colors = [
                "#2ecc71" if v > 0.7 else "#f39c12" if v > 0.5 else "#e74c3c"
                for v in sorted_auc.values()
            ]
            ax9.barh(list(sorted_auc.keys()), list(sorted_auc.values()), color=colors)
            ax9.set_xlabel("|AUC-0.5|x2")
            ax9.invert_yaxis()
            ax9.axvline(x=0.5, color="gray", linestyle="--", alpha=0.5)
            ax9.tick_params(labelsize=8)
            summary["panel_auc_roc_variable"] = [
                {"variable": k, "auc_norm": float(v)} for k, v in sorted_auc.items()
            ]
    except Exception:
        ax9.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax9.transAxes)
    ax9.set_title("Poder Discriminativo (AUC-ROC)", fontsize=11)

    # COLUMNA 2
    # 2. Top correlaciones con target
    ax2 = plt.subplot(5, 2, 2)
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
                ax2.barh(list(corr_target.keys()), list(corr_target.values()), color=colors)
                ax2.set_xlabel("|r|")
                ax2.invert_yaxis()
                ax2.tick_params(labelsize=8)
                summary["panel_top_correlaciones"] = [
                    {"variable": k, "corr_abs": float(v)} for k, v in corr_target.items()
                ]
        except Exception:
            ax2.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax2.transAxes)
    ax2.set_title("Top 10 Correlaciones con Target", fontsize=11)

    # 4. Resumen de recomendaciones (pie)
    ax4 = plt.subplot(5, 2, 4)
    if recomendaciones:
        try:
            df_rec = pl.DataFrame(recomendaciones)
            decision_counts = df_rec["recomendacion"].value_counts()
            if len(decision_counts) > 0:
                color_map = {
                    "✅ INCLUIR": "#2ecc71",
                    "❌ EXCLUIR": "#e74c3c",
                    "MANTENER": "#3498db",
                    "⚠️ EXCLUIR": "#e67e22",
                    "⚠️ EVALUAR (conflicto)": "#f39c12",
                    "🔍 EVALUAR MANUALMENTE": "#95a5a6",
                    "⚠️ EVALUAR": "#f1c40f",
                }
                colors = [
                    color_map.get(idx, "#95a5a6")
                    for idx in decision_counts["recomendacion"].to_list()
                ]
                ax4.pie(
                    decision_counts["count"].to_list(),
                    labels=decision_counts["recomendacion"].to_list(),
                    colors=colors,
                    autopct="%1.1f%%",
                    startangle=90,
                    textprops={"fontsize": 8},
                )
                summary["panel_recomendaciones"] = [
                    {"recomendacion": r["recomendacion"], "count": int(r["count"])}
                    for r in decision_counts.iter_rows(named=True)
                ]
        except Exception:
            ax4.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax4.transAxes)
    ax4.set_title("Recomendaciones EVA", fontsize=11)

    # 6. Distribucion del target
    ax6 = plt.subplot(5, 2, 6)
    if target_col in df.columns:
        value_counts = df[target_col].value_counts()
        if len(value_counts) > 0:
            labels = value_counts[target_col].to_list()
            counts = value_counts["count"].to_list()
            ax6.bar(labels, counts, color=["#2ecc71", "#e74c3c"])
            ax6.set_xlabel("Crisis Flag")
            ax6.set_ylabel("Frecuencia")
            for i, v in enumerate(counts):
                ax6.text(i, v + 50, f"{v:,}", ha="center", fontsize=9)
            summary["panel_target"] = {
                "labels": [int(x) if isinstance(x, (int, float)) else str(x) for x in labels],
                "counts": [int(x) for x in counts],
            }
    ax6.set_title("Distribucion Target", fontsize=11)

    # 8. Resumen estadistico (texto)
    ax8 = plt.subplot(5, 2, 8)
    ax8.axis("off")
    n_crisis = int(df[target_col].sum()) if target_col in df.columns else 0
    n_total = len(df)
    pct_crisis = as_float(df[target_col].mean()) * 100 if target_col in df.columns else 0
    n_vif = len([v for v in summary.get("panel_vif_top", []) if v["vif"] > 10])
    n_inc = sum(1 for r in recomendaciones if "INCLUIR" in r.get("recomendacion", ""))
    n_exc = sum(1 for r in recomendaciones if "EXCLUIR" in r.get("recomendacion", ""))
    n_eva = sum(1 for r in recomendaciones if "EVALUAR" in r.get("recomendacion", ""))
    stats = (
        f"DATASET\n{'=' * 30}\n"
        f"Registros: {n_total:,}\n"
        f"Variables: {len(df.columns)}\n"
        f"Numericas: {len(numeric_cols)}\n"
        f"Target: {target_col}\n"
        f"Crisis: {n_crisis:,} ({pct_crisis:.1f}%)\n"
        f"No-crisis: {n_total - n_crisis:,}\n"
        f"{'=' * 30}\n"
        f"VIF>10: {n_vif}\n"
        f"INCLUIR: {n_inc}\n"
        f"EXCLUIR: {n_exc}\n"
        f"EVALUAR: {n_eva}"
    )
    ax8.text(
        0.05,
        0.95,
        stats,
        transform=ax8.transAxes,
        fontsize=10,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8),
    )
    ax8.set_title("Resumen Estadistico", fontsize=11)

    # 10. Densidad comparativa crisis vs no-crisis
    ax10 = plt.subplot(5, 2, 10)
    plot_col = None
    for candidate in [
        "tasa_judicial",
        "creditos_judiciales",
        "total_costo_judicial",
        "saldo_promedio",
    ]:
        if candidate in df.columns and target_col in df.columns:
            plot_col = candidate
            break
    if plot_col:
        try:
            vals_0 = df.filter(pl.col(target_col) == 0)[plot_col].to_numpy()
            vals_1 = df.filter(pl.col(target_col) == 1)[plot_col].to_numpy()
            if len(vals_0) > 0 and len(vals_1) > 0:
                ax10.hist(
                    vals_0, bins=40, alpha=0.5, label="No crisis", color="#2ecc71", density=True
                )
                ax10.hist(vals_1, bins=40, alpha=0.5, label="Crisis", color="#e74c3c", density=True)
                ax10.set_xlabel(plot_col, fontsize=9)
                ax10.set_ylabel("Densidad")
                ax10.legend(fontsize=8)
                ax10.set_yscale("log")
                summary["panel_densidad_top_feature"] = plot_col
        except Exception:
            ax10.text(0.5, 0.5, "Error", ha="center", va="center", transform=ax10.transAxes)
    ax10.set_title(f"Densidad: {plot_col or 'N/D'}", fontsize=11)

    plt.suptitle(
        "EVA - Analisis Exploratorio de Variables\nRiesgo Crediticio Multi-Horizonte",
        fontsize=14,
        fontweight="bold",
        y=1.005,
    )
    plt.tight_layout()
    return fig, summary
