#!/bin/bash
source ../script/tools.sh

## valida que este instalado las carpetas de manera correcta en permisos.
if [ ! -d "./dags" ]; then
  echo "[ERROR] No estan instaladas las carpetas del producto, por favor usar ./instalar.sh"
  exit 1
fi 

## ejecuta el docker con el producto.

if ! docker compose build --progress plain; then
  echo "[ERROR] Build Erroneo revisa configuracion!"
  exit 1
fi 

if ! docker compose up -d > /dev/null; then
  echo "[ERROR] Up Erroneo revisa configuracion!"
  exit 1
fi 

## Lanza función de espera
animacion_wait_url "http://localhost:8080" "AirFlow"