#!/bin/bash

## para recargar los DAGs de airflow, se eliminan los .py y se copian los nuevos desde el repositorio
## asi no se rompe el desarrollo y se mantiene organozado los DAG.

clear
rm -rf ./dags/*.py
rm -rf ./dags/*.ipynb
count_dags=$(find ../../Desarrollo/airflow -maxdepth 1 -type f \( -name '*.py' -o -name '*.ipynb' \) | wc -l)
find ../../Desarrollo/airflow -maxdepth 1 -type f \( -name '*.py' -o -name '*.ipynb' \) -exec cp {} ./dags/ \;
echo -e "DAGs actualizados correctamente. Archivos copiados: ${count_dags}."

rm -rf ./src/*
mkdir -p ./src
count_src=$(find ../../Desarrollo/src -type f \( -name '*.py' -o -name '*.ipynb' \) | wc -l)
find ../../Desarrollo/src -type f \( -name '*.py' -o -name '*.ipynb' \) -print0 | while IFS= read -r -d '' file; do
	rel_path="${file#../../Desarrollo/src/}"
	mkdir -p "./src/$(dirname "$rel_path")"
	cp "$file" "./src/$rel_path"
done
echo -e "src actualizados correctamente. Archivos copiados: ${count_src}."
