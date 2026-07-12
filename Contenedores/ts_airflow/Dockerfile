##
## Docker file modificado para instalar dependencias de airflow
## los requerimientos se encuentran en el archivo requirements.txt
## hay que revisar manualmente las dependencias de airflow y los dag.
## 

FROM apache/airflow:2.10.4
COPY requirements.txt /tmp/requirements.txt
## Tengo timeouts
RUN pip install --no-cache-dir --progress-bar off --default-timeout=180 --retries=10 -r /tmp/requirements.txt