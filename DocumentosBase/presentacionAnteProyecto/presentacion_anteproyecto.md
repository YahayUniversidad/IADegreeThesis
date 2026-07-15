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

# Sistema Integrado de Inteligencia de Negocio Crediticio para el Control de la Mora

## Participación con la colectividad

**Omar Velez**  
omar.velez@yachaytech.edu.ec

Universidad Yachay Tech  
Maestría en Inteligencia Artificial

Julio 2026

---

<!-- _class: slide--intro -->
<div class="negocio-card">

## MORA

La mora crediticia es un problema que a todo el sistema financiero nacional le afecta, y es un indicador de riesgo que se debe controlar.

Un indice saludable de mora para instituciones financieras es **< 5% debido a lo significativo que es este indice en relación a las utilidades**.

Ya que un valor superior a este porcentaje puede afectar la liquidez de la institución y su capacidad de otorgar nuevos créditos.

</div>

---

<!-- _class: slide--warning -->
<div class="negocio-card">

## DATA

La data fue proporcionada por la **Cooperativa de Ahorro y Crédito Jardín Azuayo** y contiene información de prestamos, amortizaciones y juicios desde el 2019 hasta el 2026.

La misma ya fue entregada con un proceso previo de anodizado: sin datos de cuentas, ni información personal de los socios y clientes, en fiel cumplimiento con normas internas de seguridades y leyes vigentes.

### La media de registros es de 1.8 millones por año !!

</div>

---

## Problema y Motivación

- El sector de **economía social y solidaria** enfrenta altos niveles de mora crediticia
- No existen sistemas integrados que combinen:
  - Análisis histórico de crédito
  - Predicción automatizada con IA
  - Visualización interactiva para toma de decisiones
- Procesos manuales, lentos y propensos a errores

> **Objetivo:** Crear un pipeline end-to-end que transforme datos crediticios crudos en predicciones accionables y dashboards para el control de la mora.

---

## Objetivos

### Objetivo General

Disenar e implementar un sistema integrado de inteligencia de negocio crediticio para el control de la mora en el sector de economia social y solidaria.

### Objetivos Especificos

1. **Pipeline ETL** automatizado con Apache Airflow
2. **Datamart analitico** con esquema estrella en PostgreSQL
3. **Modelos de IA** (CNN + LightGBM) para prediccion multi-horizonte
4. **Dashboards interactivos** con Apache Superset
5. **Aprobacion humana** del modelo antes de produccion

---

## Arquitectura General

```bash
CSV (51 archivos) ──→ ETL ──→ PostgreSQL ──→ Datamart (Estrella)
                              │                    │
                              │                    ├──→ EVA (Analisis)
                              │                    │
                              │                    ├──→ CNN + LightGBM
                              │                    │         │
                              │                    │    MLflow (Tracking)
                              │                    │         │
                              │                    │    Predicciones
                              │                    │         │
                              │                    └──→ Superset (Dashboard)
                              │
                              └──→ FastAPI (Endpoint)
```

**Stack tecnologico:** Airflow, PostgreSQL, MLflow, TensorFlow, LightGBM, `**Polars**`, Superset

---

## Componente ETL y Datamart 1-2

### ETL (Extraccion, Transformacion, Carga)

- **51 archivos CSV**: Cabecera de prestamos, amortizaciones, juicios
- Carga masiva a PostgreSQL con `COPY` (2015-2026)
- Proceso incremental con `ON CONFLICT DO UPDATE`

---

## Componente ETL y Datamart 2-2

### Datamart (Esquema Estrella)

| Dimension                 | Contenido                       |
| ------------------------- | ------------------------------- |
| dim_tiempo                | Mes, año, trimestre, nombre_mes |
| dim_riesgo                | Codigo y descripcion de riesgo  |
| dim_sector                | Codigo y descripcion de sector  |
| dim_sucursal              | Sucursal y provincia            |
| fact_creditos_mensual     | 27 metricas por bloque          |
| fact_predicciones_mensual | Predicciones multi-horizonte    |

---

## Analisis EVA (Evaluacion de Variables Analiticas)

### Modulo Python Reutilizable

- `pipeline.py` - Orquestador EVA (modo notebook/MLflow)
- `analisis_riguroso.py` - Motor de analisis estadistico

---

### Metricas Calculadas

| Metrica           | Uso                             |
| ----------------- | ------------------------------- |
| Pearson, Spearman | Correlacion lineal y monotonica |
| VIF               | Multicolinealidad               |
| Chi-cuadrado      | Asociación categórica           |
| Cohen's d, t-test | Diferencia entre grupos         |
| Shapiro-Wilk, KS  | Normalidad                      |

---

### Dashboard 3x3

- Heatmap de correlaciones, Top correlaciones
- Valores faltantes, Distribucion target
- Boxplots de mora, Tendencia temporal
- VIF, Recomendaciones automaticas (INCLUIR/EXCLUIR)

---

## EDA Optimizado (EDA001.ipynb)

### Problema

La consulta SQL genera **12M+ registros** que agotan la memoria RAM.

### Solución Implementada

- **Polars Lazy Mode**: `pl.read_database()` + `.lazy()` difiere ejecución
- **Procesamiento por año**: Extrae y agrega datos un año a la vez (2015-2025)
- **Agregación incremental**: Solo materializa registros agregados (~miles)

**Resultado:** Mismo CSV de salida, sin errores de memoria.

---

## Modelos de Inteligencia Artificial

### CNN Multi-Horizonte

- **Arquitectura:** Conv1D + BatchNorm + Dropout + Dense
- **Salidas:** 18 neuronas sigmoid (h1 a h18 meses)
- **Entrada:** Ventana de 6 meses, 16 features
- **Target:** `crisis_flag` (score heuristico >= 4)

### LightGBM

- **18 clasificadores independientes** (uno por horizonte)
- Gradient boosting con optimizacion bayesiana
- Feature importance para interpretabilidad

---

### MLflow - Tracking de valores iniciales

- Registro de experimentos y métricas
- Versionado de modelos y artefactos
- Comparación automática para selección del mejor
- Métricas a mejorar por interacción en el producto descrito

| Metrica   | CNN   | LightGBM |
| --------- | ----- | -------- |
| AUC-ROC   | ~0.85 | ~0.87    |
| Precision | ~0.82 | ~0.84    |
| Recall    | ~0.79 | ~0.81    |

---

## Predicción y Aprobación Humana

### Pipeline de Predicción

1. Modelo seleccionado genera predicciones multi-horizonte
2. Predicciones se guardan en `fact_predicciones_mensual`
3. **Humano en el loop:** experto revisa y aprueba/rechaza

### Endpoint de Predicción

```python
# predict.py - Inferencia batch
for bloque_id in bloques:
    X_seq, ultimo_mes = generar_secuencia(df_bloque)
    y_pred = modelo.predict(X_scaled)
    # Escritura ON CONFLICT DO UPDATE
```

---

### Dashboard (Superset)

- Visualizacion por dimensiones: tiempo, riesgo, sector, sucursal
- Filtros interactivos para analisis exploratorio
- Alertas de mora y criticos

---

## Estado Actual del Proyecto

### Completado

| Componente                        | Estado     |
| --------------------------------- | ---------- |
| ETL (carga CSV a PostgreSQL)      | Funcional  |
| Datamart SQL (esquema estrella)   | Funcional  |
| Modulo EVA (analisis estadistico) | Funcional  |
| EDA001.ipynb (optimizado Polars)  | Funcional  |
| Entrenamiento CNN                 | Entrenado  |
| Entrenamiento LightGBM            | Entrenado  |
| Infraestructura Docker            | Desplegada |

---

### En Desarrollo

- DAGs Airflow (pasos placeholder)
- Endpoint FastAPI
- Comparacion automatizada de modelos
- Dashboards Superset

---

### Proximos Pasos

1. Integrar scripts reales como tareas en DAGs Airflow
2. Implementar FastAPI endpoint para predicciones
3. Configurar dashboards en Apache Superset
4. Pruebas de integracion end-to-end
5. Documentacion tecnica y de usuario

---

<!-- _class: slide--negocio invert -->
<div class="negocio-card">

## Perspectivas Económicas Futuras

Dado que el proyecto tiene un enfoque de **inteligencia de negocio crediticio**, se espera que la implementación del sistema integrado genere:

**Producto reprisable, observable y escalable para otras cooperativas e insticiones de la economia social y solidaria que se dediquen a la gestion crediticia.**

</div>

---

<!-- _class: slide--negocio invert -->
<div class="negocio-card">

### Otros nichos de mercado

Y como un producto comercial, se espera que el mismo pueda ser licenciado a almacenes de electrodomésticos, tiendas de muebles, tiendas departamentales y otros comercios que **otorguen crédito directo** a sus clientes.

Ya que el sistema crediticio y el manejo de la mora es un
problema común en este tipo de negocios.

</div>

---

<!-- _class: lead -->

# Preguntas

Gracias por su atención.

![icon](yachayCuadrado.jpg)
**Omar Velez**  
omar.velez@yachaytech.edu.ec
