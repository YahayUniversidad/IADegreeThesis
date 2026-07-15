#!/bin/bash
cd ..

cd ts_train
./parar.sh
cd ..
echo "Contenedores de train detenidos."

cd ts_airflow
./parar.sh
cd ..
echo "Contenedores de airflow detenidos."

cd ts_mlflow
./parar.sh
cd ..
echo "Contenedores de mlflow detenidos."