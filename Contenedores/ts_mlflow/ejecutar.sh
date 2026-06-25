cd mlflow
cd docker-compose
docker compose up -d

while ! curl -s http://localhost:5000 > /dev/null 2>&1; do
  echo "Esperando a que MLflow al puerto 5000"
  sleep 2
done
echo "MLflow ya está activo en http://localhost:5000"
