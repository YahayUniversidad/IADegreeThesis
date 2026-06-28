if [ ! -d "./dags" ]; then
  echo "No estan instaladas las carpetas del producto, por favor usar ./instalar.sh"
  exit 1
fi 


docker compose build
docker compose up -d

animacion() {
  local caracteres='|/-\'

  printf "Esperando sitio activo: "
  while ! curl -s http://localhost:8080 > /dev/null 2>&1; do
    for i in $(seq 0 3); do
      printf "%s" "${caracteres:$i:1}"
      sleep 0.1
      printf "\b"
    done
    #sleep 30
  done
  echo "Airflow ya está activo en http://localhost:8080"
}

animacion