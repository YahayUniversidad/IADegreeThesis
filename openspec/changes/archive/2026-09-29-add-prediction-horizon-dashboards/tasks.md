# Tasks

## 1. Vista de horizontes en PostgreSQL

- [x] 1.1 Crear `public.vw_predicciones_horizonte` (idempotente, `CREATE OR REPLACE VIEW`) con `CROSS JOIN LATERAL (VALUES …)` que despivote `prob_h01`…`prob_h18` / `pred_h01`…`pred_h18` y exponga `horizonte`, `rango_plazo` (corto/medio/largo), `probabilidad`, `prediccion`, período, sucursal y sector — verificar con `SELECT COUNT(*) FROM vw_predicciones_horizonte` ≈ 56.541 × 18 y `SELECT DISTINCT rango_plazo` = {corto, medio, largo}
- [x] 1.2 Validar clasificación de rangos y cobertura de 18 horizontes por fila de origen — verificar con consultas que `horizonte BETWEEN 1 AND 3 → corto`, `4–6 → medio`, `7–18 → largo`, y que cada `bloque_id`+período tiene exactamente 18 filas
- [x] 1.3 (Opcional, solo si es lento) Agregar índice de soporte a la vista y re-medir — verificar con `EXPLAIN ANALYZE` de la consulta de promedio por rango y período

## 2. Dataset en Superset

- [x] 2.1 Registrar `vw_predicciones_horizonte` como dataset en Superset vía API (`POST /api/v1/dataset/`) usando variables de entorno para credenciales — verificar con `GET /api/v1/dataset/` que el dataset aparece y expone las columnas esperadas
- [x] 2.2 Confirmar que las columnas `rango_plazo`, `anio`, `mes`, `nombre_sucursal`, `nombre_sector`, `probabilidad` son consultables desde el SQL Lab de Superset — verificar con una consulta de promedio de `probabilidad` agrupada por `rango_plazo` que retorne 3 filas

## 3. Dashboard 1 — Predicción por Horizonte Temporal

- [x] 3.1 Crear chart de línea: promedio de `probabilidad` por `anio`-`mes`, serie = `rango_plazo` — verificar que el chart renderiza 3 series y datos en el eje temporal
- [x] 3.2 Crear chart de barras/área: conteo de predicciones positivas (`prediccion`=1) por período y `rango_plazo` — verificar que muestra el desglose por los 3 rangos
- [x] 3.3 Crear indicadores (big numbers) de probabilidad promedio actual por cada rango de plazo — verificar 3 indicadores (corto/medio/largo) con valores numéricos
- [x] 3.4 Crear el dashboard "Predicción por Horizonte Temporal" con los charts anteriores y filtros de `rango_plazo` y período (`anio`/`mes`) — verificar que abrir el dashboard carga los charts y que aplicar cada filtro actualiza las visualizaciones

## 4. Dashboard 2 — Comparación de Rangos por Segmento

- [x] 4.1 Crear chart de barras horizontales: promedio de `probabilidad` por `nombre_sucursal`, serie = `rango_plazo` (top N sucursales) — verificar que muestra la comparación entre sucursales con los 3 rangos
- [x] 4.2 Crear chart de barras: promedio de `probabilidad` por `nombre_sector`, serie = `rango_plazo` — verificar que muestra la comparación entre sectores con los 3 rangos
- [x] 4.3 Crear chart de heatmap o tabla: `nombre_sucursal` × `rango_plazo` con probabilidad promedio — verificar que la matriz se renderiza con valores por celda
- [x] 4.4 Crear el dashboard "Comparación de Rangos por Segmento" con los charts anteriores y filtros de `rango_plazo` y período — verificar que abrir el dashboard carga los charts y que aplicar cada filtro actualiza las visualizaciones

## 5. Verificación integral

- [x] 5.1 Verificar que los dashboards 10–12 (Tendencia de Crisis, Predicciones de Crisis, Resumen por Sucursal) siguen funcionando sin cambios — verificar abriendo cada uno y confirmando que sus charts cargan con datos
- [x] 5.2 Verificar el flujo de actualización: ejecutar una consulta que confirme que los nuevos dashboards leen de `fact_predicciones` (misma fuente que el DAG de inferencia actualiza) — verificar con `SELECT MAX(fecha_ejecucion) FROM fact_predicciones` coincidente con los datos visibles en los dashboards
- [x] 5.3 Documentar en el README o en la carpeta del cambio los dos dashboards creados (nombre, slug, charts, filtros) — verificar que el documento existe y describe ambos dashboards
