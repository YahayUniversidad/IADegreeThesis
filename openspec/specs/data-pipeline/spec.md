# data-pipeline Specification

## Purpose

Proporcionar un pipeline completo de carga de datos desde archivos CSV hasta el datamart, incluyendo ETL, transformaciones y construcción del esquema estrella para análisis de riesgo crediticio.

## Requirements

### Requirement: Carga de datos CSV
El sistema SHALL cargar datos históricos de créditos desde archivos CSV hacia la base de datos PostgreSQL.

#### Scenario: Carga exitosa de CSV
- **WHEN** se ejecuta el DAG de entrenamiento con archivos CSV válidos
- **THEN** los datos se insertan en las tablas operativas (creditos, amortizacion, juicios)

#### Scenario: CSV con formato inválido
- **WHEN** los archivos CSV tienen formato incorrecto
- **THEN** el sistema muestra un error descriptivo y no carga datos parciales

### Requirement: Construcción del datamart
El sistema SHALL construir un esquema estrella con dimensiones y hechos para análisis de riesgo crediticio.

#### Scenario: Creación de dimensiones
- **WHEN** se ejecuta el pipeline del datamart
- **THEN** se crean las tablas de dimensión (dim_tiempo, dim_riesgo, dim_sector, dim_sucursal)

#### Scenario: Creación de hechos
- **WHEN** se ejecuta el pipeline del datamart
- **THEN** se crea la tabla de hechos (fact_creditos_mensual) con métricas agregadas

#### Scenario: Creación de vistas materializadas
- **WHEN** se ejecuta el pipeline del datamart
- **THEN** se crean las vistas materializadas (mv_creditos_mensuales, mv_creditos, mv_predicciones)

### Requirement: Ejecución de pipelines Airflow
El sistema SHALL ejecutar los DAGs de Airflow para orquestar la carga de datos y construcción del datamart.

#### Scenario: DAG de entrenamiento
- **WHEN** se activa el DAG de entrenamiento
- **THEN** ejecuta: crear estructura → cargar CSV → datamart → EDA → entrenar modelos → MLflow

#### Scenario: DAG de inferencia
- **WHEN** se activa el DAG de inferencia
- **THEN** ejecuta: crear estructura → cargar CSV → datamart → predicción → Superset

### Requirement: Datos disponibles para análisis
El sistema SHALL asegurar que los datos estén disponibles en el datamart para consultas y visualización.

#### Scenario: Datamart poblado
- **WHEN** se completa el pipeline de datos
- **THEN** las tablas del datamart contienen datos históricos de créditos

#### Scenario: Métricas calculadas
- **WHEN** se completa el pipeline de datos
- **THEN** fact_creditos_mensual contiene métricas como tasa_mora_90, tasa_judicial, crisis_flag
