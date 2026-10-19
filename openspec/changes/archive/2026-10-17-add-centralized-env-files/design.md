# Design

## Context

Cada servicio Docker en `Contenedores/` tiene un `docker-compose.yml` que interpola variables del archivo `.env` de su propio directorio, pero solo existe un `.env` (el de `ts_mlflow`, copiado por `instalar.sh` desde `.env.dev.example` del repo clonado). `ts_train`, `ts_airflow` y `ts_superset` no tienen `.env`, y sus credenciales de PostgreSQL deben coincidir entre sí (Airflow y Superset se conectan a la instancia de `ts_train` en `host.docker.internal:5434`). `script/ejectuarAll.sh` ya invoca un `setup.sh` inexistente. Motivación completa en `proposal.md`.

## Goals / Non-Goals

**Goals:**

- Un único punto de definición de los valores por defecto para los `.env` de `ts_train`, `ts_airflow` y `ts_superset`.
- Generación determinista y reproducible de los tres `.env` en una sola ejecución.
- `ejecutarAll.sh` funcional de punta a punta sin pasos manuales previos.

**Non-Goals:**

- Gestionar el `.env` de `ts_mlflow` (sigue con `instalar.sh`).
- Modificar `ts_mcp` o cualquier `docker-compose.yml`.
- Inyección de secretos reales de producción (los valores por defecto son de desarrollo).

## Decisions

1. **Script único `script/generarEnv.sh` con valores compartidos arriba.** Las variables comunes (`PG_USER`, `PG_PASSWORD`, `PG_PORT`, `PG_DB`, credenciales de admin de Superset, SMTP) se definen una sola vez al inicio del script; luego se escriben tres `.env` con los nombres que cada compose espera (`POSTGRES_*` en `ts_train`, `PG_*`/`SMTP_*`/`SUPERSET_*` en los otros). *Alternativa descartada*: un `.env` compartido por symlink — docker compose no lee `.env` fuera del directorio del proyecto y los nombres de variables difieren entre servicios.

2. **Valores por defecto alineados con el README de Airflow** (`postgres_usr` / `admin123` / `5434` / `postgres_db`), que ya documenta esa cadena de conexión como ejemplo. `SUPERSET_SECRET_KEY` usa un valor fijo de desarrollo en lugar de uno aleatorio por ejecución, para no rotar la clave en cada regeneración sin que el operador lo note.
   *Corrección post-implementación*: `AIRFLOW_UID` dejó de ser el default `50000` y pasó a `$(id -u)` (el uid del usuario anfitrión). Con `50000` y las carpetas de volumen propias del usuario, `airflow-init` fallaba con `PermissionError` en `/opt/airflow/logs`; con el uid del anfitrión se garantiza escritura sin `sudo`. Las carpetas `dags/`, `logs/`, etc., si quedaron creadas como root, requieren un `chown -R $(id -u):0` puntual (resuelto en la aplicación con un contenedor temporal `alpine`, sin hacerlo parte del script). Como el uid del anfitrión no tiene entrada en `/etc/passwd` dentro de la imagen, `ts_airflow/docker-compose.yml` define `USER: airflow` en el entorno común para que la CLI de Airflow resuelva un nombre de usuario.

3. **Regeneración siempre (sobrescribir).** Decisión del usuario: cada ejecución de `generarEnv.sh` pisa los `.env` con los valores vigentes del script; el script es la fuente de verdad. Los `.env` ya están en `.gitignore`, así que no hay riesgo de filtración al repositorio.

4. **`ejecutarAll.sh` llama a `generarEnv.sh` en lugar de `setup.sh`.** Con `set -e` ya presente en `ejectuarAll.sh`, un fallo del generador detiene el despliegue. Se elimina la referencia muerta a `setup.sh`.

5. **Resolución de rutas relativa al script** (`BASE_DIR` desde `BASH_SOURCE`), igual que ya hacen `ejecutarAll.sh` y los `ejecutar.sh` de cada servicio, para que funcione desde cualquier directorio de trabajo.

## Risks / Trade-offs

- [Sobrescribir `.env` borra personalizaciones del operador] → Es el comportamiento pedido; los valores editables viven en el propio `generarEnv.sh`, no en los `.env`.
- [Rotar `SUPERSET_SECRET_KEY` en cada regeneración rompería sesiones de Superset] → Se usa valor fijo de desarrollo; para producción se-documenta cambiar el default en el script.
- [Credenciales por defecto débiles (`admin123`)] → Aceptado en entorno local de desarrollo; los `.env` no se versionan y el script es el lugar natural para poner secretos reales antes de un despliegue no local.

## Migration Plan

No hay datos persistentes afectados. Si ya existen contenedores corriendo con `.env` previos, basta re-ejecutar `generarEnv.sh` y `ejecutar.sh` de cada servicio para aplicar los nuevos valores. Rollback: borrar `generarEnv.sh` y restaurar la llamada anterior en `ejecutarAll.sh` (aunque esa llamada apuntaba a un archivo inexistente).

## Open Questions

<!-- Ninguna -->
