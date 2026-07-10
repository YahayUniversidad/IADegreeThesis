#!/bin/bash
source ../script/tools.sh

cd mlflow
cd docker-compose
docker compose -p ts_mlflow build
docker compose -p ts_mlflow up -d

## Lanza función de espera
animacion_wait_url "http://localhost:5000" "MlFlow"