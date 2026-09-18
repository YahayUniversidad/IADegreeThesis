# IADegreeThesis

**Sistema Integrado de Inteligencia de Negocio para la Predicción de Crisis Crediticias mediante técnicas de Inteligencia Artificial y Analítica de negocios**

Trabajo de titulación — Universidad Yachay Tech
**Autor:** Omar Antonio Vélez Bayas
**Tutor:** Juan Pablo Astudillo León, Ph.D.
*Urcuquí, Agosto 2026*

## Links

- [Overleaf Project](https://es.overleaf.com/project)
- [IA super set](https://superset.apache.org/user-docs/using-superset/using-ai-with-superset)
- [Airflow](https://airflow.apache.org/)

## Estructura de la Tesis

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
| 1 | Introducción | `introduction.tex` | Background, motivación, planteamiento del problema, objetivo general y específicos |
| 2 | Marco Teórico | `fundamentals.tex` | Conceptos fundamentales, técnicas, modelos y herramientas utilizadas |
| 3 | Estado del Arte | `state_of_art.tex` | Revisión de literatura, estrategia de búsqueda, trabajos relacionados, brechas identificadas |
| 4 | Metodología | `metodology.tex` | Diseño de la propuesta, dataset, preprocesamiento, arquitectura, configuración experimental |
| 5 | Resultados | `results.tex` | Resultados experimentales, comparación de modelos, análisis de métricas |
| 6 | Conclusiones | `conclusions.tex` | Conclusiones del trabajo |

## Estructura del Proyecto

```
├── tesis/final/          # Documento LaTeX de la tesis
│   ├── main.tex          # Archivo principal
│   ├── chapters/         # Capítulos
│   ├── bib/              # Bibliografía
│   ├── images/           # Figuras
│   └── codes/            # Fragmentos de código
├── Contenedores/         # Infraestructura Docker
├── Desarrollo/           # Código fuente de la aplicación
└── script/               # Scripts de configuración centralizados
```

### Contenedores

Infraestructura Docker que sostiene todo el sistema. Cada subdirectorio es un servicio independiente con su propio `docker-compose.yml`, scripts de gestión (`ejecutar.sh`, `parar.sh`) y configuración `.env`. La configuración centralizada vive en `script/setup.sh`.

| Servicio | Contenedor | Descripción |
|---|---|---|
| `ts_train` | PostgreSQL + pgvector | Base de datos principal. Almacena el datamart, embeddings y datos de entrenamiento. Expuesta en puerto 5434. |
| `ts_airflow` | Apache Airflow | Orquestador de pipelines. Ejecuta los DAGs de entrenamiento e inferencia. Interfaz web en puerto 8080. |
| `ts_superset` | Apache Superset | Tableros de analítica de negocio. Conecta al datamart para visualizar predicciones y métricas. Puerto 8088. |
| `ts_mlflow` | MLflow + RustFS | Tracking de experimentos ML. Registra modelos, métricas y artefactos de CNN, MLP y LightGBM. Puerto 5000. |
| `ts_mcp` | MCP server | Servidor de herramientas para interacción con el sistema vía protocolo MCP. |

### Desarrollo

Código fuente de la aplicación y pipelines de datos.

| Directorio | Descripción |
|---|---|
| `src/` | Módulos principales del sistema |
| `src/ts_csv/` | ETL: carga y transformación de datos CSV hacia la base de datos |
| `src/ts_datamart/` | Construcción y actualización del datamart de riesgo crediticio |
| `src/ts_cnn/` | Pipeline de entrenamiento del modelo CNN |
| `src/ts_mlp/` | Pipeline de entrenamiento del modelo MLP |
| `src/ts_lightgbm/` | Pipeline de entrenamiento del modelo LightGBM |
| `src/ts_predicciones/` | Inferencia: ejecuta predicciones con el modelo seleccionado |
| `src/ts_eva/` | Análisis EDA/EVA (Exploratory Data/Variable Analysis) |
| `src/ts_embeddings/` | Generación de embeddings con pgvector |
| `src/ts_chatbot/` | Chatbot de interacción con el sistema |
| `src/ts_mcp/` | Herramientas MCP expuestas al servidor |
| `src/ts_sql/` | Utilidades y queries SQL reutilizables |
| `src/common/` | Configuración y utilidades compartidas entre módulos |
| `airflow/` | DAGs de Airflow |
| `airflow/dag_entrenamiento.py` | DAG de entrenamiento: CSV → EDA → CNN + MLP + LightGBM → MLflow |
| `airflow/dag_inferencia.py` | DAG de inferencia: CSV → Datamart → Predicción → Superset |
| `noteBooks/` | Jupyter notebooks de exploración y análisis |
| `chat_cli.py` | CLI para interactuar con el chatbot |
| `generate_embeddings.py` | Script standalone para generar embeddings |
| `run_servers.py` | Script para levantar servidores locales |

#### Dependencias Python

```bash
pip install polars psycopg2-binary mlflow lightgbm tensorflow sqlalchemy numpy pandas scikit-learn joblib matplotlib seaborn requests
```

---
***<omar.velez@yachaytech.edu.ec>*** — *Agosto 2026*
