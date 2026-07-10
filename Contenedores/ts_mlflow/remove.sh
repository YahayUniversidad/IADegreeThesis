#!/bin/bash

##
## Contenedor de mlFlow
##
## Este script detiene el contenedor de mlFlow.
##
cd mlflow
cd docker-compose
 
docker compose -p ts_mlflow down