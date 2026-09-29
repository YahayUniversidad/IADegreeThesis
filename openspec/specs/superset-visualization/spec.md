# superset-visualization Specification

## Purpose

Configurar Apache Superset para conectarse al datamart de riesgo crediticio y proporcionar visualizaciones y dashboards para análisis de datos y predicciones.

## Requirements

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

### Requirement: Dataset de horizontes de predicción
El sistema SHALL exponer un dataset de horizontes de predicción en formato largo (una fila por predicción × horizonte) que incluya el horizonte mensual, el rango de plazo y la probabilidad de crisis, para que Superset pueda visualizar la predicción por rangos de tiempo.

#### Scenario: Dataset consultable en Superset
- **WHEN** el usuario consulta el dataset de horizontes en Superset
- **THEN** el dataset retorna filas con al menos: período (mes/año), sucursal, sector, horizonte (1–18), rango de plazo (corto/medio/largo) y probabilidad de crisis

#### Scenario: Cobertura de los 18 horizontes
- **WHEN** se consulta el dataset para un período y bloque dados
- **THEN** el dataset retorna exactamente 18 filas, una por cada horizonte `prob_h01`…`prob_h18`

#### Scenario: Clasificación de rangos de plazo
- **WHEN** se consulta el dataset
- **THEN** los horizontes 1–3 se clasifican como `corto`, los horizontes 4–6 como `medio` y los horizontes 7–18 como `largo`

### Requirement: Dashboard de predicción por horizonte temporal
El sistema SHALL proporcionar un dashboard que muestre la evolución temporal de la probabilidad de crisis por rango de plazo (corto, medio, largo).

#### Scenario: Visualización de evolución por rango
- **WHEN** el usuario abre el dashboard de predicción por horizonte temporal
- **THEN** el dashboard muestra la evolución de la probabilidad de crisis en el tiempo, desglosada por rango de plazo (corto 1–3M, medio 4–6M, largo 7–18M)

#### Scenario: Filtro por rango de plazo
- **WHEN** el usuario aplica un filtro de rango de plazo en el dashboard
- **THEN** los charts muestran únicamente los datos del rango seleccionado

#### Scenario: Filtro por período
- **WHEN** el usuario aplica un filtro de período (mes/año)
- **THEN** los charts muestran únicamente los datos del período seleccionado

#### Scenario: Promedio por rango
- **WHEN** se visualiza un rango de plazo
- **THEN** el dashboard muestra el promedio de probabilidad de crisis para las predicciones del período dentro de ese rango

### Requirement: Dashboard de comparación de rangos por segmento
El sistema SHALL proporcionar un dashboard que compare la probabilidad de crisis por rango de plazo entre sucursales y sectores.

#### Scenario: Comparación por sucursal
- **WHEN** el usuario abre el dashboard de comparación de rangos por segmento
- **THEN** el dashboard muestra la comparación de probabilidades por rango de plazo agrupadas por sucursal

#### Scenario: Comparación por sector
- **WHEN** el usuario visualiza la comparación por sector
- **THEN** el dashboard muestra la comparación de probabilidades por rango de plazo agrupadas por sector

#### Scenario: Filtro por rango de plazo
- **WHEN** el usuario aplica un filtro de rango de plazo en el dashboard
- **THEN** los charts muestran únicamente los datos del rango seleccionado

#### Scenario: Filtro por período
- **WHEN** el usuario aplica un filtro de período (mes/año)
- **THEN** los charts muestran únicamente los datos del período seleccionado

### Requirement: Conservación de dashboards existentes
El sistema SHALL conservar sin cambios los dashboards existentes (Tendencia de Crisis Crediticia, Predicciones de Crisis, Resumen por Sucursal) al crear los nuevos dashboards de horizontes.

#### Scenario: Dashboards previos intactos
- **WHEN** se crean los dos dashboards nuevos de predicción por horizonte
- **THEN** los dashboards 10, 11 y 12 siguen funcionando con sus datasets y charts originales
