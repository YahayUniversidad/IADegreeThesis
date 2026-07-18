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

cd ts_superset
./parar.sh
cd ..
echo "Contenedores de superset detenidos."

cd ts_mcp
./parar.sh
cd ..
echo "Contenedores de mcp detenidos."