# Dashboards creados — add-prediction-horizon-dashboards

## Vista SQL

- **`public.vw_predicciones_horizonte`** — formato largo (1 fila por predicción × horizonte), 1.017.738 filas.
  - Columnas clave: `horizonte` (1–18), `rango_plazo` (corto/medio/largo), `probabilidad`, `prediccion`, `mes`, `anio`, `nombre_sucursal`, `nombre_sector`.
  - Clasificación: corto = h01–h03, medio = h04–h06, largo = h07–h18.

## Dataset en Superset

- **id=28** — `vw_predicciones_horizonte` (esquema `public`, base `ts_train`).

## Dashboard 1 — Predicción por Horizonte Temporal

- **id:** 13 · **slug:** `prediccion-horizonte-temporal` · **publicado:** sí

| Chart id | Nombre | Tipo | Contenido |
|----------|--------|------|-----------|
| 110 | Evolución Prob Crisis por Rango de Plazo | `echarts_timeseries_line` | AVG(`probabilidad`) por `mes`, serie = `rango_plazo` |
| 111 | Predicciones Positivas por Rango y Período | `echarts_timeseries_bar` | SUM(`prediccion`) filtrado a `prediccion`=1 por `mes`, serie = `rango_plazo` |
| 112 | Prob Promedio Corto Plazo (1-3M) | `big_number_total` | AVG(`probabilidad`) con filtro `rango_plazo`=`corto` |
| 113 | Prob Promedio Medio Plazo (4-6M) | `big_number_total` | AVG(`probabilidad`) con filtro `rango_plazo`=`medio` |
| 114 | Prob Promedio Largo Plazo (7-18M) | `big_number_total` | AVG(`probabilidad`) con filtro `rango_plazo`=`largo` |

**Filtros nativos:** Rango de Plazo (select múltiple), Año (select múltiple).

## Dashboard 2 — Comparación de Rangos por Segmento

- **id:** 14 · **slug:** `comparacion-rangos-segmento` · **publicado:** sí

| Chart id | Nombre | Tipo | Contenido |
|----------|--------|------|-----------|
| 115 | Prob Crisis por Sucursal y Rango | `echarts_timeseries_bar` | AVG(`probabilidad`) por `nombre_sucursal`, serie = `rango_plazo` |
| 116 | Prob Crisis por Sector y Rango | `echarts_timeseries_bar` | AVG(`probabilidad`) por `nombre_sector`, serie = `rango_plazo` |
| 117 | Heatmap Sucursal x Rango de Plazo | `heatmap` | `nombre_sucursal` × `rango_plazo`, valor = AVG(`probabilidad`) |

**Filtros nativos:** Rango de Plazo (select múltiple), Año (select múltiple).

## Notas de datos

- Los tres rangos tienen datos históricos 2016–2025. Para 2026–2027 el modelo solo predice horizontes largos (`largo`), por lo que `corto` y `medio` aparecen vacíos en esos períodos — comportamiento esperado, no un error de la vista.
- Los dashboards 10–12 (Tendencia de Crisis, Predicciones de Crisis, Resumen por Sucursal) permanecen sin cambios.

## URLs

- Dashboard temporal: `http://localhost:8088/superset/dashboard/prediccion-horizonte-temporal/`
- Dashboard segmentos: `http://localhost:8088/superset/dashboard/comparacion-rangos-segmento/`
