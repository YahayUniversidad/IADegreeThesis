# Spec Delta

## Purpose

Configurar Apache Superset para conectarse al datamart de riesgo crediticio y proporcionar visualizaciones y dashboards para análisis de datos y predicciones.

## ADDED Requirements

### Requirement: Conexión al datamart
El sistema SHALL conectar Superset al datamart de PostgreSQL para acceder a las tablas de dimensiones y hechos.

#### Scenario: Conexión exitosa
- **WHEN** se configura la conexión en Superset
- **THEN** Superset puede consultar las tablas del datamart

#### Scenario: Conexión fallida
- **WHEN** las credenciales son incorrectas
- **THEN** Superset muestra un error de conexión

### Requirement: Dashboards de riesgo crediticio
El sistema SHALL proporcionar dashboards preconfigurados para visualizar métricas de riesgo crediticio.

#### Dashboard: Tendencia de crisis
- **WHEN** el usuario abre el dashboard de tendencia de crisis
- **THEN** muestra la evolución temporal de créditos en crisis por sucursal y sector

#### Dashboard: Predicciones
- **WHEN** el usuario abre el dashboard de predicciones
- **THEN** muestra las predicciones de probabilidad de crisis por período

#### Dashboard: Resumen por sucursal
- **WHEN** el usuario abre el dashboard de resumen
- **THEN** muestra métricas agregadas por sucursal (total créditos, monto, mora, judicial)

### Requirement: Acceso de usuarios
El sistema SHALL permitir a los usuarios autenticados acceder a los dashboards.

#### Scenario: Usuario administrador
- **WHEN** el usuario admin inicia sesión
- **THEN** tiene acceso completo a todos los dashboards y configuraciones

#### Scenario: Usuario desarrollador
- **WHEN** el usuario desarrollador inicia sesión
- **THEN** tiene acceso de solo lectura a los dashboards

### Requirement: Actualización automática de datos
El sistema SHALL actualizar los dashboards cuando se ejecuta el DAG de inferencia.

#### Scenario: Nuevo ciclo de inferencia
- **WHEN** se completa el DAG de inferencia
- **THEN** los dashboards muestran los datos más recientes

#### Scenario: Sin nuevos datos
- **WHEN** no se ha ejecutado el DAG de inferencia
- **THEN** los dashboards muestran los datos del último ciclo exitoso