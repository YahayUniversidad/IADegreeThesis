#!/bin/bash

## Funcion de animacion para esperar el producto este activo.
## Valida que no exceda los 5 minutos de espera.
## $1 Url a ser probada
## $2 nombre producto 
animacion_wait_url() {
  local url=$1
  local nombre=$2 
  local caracteres='|/-\'
  local tiempo_maximo=300 # 5 minutos en segundos
  local tiempo_inicio=$SECONDS

  printf "Esperando sitio activo: "
  
  while ! curl -s ${url} > /dev/null 2>&1; do
    if (( (SECONDS - tiempo_inicio) >= tiempo_maximo )); then
      printf "\n\n[ERROR] Se alcanzó el tiempo límite de 5 minutos y ${nombre} no inició.\n"
      exit 1
    fi

    for i in $(seq 0 3); do
      printf "%s" "${caracteres:$i:1}"
      sleep 0.1
      printf "\b"
    done
  done
  
  printf "\n\n${nombre} ya está activo en ${url}\n"
  return 0
}