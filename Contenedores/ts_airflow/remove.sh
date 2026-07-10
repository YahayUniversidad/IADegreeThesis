#!/bin/bash

./parar.sh

## para y borra el contenedor de Airflow.
docker compose stop
docker compose down
sudo rm -rf plugins/ logs/ data/ dags/ config/ src/