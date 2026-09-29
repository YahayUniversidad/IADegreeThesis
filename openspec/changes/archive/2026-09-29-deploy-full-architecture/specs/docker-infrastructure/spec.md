# Spec Delta

## Purpose

Proporcionar despliegue automatizado y orquestación de todos los contenedores Docker del sistema, asegurando que inicien en el orden correcto y estén disponibles para los demás componentes.

## ADDED Requirements

### Requirement: Despliegue ordenado de contenedores
El sistema SHALL levantar los contenedores Docker en secuencia: PostgreSQL primero, luego Airflow, Superset, MLflow y MCP.

#### Scenario: Inicio exitoso de PostgreSQL
- **WHEN** se ejecuta el script de despliegue
- **THEN** PostgreSQL inicia en el puerto 5434 y acepta conexiones

#### Scenario: Inicio de Airflow después de PostgreSQL
- **WHEN** PostgreSQL está disponible
- **THEN** Airflow inicia en el puerto 8080 y puede conectarse a PostgreSQL

#### Scenario: Inicio de Superset después de PostgreSQL
- **WHEN** PostgreSQL está disponible
- **THEN** Superset inicia en el puerto 8088 y puede conectarse a PostgreSQL

### Requirement: Verificación de salud de contenedores
El sistema SHALL verificar que cada contenedor esté saludable antes de continuar con el siguiente.

#### Scenario: Contenedor saludable
- **WHEN** un contenedor está ejecutándose y respondiendo
- **THEN** el sistema continúa con el siguiente contenedor

#### Scenario: Contenedor no saludable
- **WHEN** un contenedor no responde después de 5 minutos
- **THEN** el sistema muestra un error y detiene el despliegue

### Requirement: Variables de entorno configuradas
El sistema SHALL cargar las variables de entorno desde archivos `.env` para cada servicio.

#### Scenario: Archivo .env existe
- **WHEN** existe un archivo .env para un servicio
- **THEN** el sistema carga las variables y las usa en la configuración

#### Scenario: Archivo .env no existe
- **WHEN** no existe un archivo .env para un servicio
- **THEN** el sistema usa valores por defecto o muestra un error

### Requirement: Scripts de gestión
El sistema SHALL proporcionar scripts para iniciar, detener y verificar el estado de todos los contenedores.

#### Scenario: Script de inicio
- **WHEN** se ejecuta `ejecutarAll.sh`
- **THEN** todos los contenedores se levantan en orden

#### Scenario: Script de parada
- **WHEN** se ejecuta `pararAll.sh`
- **THEN** todos los contenedores se detienen gracefully