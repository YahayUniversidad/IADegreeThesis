# Dashboards de Superset — Sistema de Inteligencia Crediticia

## Visión General

El sistema cuenta con 4 dashboards en Apache Superset que visualizan el portafolio de crédito de una cooperativa, las predicciones de crisis generadas por LightGBM, y análisis dimensionales para la toma de decisiones.

### Fuentes de datos

| Vista SQL | Tabla fuente | Descripción |
|-----------|-------------|-------------|
| `v_creditos` | `fact_creditos_mensual` + 4 dimensiones | Histórico de créditos con métricas mensuales |
| `v_predicciones` | `fact_predicciones` + 4 dimensiones | Predicciones LightGBM multi-horizonte |

### Dimensiones del datamart (estrella)

| Dimensión | Columna clave | Descripción |
|-----------|---------------|-------------|
| `dim_tiempo` | `mes` | Fecha, año, trimestre, nombre del mes |
| `dim_riesgo` | `codigo_riesgo` | Nivel de riesgo del crédito |
| `dim_sector` | `codigo_sector` | Sector económico del deudor |
| `dim_sucursal` | `codigo_sucursal` | Sucursal de la cooperativa |

---

## Dashboard 1: Histórico de Créditos

**Fuente:** `v_creditos`
**Propósito:** Visualizar la evolución temporal del portafolio de crédito de la cooperativa.

| # | Chart | Tipo | Descripción | SQL |
|---|-------|------|-------------|-----|
| 1 | **Evolución de Créditos** | Línea temporal | Cantidad total de créditos otorgados por mes. Muestra la tendencia del portafolio. Si sube, la cooperativa está otorgando más créditos. Si baja, se está contrayendo. | `SUM(num_creditos)` agrupado por `mes` |
| 2 | **Monto Total Promedio** | Línea temporal | Monto promedio de cada crédito por mes. Indica si los créditos están siendo más grandes o más pequeños con el tiempo. Un aumento puede significar mayor exposición al riesgo. | `AVG(monto_total)` por `mes` |
| 3 | **Tasa de Mora 90+** | Línea temporal | Porcentaje promedio de créditos con más de 90 días de mora. Es el indicador principal de cartera vencida. Si sube, la calidad del portafolio está deteriorándose. | `AVG(tasa_mora_90)` por `mes` |
| 4 | **Crisis por Mes** | Barras temporales | Cantidad de bloques (combinación riesgo+sector+sucursal) que entraron en "crisis" cada mes. Un bloque entra en crisis cuando acumula ≥5 puntos en 11 reglas de scoring (mora, judiciales, crecimiento, etc.). | `SUM(crisis_flag)` por `mes` |
| 5 | **Créditos por Sector** | Pie chart | Distribución porcentual del total de créditos por sector económico. Muestra la concentración del portafolio. Si un sector domina mucho, hay riesgo de concentración. | `SUM(num_creditos)` agrupado por `sector` |
| 6 | **Top Sucursales por Monto** | Tabla | Las 10 sucursales con mayor monto total de créditos. Identifica qué sucursales manejan más dinero y podrían tener mayor impacto si tienen problemas. | `SUM(monto_total)` por `codigo_sucursal`, top 10 |

---

## Dashboard 2: Predicciones Crediticias

**Fuente:** `v_predicciones`
**Propósito:** Visualizar las predicciones del modelo LightGBM multi-horizonte.

### Pipeline de predicción

El modelo LightGBM genera predicciones mediante el siguiente flujo:

1. **Preprocesamiento:** Toma los datos preprocesados del EDA (`datos_preprocesados.csv`)
2. **Feature engineering:** Genera features estadísticas — 7 estadísticas (mean, std, min, max, median, last, trend) por cada una de las 21 features base = 147 features totales
3. **Entrenamiento:** 18 modelos LightGBM independientes (uno por horizonte de 1-18 meses), con early stopping y `scale_pos_weight` para manejar desbalanceo de clases
4. **Predicción:** Cada modelo predice la probabilidad de crisis para cada bloque a su horizonte correspondiente
5. **Agregación:** Se calcula `prob_media` (promedio de las 18 probabilidades) y `pred_media` (0 o 1 basado en prob_media > 0.5)

### Métricas del modelo

| Métrica | Horizonte 1 | Horizonte 18 | Promedio |
|---------|-------------|--------------|----------|
| Accuracy | 0.94 | 0.90 | 0.92 |
| Precision | 0.69 | 0.50 | 0.57 |
| Recall | 0.54 | 0.03 | 0.39 |
| AUC-ROC | 0.87 | 0.70 | 0.80 |

| # | Chart | Tipo | Descripción | SQL |
|---|-------|------|-------------|-----|
| 1 | **Probabilidad Promedio de Crisis** | Línea temporal | La probabilidad media de crisis de TODOS los bloques por mes. Si sube, el modelo detecta condiciones adversas generalizadas. Si baja, las condiciones mejoran. | `AVG(prob_media)` por `mes_prediccion` |
| 2 | **Predicciones de Crisis por Mes** | Barras temporales | Cuántos bloques fueron clasificados como "en crisis" (`pred_media=1`) cada mes. Es el conteo de alertas activas del modelo. | `SUM(pred_media)` por `mes_prediccion` |
| 3 | **Top Bloques en Riesgo** | Tabla | Los 20 bloques con mayor probabilidad promedio de crisis. Identifica qué combinación riesgo+sector+sucursal tiene peor pronóstico. | `AVG(prob_media)` por `bloque_id`, top 20 |

---

## Dashboard 3: KPIs Generales

**Fuente:** `v_creditos` + `v_predicciones`
**Propósito:** Resumen ejecutivo con 4 indicadores clave para la gerencia.

| # | Chart | Tipo | Descripción | SQL |
|---|-------|------|-------------|-----|
| 1 | **Total Créditos** | Big Number | Número total de registros de crédito en el histórico. Es el volumen total del portafolio analizado. | `COUNT(*)` de `v_creditos` |
| 2 | **Créditos con Crisis** | Big Number | Suma total de meses donde bloques entraron en crisis (`crisis_flag=1`). Acumulado de toda la historia. | `SUM(crisis_flag)` de `v_creditos` |
| 3 | **Total Predicciones** | Big Number | Cantidad total de predicciones generadas (bloques × meses). Cada fila es un bloque predicho para un mes específico. | `COUNT(*)` de `v_predicciones` |
| 4 | **Probabilidad Promedio** | Big Number | Probabilidad media de crisis de todas las predicciones. Si es alta (>0.3), el modelo ve riesgo generalizado. Si es baja (<0.1), las condiciones son favorables. | `AVG(prob_media)` de `v_predicciones` |

---

## Dashboard 4: Análisis Dimensional

**Fuente:** `v_creditos`
**Propósito:** Cruce de métricas con las dimensiones del datamart para análisis por segmento.

| # | Chart | Tipo | Descripción | SQL |
|---|-------|------|-------------|-----|
| 1 | **Créditos por Riesgo** | Tabla | Total de créditos agrupados por nivel de riesgo. Muestra la distribución del portafolio por clasificación de riesgo. | `SUM(num_creditos)` por `riesgo` |
| 2 | **Mora por Sector** | Tabla | Tasa de mora 90+ promedio por sector económico. Identifica qué sectores tienen peor comportamiento de pago. Los sectores con mora alta son candidatos a restricción de crédito. | `AVG(tasa_mora_90)` por `sector` |
| 3 | **Evolución por Riesgo** | Línea temporal | Cómo evoluciona el número de créditos por nivel de riesgo a lo largo del tiempo. Muestra si ciertos niveles de riesgo están creciendo o reduciéndose. | `SUM(num_creditos)` por `mes` × `riesgo` |

---

## Arquitectura del sistema

```
PostgreSQL (raw)
    ↓
ETL.ipynb (extracción y limpieza)
    ↓
mv_creditos_mensuales (vista materializada)
    ↓
EDA.ipynb (21 features → datos_preprocesados.csv)
    ↓
LightGBM (18 modelos → fact_predicciones)
    ↓
Superset (4 dashboards)
```

### Componentes

| Componente | Tecnología | Función |
|------------|-----------|---------|
| Base de datos | PostgreSQL 15 | Almacenamiento de datos raw y datamart |
| ETL | Python + Polars | Extracción y transformación de datos |
| EDA | Python + Polars | Análisis exploratorio, cálculo de features |
| Modelo | LightGBM | Predicción de crisis multi-horizonte |
| Visualización | Apache Superset 6.1 | Dashboards interactivos |
| Orquestación | Apache Airflow | Ejecución programada de DAGs |
| Tracking | MLflow | Registro de experimentos y métricas |

---

## Datos técnicos

- **Servidor Superset:** `http://localhost:8088` (desarrollo), `http://192.168.0.97:8088` (producción)
- **Base de datos:** `postgres_db` en puerto 5432
- **Usuario Superset:** `admin`
- **Script de creación:** `src/ts_superset/mcpDashboards.py`
- **Vistas SQL:** `v_creditos`, `v_predicciones` (creadas automáticamente por el script)

---

*Documento generado para la tesis de maestría — julio 2026*
