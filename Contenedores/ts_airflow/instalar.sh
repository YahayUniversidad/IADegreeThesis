#!/bin/bash

# Crear carpetas
mkdir -p dags logs plugins config data

# Copia DAGS
cp ../../Desarrollo/config/airflow/*.py ./dags/

# Cambiar propietario al usuario actual usando su UID real
sudo chown -R $(id -u):$(id -g) dags logs plugins config data

# Dar permisos adecuados
chmod -R 755 dags logs plugins config data

echo "Carpetas creadas con permisos para el usuario $(whoami) (UID: $(id -u))"

./ejecutar.sh