## Links

Aprendizaje
https://www.youtube.com/watch?v=PJzIzytxJ2M
## Variables

Al momento se encuentra las variable 

Ubicación en el Path de airflow el respaldo se encuentra en el archivo `variables.json`

| Nombre           | Descripcion                                                                                          |
| ---------------- | ---------------------------------------------------------------------------------------------------- |
| string_conexion  | Conexion a la base de datos, no usa las conexiones internas por problemas en los tiempos de sesiones |
| path_carpeta_csv | Carpeta de trabajo de CSV                                                                            |
## Comandos

Los comandos disponibles para este contenedor son:

| Comando       | Descripción                                                                                                                                                                  |
| ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `instalar.sh` | Genera un capetas y permisos necesarios previos al lanzamiento desde `docker-compose.yml` **No usar**                                                                        |
| `ejecutar.sh` | Ejecuta el contenedor                                                                                                                                                        |
| `update.sh`   | Actualiza los desarrollos del los DAG, mas los elementos de `src` necesarios para ejecutar los pipelines, el desarrollo esta en: `/Desarrollo/airflow/` y `/Desarrollo/src/` |
| `parar.sh`    | Para el contenedor docker                                                                                                                                                    |
| `remover.sh`  | Remueve el contenedor **No usar**                                                                                                                                            |
## Pipilenes

Breve descripción de los pipelines activos.

| Nombre      | Descripción                                                                                  | Variables para ejecución          |
| ----------- | -------------------------------------------------------------------------------------------- | --------------------------------- |
| DAG-ETL-CSV | Toma los csv de información crediticia y los sube al servidor de base de datos se POSTGRESQL | path_carpeta_csv, string_conexion |
|             |                                                                                              |                                   |
|             |                                                                                              |                                   |
## Librerias de los DAG

Los DAG (Grafo Aciclico Dirigido) en ocasiones llama código en la carpeta `src` de los desarrollos que no tienen todas librerías requeridas para su funcionamiento, por tal motivo se debe de actualizar el archivo `requirements.txt` y luego volver a construir el contenedor `build`

> [!WARNING]
> Es de suma importancia tener claro los requerimientos pues si un pipeline nuevo no sube este es el principal punto de observación 

