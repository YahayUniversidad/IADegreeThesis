---
marp: true
theme: default
class: lead slide--tecnica
paginate: true
transition: fade
size: 16:9
style: |-
  h1 { color: #1a5276; }
  h2 { color: #2e86c1; }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }
  blockquote {
    border-left: 4px solid #2e86c1;
    padding-left: 1rem;
    color: #555;
  }
  table { font-size: 0.8em; }
  section {
    position: relative;
    padding-bottom: 52px;
    padding-top: 52px;
    font-family: 'Arial', sans-serif;
    justify-content: flex-start;
  }
  section.slide--tecnica {
    background: linear-gradient(rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.22)), url("tech.jpg") no-repeat center center / cover !important;
  }
  section.slide--negocio {
    background: linear-gradient(rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.22)), url("negocio.jpg") no-repeat center center / cover !important;
  }
  section.slide--negocio .negocio-card {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 24px;
    padding: 1.4rem 1.8rem;
    color: #1f2d3d;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    backdrop-filter: blur(3px);
    max-width: 90%;
  }
  section.slide--negocio .negocio-card h2,
  section.slide--negocio .negocio-card h3,
  section.slide--negocio .negocio-card p,
  section.slide--negocio .negocio-card strong {
    color: inherit;
  }

  section.slide--intro {
    background: linear-gradient(rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.22)), url("estadistica.jpg") no-repeat center center / cover !important;
  }
  section.slide--intro .negocio-card {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 24px;
    padding: 1.4rem 1.8rem;
    color: #1f2d3d;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    backdrop-filter: blur(3px);
    min-height: 77%;
    max-width: 90%;
  }
  section.slide--intro .negocio-card h2,
  section.slide--intro .negocio-card h3,
  section.slide--intro .negocio-card p,
  section.slide--intro .negocio-card strong {
    color: inherit;
  }
  section.slide--warning {
    background: linear-gradient(rgba(255, 255, 255, 0.22), rgba(255, 255, 255, 0.22)), url("warning.jpg") no-repeat center center / cover !important;

    padding-top: 90px;
  }
  section.slide--warning .negocio-card {
    background: rgba(255, 255, 255, 0.8);
    border-radius: 24px;
    padding: 1.4rem 1.8rem;
    color: #1f2d3d;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
    backdrop-filter: blur(3px);
    min-height: 77%;
    max-width: 90%;
  }
  section.slide--warning .negocio-card h2,
  section.slide--warning .negocio-card h3,
  section.slide--warning .negocio-card p,
  section.slide--warning .negocio-card strong {
    color: inherit;
  }
  section::after {
    content: "";
    position: absolute;
    left: 0px;
    bottom: -45px;
    width: 1280px;
    height: 74px;
    background: url("image5.jpeg") no-repeat left center / contain;
    opacity: 0.95;
    pointer-events: none;
  }
---

<!-- _class: lead -->

# Sistema Integrado de Inteligencia de Negocio para la Predicción de Crisis Crediticias

## Trabajo de titulación

**Omar Vélez Bayas**  
omar.velez@yachaytech.edu.ec

Universidad Yachay Tech  
Maestría en Inteligencia Artificial

Agosto 2026

---

<!-- _class: lead -->

# 1. Introducción

---

<!-- _class: slide--intro -->
<div class="negocio-card">

## Contexto y Motivación

La **mora crediticia** es un indicador de riesgo que todo el sistema financiero debe controlar. Un índice saludable es **< 5%**, ya que un valor superior puede afectar la liquidez de la institución y su capacidad de otorgar nuevos créditos.

Las instituciones de **economía social y solidaria** administran grandes volúmenes de información crediticia, pero los indicadores se generan mediante procesos manuales y repositorios separados.

</div>

---

<!-- _class: slide--warning -->
<div class="negocio-card">

## Datos

La data fue proporcionada por la **Cooperativa de Ahorro y Crédito Jardín Azuayo** y contiene información de préstamos, amortizaciones y juicios desde el 2019 hasta el 2026.

La misma ya fue entregada con un proceso previo de **anonimizado**: sin datos de cuentas, ni información personal de los socios y clientes, en fiel cumplimiento con normas internas de seguridad y leyes vigentes.

### La media de registros es de 1.8 millones por año

</div>

---

<!-- _class: slide--warning -->
<div class="negocio-card">

## Planteamiento del Problema

Tres brechas identificadas:

1. **Brecha de datos:** no existe un flujo único para integrar, limpiar y agregar la información crediticia
2. **Brecha analítica:** los modelos no se comparan bajo un protocolo multi-horizonte común
3. **Brecha operativa:** los resultados del modelado no se registran, almacenan y visualizan de forma automatizada

</div>

---

## Pregunta de Investigación

> ¿Cómo integrar datos crediticios, modelos de aprendizaje automático y herramientas de inteligencia de negocio en un sistema automatizado que permita predecir crisis crediticias en múltiples horizontes temporales y visualizar los resultados para la toma de decisiones?

### Hipótesis

Un pipeline end-to-end que combine ETL automatizado, modelos multi-horizonte y dashboards interactivos permite generar predicciones accionables con rendimiento competitivo frente a enfoques individuales.

---

## Objetivos

### Objetivo General

Diseñar e implementar un sistema integrado de inteligencia de negocio para la predicción de crisis crediticias en el sector de economía social y solidaria.

### Objetivos Específicos

1. Construir un **pipeline ETL** automatizado con Apache Airflow
2. Diseñar un **datamart analítico** con esquema estrella en PostgreSQL
3. Evaluar **modelos de IA** (CNN, MLP, LightGBM) para predicción multi-horizonte
4. Implementar **dashboards interactivos** con Apache Superset
5. Automatizar **entrenamiento, inferencia y registro** con MLflow

---

<!-- _class: lead -->

# 2. Marco Teórico

---

## Conceptos Clave

| Concepto | Descripción |
|----------|-------------|
| **Riesgo crediticio** | Probabilidad de incumplimiento de obligaciones financieras |
| **Inteligencia de negocio** | Consolidación de datos en datamarts + dashboards |
| **Predicción multi-horizonte** | Estimación de probabilidad de crisis a 1, 2, …, 18 meses |
| **Clases desbalanceadas** | La clase positiva (crisis) es minoritaria en los datos |
| **Validación temporal** | Split cronológico para evitar fuga de información |
| **MLOps** | Automatización del ciclo de vida de modelos ML |

---

## Modelos Evaluados

| Modelo | Tipo | Salida |
|--------|------|--------|
| **CNN** | Red neuronal convolucional 1D | 18 neuronas sigmoid (h1–h18) |
| **MLP** | Perceptrón multicapa | 18 neuronas sigmoid (h1–h18) |
| **LightGBM** | Gradient boosting | 18 clasificadores independientes |

**Variable objetivo:** `crisis_flag` (score heurístico ≥ 4)

**Métricas de evaluación:** AUC-ROC, Precision, Recall, F1-Score

---

<!-- _class: lead -->

# 3. Estado del Arte

---

## Brechas Identificadas

| Brecha | Descripción |
|--------|-------------|
| **Multi-horizonte** | Pocos trabajos predicen simultáneamente en múltiples ventanas temporales |
| **Integración end-to-end** | La mayoría se enfoca en el modelo, no en el pipeline completo |
| **MLOps aplicado** | Escasa automatización de entrenamiento, registro e inferencia |
| **Visualización** | Limitada integración de predicciones en dashboards de negocio |

> **Posicionamiento:** este trabajo integra las tres brechas en un sistema reproducible y automatizado.

---

<!-- _class: lead -->

# 4. Metodología

---

## Arquitectura del Sistema

```bash
CSV (51 archivos) ──→ ETL ──→ PostgreSQL ──→ Datamart (Estrella)
                              │                    │
                              │                    ├──→ EVA (Análisis)
                              │                    │
                              │                    ├──→ CNN + MLP + LightGBM
                              │                    │         │
                              │                    │    MLflow (Tracking)
                              │                    │         │
                              │                    │    Predicciones (18 horizontes)
                              │                    │         │
                              │                    └──→ Superset (Dashboards)
```

**Stack:** Airflow · PostgreSQL · MLflow · TensorFlow · LightGBM · Polars · Superset

---

## ETL y Datamart

### ETL (Extracción, Transformación, Carga)

- **51 archivos CSV**: préstamos, amortizaciones, juicios (2015–2026)
- Carga masiva con `COPY` + proceso incremental `ON CONFLICT DO UPDATE`

### Datamart (Esquema Estrella)

| Dimensión / Hecho | Contenido |
|-------------------|-----------|
| `dim_tiempo` | Mes, año, trimestre |
| `dim_riesgo` | Código y descripción de riesgo |
| `dim_sector` | Código y descripción de sector |
| `dim_sucursal` | Sucursal y provincia |
| `fact_creditos_mensual` | 27 métricas por bloque |
| `fact_predicciones` | Predicciones multi-horizonte (56.541 filas) |

---

## Análisis EVA (Evaluación de Variables Analíticas)

### Módulo Python reutilizable

- `pipeline.py` — Orquestador EVA (modo notebook/MLflow)
- `analisis_riguroso.py` — Motor de análisis estadístico

| Métrica | Uso |
|---------|-----|
| Pearson, Spearman | Correlación lineal y monótona |
| VIF | Multicolinealidad |
| Chi-cuadrado | Asociación categórica |
| Cohen's d, t-test | Diferencia entre grupos |
| Shapiro-Wilk, KS | Normalidad |

**Dashboard 3×3:** heatmap de correlaciones, distribución target, boxplots de mora, VIF, recomendaciones automáticas (INCLUIR/EXCLUIR)

---

## EDA Optimizado

### Problema

La consulta SQL genera **12M+ registros** que agotan la memoria RAM.

### Solución implementada

- **Polars Lazy Mode:** `pl.read_database()` + `.lazy()` difiere la ejecución
- **Procesamiento por año:** extrae y agrega datos un año a la vez (2015–2025)
- **Agregación incremental:** solo materializa registros agregados (~miles)

**Resultado:** mismo CSV de salida, sin errores de memoria.

---

## Modelos Desarrollados: Arquitectura Multi-Horizonte

### Diseño propio (contribución de IA)

```
  Entrada (t-6 … t-1)        Tronco del modelo           Salida multi-horizonte
  ───────────────────        ─────────────────           ──────────────────────
  features del bloque   ┌─► CNN   Conv1D→BN→Dense(128/64) ─┐
  crediticio (6 meses)  ├─► MLP   Flatten→Dense(128/64)  ─┼─► 18 × sigmoid
  por sucursal/sector   └─► LGBM  18 boosters (1/horizonte)─┘    h1 … h18
                                                                     │
                                          P(crisis_flag | horizonte h)
```

| Modelo | Arquitectura diseñada | Multi-horizonte |
|--------|----------------------|-----------------|
| **CNN** | Conv1D(64)→BN→Conv1D(128)→BN→MaxPool→Dense(128)→Dense(64) | 18 × Dense(1, sigmoid) |
| **MLP** | Flatten→Dense(128, ReLU)→Dense(64, ReLU) | 18 × Dense(1, sigmoid) |
| **LightGBM** | Gradient boosting con `scale_pos_weight` por horizonte | 18 clasificadores independientes |

**Target:** `crisis_flag` (score ≥ 4) · **Pérdida:** binary cross-entropy con pesos por clase (desbalance)

### Nexo con la orquestación programada (Airflow)

| DAG | Cron | Flujo | Vinculación con los modelos |
|-----|------|-------|----------------------------|
| **DAG-Entrenamiento** | `0 3 1 * *` (mensual) | estructura → CSV → datamart → EDA/EVA → **[CNN ∥ MLP ∥ LGBM]** → selección (AUC) | Diseña y entrena las 18 cabezas multi-horizonte |
| **DAG-Inferencia** | `0 6 * * *` (diario) | estructura → CSV → datamart → **predicción** → Superset | Ejecuta el mejor modelo → `prob_h01`…`prob_h18` |

---

## Pipeline MLOps

1. **Entrenamiento** (`dag_entrenamiento.py`): CSV → EDA → CNN + MLP + LightGBM → MLflow
2. **Inferencia** (`dag_inferencia.py`): CSV → Datamart → Predicción → Superset
3. **Registro** (MLflow): métricas, artefactos, versionado de modelos

### Predicción Multi-Horizonte

- Modelo seleccionado genera `prob_h01` … `prob_h18`
- Predicciones se almacenan en `fact_predicciones`
- **LightGBM** seleccionado como mejor modelo

### Aprobación Humana

1. Modelo seleccionado genera predicciones multi-horizonte
2. Predicciones se guardan en `fact_predicciones`
3. **Humano en el loop:** experto revisa y aprueba/rechaza antes de producción

---

<!-- _class: lead -->

# 5. Resultados

---

## Comparación de Modelos

| Métrica | CNN | MLP | LightGBM |
|---------|-----|-----|----------|
| **AUC-ROC** | 0.85 | 0.84 | **0.87** |
| **Precision** | 0.82 | 0.81 | **0.84** |
| **Recall** | 0.79 | 0.78 | **0.81** |
| **F1-Score** | 0.80 | 0.79 | **0.82** |

**LightGBM** obtiene el mejor rendimiento global y fue seleccionado para producción.

---

## Dashboards de Superset

### 5 Dashboards implementados

| Dashboard | Contenido |
|-----------|-----------|
| Tendencia de Crisis | Evolución temporal por sucursal y sector |
| Predicciones de Crisis | Probabilidad de crisis por período |
| Resumen por Sucursal | Métricas agregadas (créditos, mora, judicial) |
| **Predicción por Horizonte** | Evolución por rango de plazo (corto/medio/largo) |
| **Comparación por Segmento** | Rangos por sucursal y sector + heatmap |

**Filtros interactivos:** rango de plazo, período, sucursal, sector

---

## Datamart y Predicciones

- **56.541 predicciones** almacenadas en `fact_predicciones`
- **18 horizontes mensuales** (`prob_h01` … `prob_h18`)
- **3 rangos de plazo:** corto (1–3M), medio (4–6M), largo (7–18M)
- **133 períodos** de datos, **65 sucursales**, **21 sectores**

### Vista analítica

`vw_predicciones_horizonte` — formato largo (1.017.738 filas) para visualización por horizonte

---

<!-- _class: lead -->

# 6. Conclusiones

---

## Contribuciones

1. **Sistema integrado end-to-end** que conecta ETL, datamart, modelos, MLOps y dashboards
2. **Comparación rigurosa** de CNN, MLP y LightGBM bajo protocolo multi-horizonte
3. **Pipeline automatizado** con Airflow + MLflow para entrenamiento e inferencia
4. **5 dashboards interactivos** con predicciones por rango de plazo y segmento
5. **Prototipo reproducible** escalable a otras cooperativas de economía social

---

## Limitaciones y Trabajo Futuro

### Limitaciones
- Datos de una sola cooperativa (Jardín Azuayo)
- Horizontes más allá de 18 meses no evaluados
- Clasificación binaria (crisis/no crisis) sin niveles de severidad

### Trabajo Futuro
- Extender a más instituciones del sector
- Incorporar modelos de series temporales (LSTM, Transformer)
- Implementar alertas automáticas basadas en predicciones
- Evaluar explicabilidad (SHAP) para toma de decisiones

---

<!-- _class: slide--negocio invert -->
<div class="negocio-card">

## Perspectivas Económicas

El sistema es un **producto reproducible, observable y escalable** para cooperativas e instituciones de economía social y solidaria.

Potencial de licenciamiento a comercios que otorguen crédito directo: almacenes de electrodomésticos, tiendas de muebles, tiendas departamentales.

</div>

---

<!-- _class: lead -->

# Preguntas

Gracias por su atención.

![icon](yachayCuadrado.jpg)<br/>**Omar Vélez Bayas**<br/>omar.velez@yachaytech.edu.ec
