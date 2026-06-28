#!/bin/bash
# instalar.sh

# Crear carpetas
mkdir -p dags logs plugins config

# Cambiar propietario al usuario actual usando su UID real
sudo chown -R $(id -u):$(id -g) dags logs plugins config

# Dar permisos adecuados
chmod -R 755 dags logs plugins config

echo "Carpetas creadas con permisos para el usuario $(whoami) (UID: $(id -u))"
