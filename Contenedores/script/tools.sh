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

## Funcion de animacion para esperar que una base de datos PostgreSQL este activa
## Se usa 3 segundos para no hacer creer que e sun ataque.
## $1 Host de la base de datos (ej: localhost, db, postgres)
## $2 Puerto
## $3 Nombre descriptivo para mostrar
animacion_wait_db() {
  local host=$1
  local port=$2
  local nombre=$3
  local caracteres='|/-\'
  local tiempo_maximo=300 # 5 minutos en segundos
  local tiempo_inicio=$SECONDS

  printf "Esperando base de datos %s activa: " "$nombre"

  while ! timeout 1 bash -c "echo > /dev/tcp/${host}/${port}" 2>/dev/null; do
    if (( (SECONDS - tiempo_inicio) >= tiempo_maximo )); then
      printf "\n\n[ERROR] Se alcanzó el tiempo límite de 5 minutos y %s no inició.\n" "$nombre"
      exit 1
    fi

    for i in $(seq 0 3); do
      printf "%s" "${caracteres:$i:1}"
      sleep 3 
      printf "\b"
    done
  done

  printf "\n\n%s ya está activo en %s:%s\n" "$nombre" "$host" "$port"
  return 0
}