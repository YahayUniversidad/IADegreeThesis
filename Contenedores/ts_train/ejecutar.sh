#!/bin/bash
source ../script/tools.sh

docker compose build
docker compose up -d

## Lanza animacion
animacion_wait_db "localhost" "5432" "PostgreSQL"