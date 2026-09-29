# Proposal

## Why

El modelo seleccionado (LightGBM) genera predicciones de crisis en 18 horizontes mensuales (`prob_h01`…`prob_h18`) que ya están en `fact_predicciones`, pero Superset solo visualiza agregados (`prob_media`, `pred_media`). No hay dashboards que permitan ver la predicción por rangos de tiempo (corto / mediano / largo plazo) ni compararla por sucursal o sector.

## What Changes

- Crear un dataset largo (un fila por predicción × horizonte) que exponga horizonte, rango de plazo y probabilidad de crisis.
- Crear dos dashboards nuevos en Superset, conservando los tres existentes:
  1. **Predicción por Horizonte Temporal** — evolución de la probabilidad de crisis por rango de plazo (corto 1–3M, medio 4–6M, largo 7–18M) en el tiempo.
  2. **Comparación de Rangos por Segmento** — comparación de los rangos de plazo por sucursal y sector.
- Filtros de rango de tiempo y de período en ambos dashboards.

## Capabilities

### New Capabilities

_(ninguna)_

### Modified Capabilities

- `superset-visualization`: nuevos requisitos de dashboards de predicción por horizonte temporal y comparación por segmento; dataset de horizontes para visualización.

## Impact

- **Superset**: 1 dataset virtual nuevo (o vista SQL), 6–8 charts nuevos, 2 dashboards publicados. Los dashboards 10–12 actuales se conservan sin cambios.
- **PostgreSQL (`ts_train`)**: posible vista `vw_predicciones_horizonte` en `public` para desnormalizar horizontes; no modifica tablas base.
- **Airflow / pipelines**: sin cambios (la data ya se escribe en `fact_predicciones`).
- **API Superset**: se puede crear todo vía API/SQL con la conexión existente (`localhost:5434` + Superset admin).
