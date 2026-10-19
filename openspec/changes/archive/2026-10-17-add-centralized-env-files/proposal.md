# Proposal

## Why

Los `docker-compose.yml` de `ts_train`, `ts_airflow` y `ts_superset` referencian variables de entorno (`POSTGRES_*`, `PG_*`, `SMTP_*`, `SUPERSET_*`, etc.) sin que exista ningún archivo `.env` en esas carpetas, por lo que el despliegue falla o depende de que el operador recuerde crear los `.env` a mano y mantenga los valores consistentes entre servidores (la contraseña de `ts_train` debe coincidir con la cadena de conexión que usan Airflow y Superset). Además, `script/ejectuarAll.sh` llama a `script/setup.sh`, un archivo inexistente que hace fallar el levantamiento completo.

## What Changes

- Nuevo `Contenedores/script/generarEnv.sh`: script centralizado que genera los archivos `.env` de `ts_train`, `ts_airflow` y `ts_superset` con valores por defecto consistentes entre sí (mismas credenciales y puerto de PostgreSQL en los tres).
- `generarEnv.sh` siempre regenera los `.env` en cada ejecución (sobrescribe valores previos).
- `ts_mlflow` queda fuera del alcance: su `.env` sigue gestionándose con `instalar.sh` (copia de `.env.dev.example` dentro del repo clonado). `ts_mcp` también queda excluido.
- `script/ejectuarAll.sh` se actualiza para llamar a `script/generarEnv.sh` en lugar del `setup.sh` inexistente.
- Se aprovecha que `.gitignore` ya ignora `.env` (los archivos generados no se versionan).

## Capabilities

### New Capabilities

<!-- Ninguna -->

### Modified Capabilities

- `docker-infrastructure`: el requisito "Variables de entorno configuradas" pasa de depender de archivos `.env` creados manualmente a generarlos de forma automatizada y centralizada con `script/generarEnv.sh`, definido el comportamiento ante regeneración y los servicios cubiertos.

## Impact

- Archivos nuevos: `Contenedores/script/generarEnv.sh`; `.env` generados en `Contenedores/ts_train/`, `Contenedores/ts_airflow/` y `Contenedores/ts_superset/`.
- Archivos modificados: `Contenedores/script/ejectuarAll.sh` (referencia a `setup.sh` → `generarEnv.sh`).
- Sin cambios en `docker-compose.yml`, Dockerfiles ni en `ts_mlflow`/`ts_mcp`.
- Requiere Bash y acceso de escritura en `Contenedores/`; no añade dependencias.
