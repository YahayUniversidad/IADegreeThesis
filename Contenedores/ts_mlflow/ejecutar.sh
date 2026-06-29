#!/bin/bash
source ../script/tools.sh

cd mlflow
cd docker-compose
docker compose up -d

## Lanza función de espera
animacion_wait_url "http://localhost:5000" "MlFlow"