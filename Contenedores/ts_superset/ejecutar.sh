#!/bin/bash
source ../script/tools.sh

## Up contenedor
docker compose up -d --build

## Lanza función de espera
animacion_wait_url "http://localhost:8088" "Superset"
animacion_wait_url "http://localhost:5008" "Superset MCP"

