#!/bin/bash

## valida que este instalado las carpetas de manera correcta en permisos.
if [ ! -d "./dags" ]; then
  echo "[ERROR] No estan instaladas las carpetas del producto, por favor usar ./instalar.sh"
  exit 1
fi 

## ejecuta el docker con el producto.

if ! docker compose build > /dev/null; then
  echo "[ERROR] Build Erroneo revisa configuracion!"
  exit 1
fi 

if ! docker compose up -d > /dev/null; then
  echo "[ERROR] Up Erroneo revisa configuracion!"
  exit 1
fi 

## Funcion de animacion para esperar el producto este activo.
## Valida que no exceda los 5 minutos de espera.
animacion() {
  local caracteres='|/-\'
  local tiempo_maximo=300 # 5 minutos en segundos
  local tiempo_inicio=$SECONDS

  printf "Esperando sitio activo: "
  
  while ! curl -s http://localhost:8080 > /dev/null 2>&1; do
    if (( (SECONDS - tiempo_inicio) >= tiempo_maximo )); then
      printf "\n\n[ERROR] Se alcanzó el tiempo límite de 5 minutos y Airflow no inició.\n"
      exit 1
    fi

    for i in $(seq 0 3); do
      printf "%s" "${caracteres:$i:1}"
      sleep 0.1
      printf "\b"
    done
  done
  
  printf "\n\nAirflow ya está activo en http://localhost:8080\n"
  return 0
}

## Lanza función de espera
animacion