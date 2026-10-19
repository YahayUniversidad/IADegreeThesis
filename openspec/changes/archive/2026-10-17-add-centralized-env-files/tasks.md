# Tasks

## 1. Generador centralizado de .env

- [x] 1.1 Crear `Contenedores/script/generarEnv.sh` con los valores por defecto compartidos (credenciales y puerto PostgreSQL, admin de Superset, SMTP, `AIRFLOW_UID`, `SUPERSET_SECRET_KEY`) y la escritura de los `.env` de `ts_train`, `ts_airflow` y `ts_superset` con las variables exactas que sus `docker-compose.yml` interpolan; verificar ejecutándolo desde `Contenedores/script/` y comprobando que los tres archivos `.env` existen (`ls Contenedores/ts_{train,airflow,superset}/.env`).
- [x] 1.2 Verificar que cada `.env` generado contiene todas las variables de su compose: `grep` de `POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD` en `ts_train/.env`, de `PG_USER|PG_PASSWORD|PG_PORT|PG_DB|SMTP_USER|SMTP_PASSWORD|AIRFLOW_UID` en `ts_airflow/.env`, y de `SUPERSET_SECRET_KEY|PG_USER|PG_PASSWORD|PG_PORT|PG_DB|SUPERSET_ADMIN_*|MCP_DEV_USERNAME` en `ts_superset/.env`.
- [x] 1.3 Verificar la consistencia compartida: el valor de `POSTGRES_USER`/`POSTGRES_PASSWORD`/puerto `5434` en `ts_train/.env` coincide con `PG_USER`/`PG_PASSWORD`/`PG_PORT` en `ts_airflow/.env` y `ts_superset/.env`.
- [x] 1.4 Verificar que una segunda ejecución de `generarEnv.sh` sobrescribe los `.env` (cambiar un valor a mano, re-ejecutar y comprobando que vuelve al default) y que `ts_mlflow/` y `ts_mcp/` quedan intactos (`git status Contenedores/ts_mlflow Contenedores/ts_mcp` sin cambios).

## 2. Integración con el despliegue centralizado

- [x] 2.1 Reemplazar en `Contenedores/script/ejectuarAll.sh` la llamada a `setup.sh` por `generarEnv.sh`; verificar con `grep generarEnv.sh Contenedores/script/ejecutarAll.sh` y `bash -n Contenedores/script/ejecutarAll.sh` (sintaxis OK y sin referencias a `setup.sh`).

## 3. Verificación integral

- [x] 3.1 Ejecutar `bash Contenedores/script/generarEnv.sh` desde la raíz del proyecto (otro cwd) y verificar que los `.env` se generan en los directorios correctos gracias a la resolución de rutas con `BASH_SOURCE`.
- [x] 3.2 Ejecutar `docker compose config` en `ts_train`, `ts_airflow` y `ts_superset` y verificar que no quedan variables sin resolver (sin advertencias de "variable is not set") gracias a los `.env` generados.
