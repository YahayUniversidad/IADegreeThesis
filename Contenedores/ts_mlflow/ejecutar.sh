#!/bin/bash
source ../script/tools.sh

cd mlflow
cd docker-compose
docker compose -p ts_mlflow build
docker_start_or_up -p ts_mlflow

## Lanza función de espera
animacion_wait_url "http://localhost:5000" "MlFlow"