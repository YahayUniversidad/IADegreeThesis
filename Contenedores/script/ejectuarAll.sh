#!/bin/bash
cd ..

# Setup centralizado: genera .env y configura permisos
echo "Ejecutando setup centralizado..."
cd script
./setup.sh
cd ..

echo "Iniciando contenedores de train"
cd ts_train
./ejecutar.sh
cd ..

echo "Iniciando contenedores de airflow"
cd ts_airflow
./ejecutar.sh
cd ..

echo "Iniciando contenedores de superset"
cd ts_superset
./ejecutar.sh
cd ..

echo "Iniciando contenedores de mlflow"
cd ts_mlflow
./ejecutar.sh
cd ..