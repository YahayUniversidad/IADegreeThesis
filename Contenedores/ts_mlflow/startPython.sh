#!/bin/bash

##
## Configuracion para MLFlow mediante python
## Este producto guarda la informacion em mlflow.db y la interfaz web se encuentra en http://localhost:5000
## 
## Guarda unicamente el archivo local.
##
export MLFLOW_TRACKING_URI="http://localhost:5000"
export MLFLOW_TRACKING_USERNAME="admin"
export MLFLOW_TRACKING_PASSWORD="admin123"

if python3 -m pip show mlflow >/dev/null 2>&1; then
	echo "mlflow ya está instalada"
else
	echo "mlflow no está instalada. Instalando..."
	python3 -m pip install mlflow
fi

mlflow server --port 5000