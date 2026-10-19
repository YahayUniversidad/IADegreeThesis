# docker-infrastructure Specification

## Purpose

Proporcionar despliegue automatizado y orquestación de todos los contenedores Docker del sistema, asegurando que inicien en el orden correcto y estén disponibles para los demás componentes.

## Requirements

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
El sistema SHALL cargar las variables de entorno desde archivos `.env` para cada servicio, y los servicios `ts_train`, `ts_airflow` y `ts_superset` SHALL obtener sus valores de un conjunto de variables compartidas y consistentes entre sí (mismas credenciales y puerto de PostgreSQL).

#### Scenario: Archivo .env existe
- **WHEN** existe un archivo .env para un servicio
- **THEN** el sistema carga las variables y las usa en la configuración

#### Scenario: Archivo .env no existe
- **WHEN** no existe un archivo .env para un servicio
- **THEN** el sistema usa valores por defecto o muestra un error

#### Scenario: Valores compartidos entre servicios
- **WHEN** se generan los `.env` de `ts_train`, `ts_airflow` y `ts_superset`
- **THEN** las credenciales y el puerto de PostgreSQL referenciados por Airflow y Superset coinciden con los definidos por `ts_train` (publicación en el puerto 5434)

### Requirement: Generación centralizada de archivos .env
El sistema SHALL proporcionar el script `Contenedores/script/generarEnv.sh` que genera los archivos `.env` de `ts_train`, `ts_airflow` y `ts_superset` a partir de valores por defecto definidos en un solo lugar, y SHALL sobrescribir los `.env` existentes en cada ejecución. `ts_mlflow` y `ts_mcp` quedan fuera del alcance de este script.

#### Scenario: Primera generación
- **WHEN** se ejecuta `generarEnv.sh` y no existen archivos `.env` en los servicios cubiertos
- **THEN** se crean los archivos `.env` de `ts_train`, `ts_airflow` y `ts_superset` con todas las variables que sus `docker-compose.yml` referencian

#### Scenario: Regeneración sobre archivos existentes
- **WHEN** se ejecuta `generarEnv.sh` y ya existen archivos `.env` generados previamente
- **THEN** los archivos se sobrescriben con los valores por defecto vigentes del script

#### Scenario: Servicios fuera de alcance
- **WHEN** se ejecuta `generarEnv.sh`
- **THEN** no se crean ni modifican archivos en `ts_mlflow` ni `ts_mcp`

### Requirement: Integración del generador en el despliegue centralizado
`ejecutarAll.sh` SHALL ejecutar `generarEnv.sh` antes de levantar los contenedores, de modo que el despliegue completo no dependa de la creación manual previa de los archivos `.env`.

#### Scenario: Despliegue completo con generación previa
- **WHEN** se ejecuta `script/ejecutarAll.sh`
- **THEN** se ejecuta `generarEnv.sh` y, en caso de éxito, continúa el levantamiento ordenado de los contenedores

#### Scenario: Fallo del generador detiene el despliegue
- **WHEN** `generarEnv.sh` termina con error
- **THEN** `ejecutarAll.sh` muestra el error y no intenta levantar los contenedores

### Requirement: Scripts de gestión
El sistema SHALL proporcionar scripts para iniciar, detener y verificar el estado de todos los contenedores.

#### Scenario: Script de inicio
- **WHEN** se ejecuta `ejecutarAll.sh`
- **THEN** todos los contenedores se levantan en orden

#### Scenario: Script de parada
- **WHEN** se ejecuta `pararAll.sh`
- **THEN** todos los contenedores se detienen gracefully
