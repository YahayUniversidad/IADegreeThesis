#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$(dirname "$SCRIPT_DIR")"

# ts_mlflow (primero porque es independiente y puede tener contenedores huérfanos)
echo "=== Deteniendo ts_mlflow ==="
cd "$BASE_DIR/ts_mlflow"
./parar.sh
echo ""

# ts_superset
echo "=== Deteniendo ts_superset ==="
cd "$BASE_DIR/ts_superset"
./parar.sh
echo ""

# ts_airflow
echo "=== Deteniendo ts_airflow ==="
cd "$BASE_DIR/ts_airflow"
./parar.sh
echo ""

# ts_train (último porque otros dependen de él)
echo "=== Deteniendo ts_train ==="
cd "$BASE_DIR/ts_train"
./parar.sh
echo ""

echo "=== Todos los contenedores detenidos ==="