#!/bin/bash
source ../script/tools.sh

## Build (siempre, para asegurar imagen actualizada)
docker compose build

## Up contenedor
docker_start_or_up

## Lanza función de espera
animacion_wait_url "http://localhost:8088" "Superset"
