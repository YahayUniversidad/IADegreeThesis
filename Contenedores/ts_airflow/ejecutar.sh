docker compose build
docker compose up -d

while ! curl -s http://localhost:8080 > /dev/null 2>&1; do
  echo "Esperando a que airflow al puerto 8080"
  sleep 2
done
echo "Airflow ya está activo en http://localhost:8080"
