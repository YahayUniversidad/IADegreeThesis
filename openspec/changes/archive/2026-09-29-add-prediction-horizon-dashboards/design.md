# Design

## Context

Ver `proposal.md` — Why. Resumen operativo del estado actual:

- `fact_predicciones` (public, 56.541 filas) guarda las 18 probabilidades mensuales en formato ancho (`prob_h01`…`prob_h18`, `pred_h01`…`pred_h18`) más agregados (`prob_media`, `pred_media`, `crisis_count`).
- Superset (puerto 8088) ya tiene 3 datasets virtuales SQL (`vw_tendencia_crisis`, `vw_predicciones_crisis`, `vw_resumen_sucursal`) y 3 dashboards (ids 10–12). Ninguno expone horizontes individuales.
- Dimensiones disponibles: `dim_tiempo` (mes, anio, trimestre, nombre_mes), `dim_sucursal` (codigo_sucursal, codigo_provincia), `dim_sector` (codigo_sector, descripcion), `dim_riesgo`.
- No hay scripts de creación programática de dashboards; los actuales se crearon vía UI/API. El DAG de inferencia tiene un TODO de refresh de Superset.
- Acceso disponible: `psql` vía `docker exec postgres_persistencia` y API REST de Superset (`/api/v1/...`) con admin.

## Goals / Non-Goals

**Goals:**

- Exponer los 18 horizontes en formato largo consultable desde Superset.
- Dos dashboards nuevos: evolución temporal por rango de plazo y comparación por segmento.
- Filtros de rango de plazo y período en ambos dashboards.
- Creación reproducible vía API REST de Superset + SQL, sin tocar los dashboards existentes.

**Non-Goals:**

- Modificar pipelines de inferencia o Airflow (la data ya se escribe en `fact_predicciones`).
- Cambiar el modelo LightGBM ni recalcular predicciones.
- Agregar nuevos horizontes distintos de 1–18.
- Permisos/roles granulares más allá de los existentes.

## Decisions

### D1: Vista SQL en PostgreSQL (`vw_predicciones_horizonte`) en lugar de dataset virtual de Superset

**Decisión**: Crear la vista en `public.vw_predicciones_horizonte` y registrarla como dataset en Superset.

**Razón**: El formato largo multiplica ×18 las filas (~1,02 M). Un dataset virtual re-ejecuta el SQL en cada consulta de chart; una vista materializa el plan en PostgreSQL y permite índices si hiciera falta. Además, la vista es reutilizable fuera de Superset (chatbot RAG, notebooks, MCP).

**Alternativa considerada**: Dataset virtual SQL en Superset (patrón de los datasets 25–27). Se descarta por volumen y por no ser reutilizable. Si en implementación se prefiere consistencia con el patrón actual, un dataset virtual sigue siendo funcionalmente correcto; la vista solo es preferible por rendimiento y reuso.

### D2: Despivotar con `CROSS JOIN LATERAL (VALUES …)`

**Decisión**: Usar un bloque `VALUES` con las 18 tuplas `(horizonte, prob, pred)` lateral a `fact_predicciones`.

**Razón**: Explícito, portable y legible; el planificador genera un simple append. `generate_series` + índice de array es más corto pero menos obvio y depende de construir arrays. `UNION ALL` ×18 es verboso y más lento de parsear.

### D3: Clasificación de rangos en la vista (no en el chart)

**Decisión**: La vista expone `rango_plazo` con la clasificación fija: `corto` (h01–h03), `medio` (h04–h06), `largo` (h07–h18).

**Razón**: Un solo lugar de verdad; los charts solo filtran/agregan. Si mañana cambian los cortes, se altera la vista y ambos dashboards se actualizan sin reconfigurar charts.

### D4: Creación de charts y dashboards vía API REST de Superset

**Decisión**: Script (o secuencia de llamadas `curl`/Python) que use `/api/v1/dataset/`, `/api/v1/chart/`, `/api/v1/dashboard/` con el token de admin.

**Razón**: Reproducible, auditable y versionable en el repo. La UI manual no deja rastro. El patrón de auth (`/api/v1/security/login`) ya está probado en este entorno.

**Alternativa considerada**: Exportar/importar JSON de dashboard. Más frágil entre versiones de Superset y difícil de mantener a mano.

### D5: Tipos de chart

**Dashboard 1 — Predicción por Horizonte Temporal**:

- Línea: promedio de `probabilidad` por `anio-mes`, serie = `rango_plazo` (3 series).
- Área apilada o barras: distribución de predicciones (`prediccion`=1) por rango y período.
- Big number / indicadores: prob_media actual por rango (corto/medio/largo).

**Dashboard 2 — Comparación de Rangos por Segmento**:

- Barras horizontales: promedio de `probabilidad` por `nombre_sucursal`, serie = `rango_plazo` (top N sucursales).
- Barras: promedio de `probabilidad` por `nombre_sector`, serie = `rango_plazo`.
- Heatmap o tabla: sucursal × rango de plazo con la probabilidad promedio.

Ambos dashboards con filtros nativos de Superset sobre `rango_plazo` y `anio`/`mes`.

## Risks / Trade-offs

- [Rendimiento de la vista ~1 M filas] → Agregar índice en `(id_tiempo, rango_plazo)` o `INCLUDE (probabilidad)` si las consultas son lentas; los filtros de Superset se empujan a PostgreSQL. Mitigación: limitar charts a promedios agregados, no a filas crudas.
- [La API de Superset varía entre versiones] → Fijar el contrato contra la versión del contenedor `local/superset-postgres:latest` desplegada; validar con `GET /api/v1/dashboard/` antes de crear. Si un endpoint falla, fallback documentado a UI.
- [Los cortes de rango (3/6/18) son una decisión de negocio] → Quedan centralizados en la vista (D3); cambiarlos es un `CREATE OR REPLACE VIEW`.
- [Los dashboards 10–12 podrían romperse si se tocan datasets compartidos] → No se modifica ningún dataset ni chart existente; solo se crean objetos nuevos.
- [Credenciales admin en scripts] → El script no debe commitear secrets; usar variables de entorno (`SUPERSET_URL`, `SUPERSET_USER`, `SUPERSET_PASSWORD`) ya presentes en `Contenedores/ts_superset/.env`.

## Migration Plan

1. Crear `vw_predicciones_horizonte` en PostgreSQL (idempotente con `CREATE OR REPLACE VIEW`).
2. Registrar el dataset en Superset vía API (o UI si la API de dataset requiere pasos manuales).
3. Crear charts del Dashboard 1, luego el Dashboard 1.
4. Crear charts del Dashboard 2, luego el Dashboard 2.
5. Verificar: ambos dashboards cargan con datos; los dashboards 10–12 siguen funcionando; filtros de rango y período responden.

**Rollback**: `DROP VIEW IF EXISTS public.vw_predicciones_horizonte;` + eliminar charts/dashboards nuevos vía API. Los objetos existentes no se tocan.

## Open Questions

- ¿Conviene materializar la vista (`MATERIALIZED VIEW` + refresh en el DAG) si la latencia de los charts supera ~2 s? Se puede decidir después midiendo; no cambia specs ni tareas iniciales.
- ¿Los dashboards deben ser visibles para el rol `Gamma` (solo lectura) desde el inicio? Por ahora se publican con el acceso por defecto de admin; ajustar permisos es un cambio de configuración menor.
