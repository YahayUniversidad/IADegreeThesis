#!/bin/bash
source ../script/tools.sh

## ejecuta el docker con el producto.

if ! docker compose build --progress plain; then
  echo "[ERROR] Build Erroneo revisa configuracion!"
  exit 1
fi 

## Si el contenedor webserver ya existe, solo reiniciar servicios principales.
## airflow_init es one-shot (restart: "no") y no se puede re-ejecutar con start.
if docker compose ps -q airflow_webserver 2>/dev/null | grep -q .; then
  echo "Contenedores existentes detectados, reiniciando..."
  docker compose start redis_srv airflow_webserver airflow_scheduler
else
  echo "Primera vez, creando contenedores..."
  if ! docker compose up -d > /dev/null; then
    echo "[ERROR] Up Erroneo revisa configuracion!"
    exit 1
  fi
fi

## Lanza función de espera
animacion_wait_url "http://localhost:8080" "AirFlow"