#!/bin/bash

# Crear carpetas
mkdir -p dags logs plugins config data src

# Cambiar propietario al usuario actual usando su UID real
sudo chown -R $(id -u):$(id -g) dags logs plugins config data src

# Dar permisos adecuados
chmod -R 755 dags logs plugins config data src

echo "Carpetas creadas con permisos para el usuario $(whoami) (UID: $(id -u))"

./ejecutar.sh