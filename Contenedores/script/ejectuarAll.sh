#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# Setup centralizado: genera .env
echo "=== Ejecutando setup centralizado ==="
bash "$SCRIPT_DIR/setup.sh"
echo ""

# ts_train (fuente de datos, DEBE ser primero)
echo "=== Iniciando ts_train (PostgreSQL) ==="
cd "$BASE_DIR/ts_train"
./ejecutar.sh
echo ""

# ts_airflow (depende de ts_train)
echo "=== Iniciando ts_airflow ==="
cd "$BASE_DIR/ts_airflow"
./ejecutar.sh
echo ""

# ts_superset (depende de ts_train)
echo "=== Iniciando ts_superset ==="
cd "$BASE_DIR/ts_superset"
./ejecutar.sh
echo ""

# ts_mlflow (INDEPENDIENTE, no tocar configuración)
echo "=== Iniciando ts_mlflow ==="
cd "$BASE_DIR/ts_mlflow"
./ejecutar.sh
echo ""

echo "=== Arquitectura completa levantada ==="