#!/bin/bash
set -e

##
## Generador centralizado de archivos .env
##
## Crea (y siempre sobrescribe) los .env de ts_train, ts_airflow y ts_superset
## a partir de los valores por defecto definidos en este archivo.
## Los valores editables de cada despliegue se cambian AQUI, no en los .env.
## ts_mlflow y ts_mcp quedan fuera de alcance (mlflow usa instalar.sh).
##

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

## Valores compartidos (fuente única de verdad)
PG_USER="postgres_usr"
PG_PASSWORD="admin123"
PG_PORT="5434"
PG_DB="postgres_db"

## UID del usuario anfitrión: los contenedores corren como este uid para que
## los volúmenes montados (dags, logs, ...) sean escribibles sin sudo.
AIRFLOW_UID="$(id -u)"
SMTP_USER="omargo33@gmail.com"
SMTP_PASSWORD="changeme"

SUPERSET_SECRET_KEY="dev_secret_key_cambiar_en_produccion"
SUPERSET_ADMIN_USERNAME="admin"
SUPERSET_ADMIN_FIRSTNAME="Admin"
SUPERSET_ADMIN_LASTNAME="User"
SUPERSET_ADMIN_EMAIL="admin@example.com"
SUPERSET_ADMIN_PASSWORD="admin123"
MCP_DEV_USERNAME="admin"

## ts_train: PostgreSQL (expone POSTGRES_* a su docker-compose)
cat > "$BASE_DIR/ts_train/.env" <<EOF
POSTGRES_DB=$PG_DB
POSTGRES_USER=$PG_USER
POSTGRES_PASSWORD=$PG_PASSWORD
EOF

## ts_airflow: usa PG_* de la instancia de ts_train + SMTP + UID
cat > "$BASE_DIR/ts_airflow/.env" <<EOF
AIRFLOW_UID=$AIRFLOW_UID
PG_USER=$PG_USER
PG_PASSWORD=$PG_PASSWORD
PG_PORT=$PG_PORT
PG_DB=$PG_DB
SMTP_USER=$SMTP_USER
SMTP_PASSWORD=$SMTP_PASSWORD
EOF

## ts_superset: usa PG_* de la instancia de ts_train + admin + MCP
cat > "$BASE_DIR/ts_superset/.env" <<EOF
SUPERSET_SECRET_KEY=$SUPERSET_SECRET_KEY
PG_USER=$PG_USER
PG_PASSWORD=$PG_PASSWORD
PG_PORT=$PG_PORT
PG_DB=$PG_DB
SUPERSET_ADMIN_USERNAME=$SUPERSET_ADMIN_USERNAME
SUPERSET_ADMIN_FIRSTNAME=$SUPERSET_ADMIN_FIRSTNAME
SUPERSET_ADMIN_LASTNAME=$SUPERSET_ADMIN_LASTNAME
SUPERSET_ADMIN_EMAIL=$SUPERSET_ADMIN_EMAIL
SUPERSET_ADMIN_PASSWORD=$SUPERSET_ADMIN_PASSWORD
MCP_DEV_USERNAME=$MCP_DEV_USERNAME
EOF

echo "Archivos .env generados en ts_train, ts_airflow y ts_superset"
