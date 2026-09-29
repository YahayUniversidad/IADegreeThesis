# Sistema Integrado de Inteligencia de Negocio para la Predicción de Crisis Crediticias

Trabajo de titulación — Universidad Yachay Tech

**Autor:** Omar Antonio Vélez Bayas
**Tutor:** Juan Pablo Astudillo León, Ph.D.
*Urcuquí, Agosto 2026*

---

## Resumen del proyecto

Este trabajo aborda la integración de datos crediticios, modelos de aprendizaje automático y herramientas de inteligencia de negocio en un sistema unificado. Se construye un prototipo reproducible que consolida fuentes operativas en un datamart, entrena y compara modelos predictivos (CNN, MLP, LightGBM), registra experimentos con MLflow, ejecuta inferencias multi-horizonte vía Apache Airflow y visualiza resultados en dashboards de Apache Superset.

El sistema predice probabilidades de crisis crediticia en 18 horizontes mensuales (`prob_h01`…`prob_h18`) y las expone en dos dashboards interactivos: evolución temporal por rango de plazo (corto/mediano/largo) y comparación por sucursal y sector.

## Estructura de la tesis

La tesis se compila desde `tesis/final/main.tex`. Los capítulos están en `tesis/final/chapters/`.

### Preliminares

| Archivo | Contenido |
|---|---|
| `autoria.tex` | Autoría |
| `autorizacion.tex` | Autorización de publicación |
| `dedication.tex` | Dedicatoria |
| `acknowledgments.tex` | Agradecimientos |
| `resumen.tex` | Resumen en español |
| `abstract.tex` | Abstract en inglés |

### Capítulos principales

| # | Capítulo | Archivo | Contenido |
|---|---|---|---|
| 1 | Introducción | `introduction.tex` | Contexto, motivación, planteamiento del problema, pregunta de investigación, objetivos y contribuciones |
| 2 | Marco Teórico | `fundamentals.tex` | Conceptos de inteligencia de negocio, aprendizaje automático, modelos utilizados y herramientas |
| 3 | Estado del Arte | `state_of_art.tex` | Revisión de literatura, trabajos relacionados y brechas identificadas |
| 4 | Metodología | `metodology.tex` | Diseño de la propuesta, dataset, preprocesamiento, arquitectura y configuración experimental |
| 5 | Resultados | `results.tex` | Resultados experimentales, comparación de modelos y análisis de métricas |
| 6 | Conclusiones | `conclusions.tex` | Conclusiones del trabajo |

## Arquitectura del sistema

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  ts_train    │    │  ts_airflow  │    │  ts_mlflow   │
│  PostgreSQL  │◄───│  Pipelines   │───►│  Tracking    │
│  + pgvector  │    │  ETL + ML    │    │  Experimentos│
│  (puerto 5434)│    │  (puerto 8080)│   │  (puerto 5000)│
└──────┬───────┘    └──────────────┘    └──────────────┘
       │
       ▼
┌──────────────┐    ┌──────────────┐
│ ts_superset  │    │   ts_mcp     │
│ Dashboards   │    │  MCP server  │
│ Analítica    │    │  (puerto 5011)│
│ (puerto 8088)│    └──────────────┘
└──────────────┘
```

### Contenedores Docker

Cada servicio vive en `Contenedores/` con su propio `docker-compose.yml`, scripts de gestión (`ejecutar.sh`, `parar.sh`) y configuración `.env`.

| Servicio | Descripción | Puerto |
|---|---|---|
| `ts_train` | PostgreSQL + pgvector. Datamart, embeddings y datos de entrenamiento | 5434 |
| `ts_airflow` | Apache Airflow. Orquesta DAGs de entrenamiento e inferencia | 8080 |
| `ts_superset` | Apache Superset. Dashboards de analítica de negocio | 8088 |
| `ts_mlflow` | MLflow + RustFS. Tracking de experimentos ML | 5000 |
| `ts_mcp` | Servidor MCP para interacción externa | 5011 |

### Módulos de desarrollo (`Desarrollo/src/`)

| Módulo | Descripción |
|---|---|
| `ts_csv/` | ETL: carga y transformación de datos CSV |
| `ts_datamart/` | Construcción del datamart de riesgo crediticio |
| `ts_cnn/` | Entrenamiento del modelo CNN |
| `ts_mlp/` | Entrenamiento del modelo MLP |
| `ts_lightgbm/` | Entrenamiento del modelo LightGBM |
| `ts_predicciones/` | Inferencia multi-horizonte con el modelo seleccionado |
| `ts_eva/` | Análisis EDA/EVA |
| `ts_embeddings/` | Generación de embeddings con pgvector |
| `ts_chatbot/` | Chatbot de interacción |
| `ts_mcp/` | Herramientas MCP |
| `ts_sql/` | Queries SQL reutilizables |

### Pipelines (Airflow)

| DAG | Flujo |
|---|---|
| `dag_entrenamiento.py` | CSV → EDA → CNN + MLP + LightGBM → MLflow |
| `dag_inferencia.py` | CSV → Datamart → Predicción → Superset |

## Dashboards de Superset

### Predicción por Horizonte Temporal
- Evolución de la probabilidad de crisis por rango de plazo (corto 1–3M, medio 4–6M, largo 7–18M)
- Predicciones positivas por período y rango
- KPIs de probabilidad promedio por rango
- Filtros: rango de plazo, año

### Comparación de Rangos por Segmento
- Comparación de probabilidades por sucursal y rango de plazo
- Comparación por sector y rango de plazo
- Heatmap sucursal × rango de plazo
- Filtros: rango de plazo, año

### Dashboards históricos
- Tendencia de Crisis Crediticia
- Predicciones de Crisis
- Resumen por Sucursal

## Compilación de la tesis

```bash
cd tesis/final
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

## Dependencias Python

```bash
pip install polars psycopg2-binary mlflow lightgbm tensorflow sqlalchemy numpy pandas scikit-learn joblib matplotlib seaborn requests
```

---

![logo](/DocumentosBase/yachayCuadrado.jpg)

***<omar.velez@yachaytech.edu.ec>*** — *Agosto 2026*
