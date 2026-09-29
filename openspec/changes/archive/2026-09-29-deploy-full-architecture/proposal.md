# Proposal

## Why

El sistema de inteligencia de negocio para predicción de crisis crediticias tiene múltiples componentes (PostgreSQL, Airflow, Superset, MLflow) que necesitan ser desplegados y configurados correctamente antes de que el sistema RAG pueda funcionar. Actualmente, los contenedores Docker existen pero no están ejecutándose de forma coordinada, y los datos no fluyen correctamente hacia Apache Superset para visualización.

El sistema RAG usa el servidor MCP Python local (puerto 8000), NO el contenedor Docker ts_mcp. El ts_mcp Docker es opcional para acceso externo vía protocolo MCP.

## What Changes

- **Despliegue de contenedores Docker core**: Levantar los servicios esenciales (PostgreSQL con pgvector, Airflow, Superset, MLflow) en el orden correcto
- **Configuración de variables de entorno**: Crear y validar archivos `.env` para cada servicio con las credenciales y parámetros correctos
- **Carga de datos iniciales**: Ejecutar los DAGs de Airflow para cargar datos históricos y crear el datamart
- **Configuración de Superset**: Conectar Superset al datamart y crear dashboards iniciales
- **Verificación del flujo de datos**: Confirmar que los datos fluyen desde PostgreSQL → Datamart → Superset
- **Preparación para RAG**: Una vez que la arquitectura esté funcionando, el sistema RAG puede conectarse a la base de datos
- **MCP Servers (Opcional)**: Despliegue opcional de ts_mcp Docker para acceso externo vía protocolo MCP

## Capabilities

### New Capabilities
- `docker-infrastructure`: Despliegue y orquestación de contenedores Docker para los servicios core del sistema (PostgreSQL, Airflow, Superset, MLflow)
- `data-pipeline`: Pipeline de carga de datos desde CSV hasta el datamart, incluyendo ETL y transformaciones
- `superset-visualization`: Configuración de Apache Superset para visualizar el datamart y predicciones
- `mcp-servers`: Servidores MCP opcionales para acceso externo a PostgreSQL y Superset vía protocolo MCP (NO requerido para el sistema RAG)

### Modified Capabilities
(No existing capabilities to modify)

## Impact

- **Código afectado**:
  - `Contenedores/` - docker-compose.yml y scripts de ejecución (excluyendo ts_mcp del flujo principal)
  - `Desarrollo/airflow/` - DAGs de entrenamiento e inferencia
  - `Desarrollo/src/ts_csv/` - ETL de datos CSV
  - `Desarrollo/src/ts_datamart/` - Construcción del datamart
  - `Desarrollo/src/ts_predicciones/` - Pipeline de predicciones

- **Dependencias**:
  - Docker y Docker Compose instalados
  - Imágenes Docker: pgvector/pgvector:pg15, apache/airflow, apache/superset, mlflow
  - Datos CSV históricos para carga inicial

- **Sistemas afectados**:
  - PostgreSQL (puerto 5434) - Base de datos principal (fuente de verdad)
  - Airflow (puerto 8080) - Orquestador de pipelines
  - Superset (puerto 8088) - Visualización de datos
  - MLflow (puerto 5000) - Tracking de experimentos (independiente, base de datos del proveedor)
  - MCP Python (puerto 8000) - Servidor MCP local usado por el RAG
  - MCP Docker (puertos 5009, 5011) - OPCIONAL, para acceso externo