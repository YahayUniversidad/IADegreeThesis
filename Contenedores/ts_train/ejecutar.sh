#!/bin/bash
source ../script/tools.sh

docker compose build
docker_start_or_up

## Lanza animacion
animacion_wait_db "localhost" "5434" "PostgreSQL"