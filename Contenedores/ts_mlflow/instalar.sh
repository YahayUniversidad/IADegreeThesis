#!/bin/bash

##
## Contenedor de mlFlow
##
## El documento esta en https://mlflow.org/docs/latest/genai/tracing/quickstart/
## 
## Este producto baja la instancia completa. dentro de mlflow y dentro docker-compose.
##
git clone --depth 1 --filter=blob:none --sparse https://github.com/mlflow/mlflow.git
cd mlflow
git sparse-checkout set docker-compose
cd docker-compose
cp .env.dev.example .env
docker compose build