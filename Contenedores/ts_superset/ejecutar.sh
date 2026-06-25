docker compose up -d --build

while ! curl -s http://localhost:8088 > /dev/null 2>&1; do
  echo "Esperando a que Superset esté disponible en el puerto 8088"
  sleep 2
done
echo "Superset ya está activo en http://localhost:8088"
