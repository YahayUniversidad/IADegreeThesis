./parar.sh

docker compose stop
docker compose down
sudo rm -rf plugins/ logs/ data/ dags/ config/