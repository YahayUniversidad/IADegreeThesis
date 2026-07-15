#!/bin/bash

## para recargar los DAGs de airflow, se eliminan los .py y se copian los nuevos desde el repositorio
## asi no se rompe el desarrollo y se mantiene organozado los DAG.

clear
rm -rf ./dags/*.py
cp ../../Desarrollo/airflow/*.py ./dags/

rm -rf ./src/*
mkdir -p ./src
cp -a ../../Desarrollo/src/. ./src/
