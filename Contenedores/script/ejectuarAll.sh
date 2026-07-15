#!/bin/bash

cd ..

echo "Iniciando contenedores de train"
cd ts_train
./ejecutar.sh
cd ..

echo "Iniciando contenedores de airflow"
cd ts_airflow
./ejecutar.sh
cd ..

echo "Iniciando contenedores de mlflow"
cd ts_mlflow
./ejecutar.sh
cd ..