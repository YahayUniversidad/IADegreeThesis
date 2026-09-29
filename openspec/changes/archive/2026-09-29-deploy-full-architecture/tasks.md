# Tasks

## 1. Verificación de prerrequisitos

- [x] 1.1 Verificar que Docker y Docker Compose están instalados ejecutando `docker --version` y `docker compose --version` y confirmar que retornan versiones válidas
- [x] 1.2 Verificar que los puertos 5434, 8080, 8088 y 5000 están disponibles ejecutando `netstat -tuln | grep -E ':(5434|8080|8088|5000)\s'` y confirmar que no hay procesos escuchando
- [x] 1.3 Verificar que los archivos CSV históricos existen en la ruta esperada (`Contenedores/ts_airflow/data/csv/`) y contienen datos válidos
- [x] 1.4 Verificar que los archivos `.env` existen para cada servicio core (`ts_train`, `ts_airflow`, `ts_superset`) y contienen las credenciales correctas

## 2. Configuración de recursos Docker (19GB de 32GB para servicios core)

- [x] 2.1 Configurar límite de memoria en `Contenedores/ts_train/docker-compose.yml` para el servicio postgres_srv con `mem_limit: 6g` y `memswap_limit: 6g`
- [x] 2.2 Configurar límite de memoria en `Contenedores/ts_airflow/docker-compose.yml` para los servicios airflow_webserver y airflow_scheduler con `mem_limit: 6g` y `memswap_limit: 6g` cada uno
- [x] 2.3 Configurar límite de memoria en `Contenedores/ts_superset/docker-compose.yml` para el servicio superset_srv con `mem_limit: 4g` y `memswap_limit: 4g`
- [x] 2.4 Verificar configuración de ts_mlflow (NO MODIFICAR su docker-compose.yml, usa configuración del proveedor con ~3GB)
- [x] 2.5 Verificar que la suma total de límites core no excede 19GB: ts_train(6GB) + ts_airflow(6GB) + ts_superset(4GB) + ts_mlflow(3GB) = 19GB
- [x] 2.6 Documentar que el RAG usa MCP Python local (puerto 8000), NO ts_mcp Docker

## 3. Despliegue de contenedores Docker core (orden crítico)

- [x] 3.1 **PRIMERO**: Desplegar ts_train (fuente de datos) ejecutando `cd Contenedores/ts_train && ./ejecutar.sh` y verificar que está disponible en el puerto 5434 con `pg_isready -h localhost -p 5434`
- [x] 3.2 Verificar que init.sh se ejecutó correctamente consultando los esquemas creados: `psql -h localhost -p 5434 -U postgres_usr -d postgres_db -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name IN ('datamart', 'embeddings', 'airflow', 'superset')"`
- [x] 3.3 Verificar que la extensión pgvector está habilitada: `psql -h localhost -p 5434 -U postgres_usr -d postgres_db -c "SELECT * FROM pg_extension WHERE extname = 'vector'"`
- [x] 3.4 **SEGUNDO**: Desplegar ts_airflow ejecutando `cd Contenedores/ts_airflow && ./ejecutar.sh` y verificar que está disponible en el puerto 8080 con `curl -s http://localhost:8080/health`
- [x] 3.5 **TERCERO**: Desplegar ts_superset ejecutando `cd Contenedores/ts_superset && ./ejecutar.sh` y verificar que está disponible en el puerto 8088 con `curl -s http://localhost:8088/health`
- [x] 3.6 **CUARTO**: Desplegar ts_mlflow (INDEPENDIENTE, base de datos del proveedor) ejecutando `cd Contenedores/ts_mlflow && ./ejecutar.sh` y verificar que está disponible en el puerto 5000 con `curl -s http://localhost:5000`
- [x] 3.7 Verificar que los límites de memoria se aplicaron correctamente ejecutando `docker stats --no-stream` y confirmando que cada contenedor está dentro de su límite

## 4. Configuración de Airflow (ejecutado por DAG de entrenamiento)

- [x] 4.1 Acceder a la interfaz de Airflow en `http://localhost:8080` con las credenciales admin/admin y verificar que el DAG de entrenamiento está visible
- [x] 4.2 Configurar las variables de Airflow (string_conexion, mlflow_uri) desde la interfaz o CLI de Airflow
- [x] 4.3 Ejecutar el DAG de entrenamiento manualmente desde la interfaz de Airflow y verificar que completa todas las tareas (crear estructura → cargar CSV → datamart → EDA → entrenar modelos → MLflow)
- [x] 4.4 Verificar que los datos se cargaron correctamente en PostgreSQL consultando las tablas operativas (creditos, amortizacion, juicios)

## 5. Construcción del datamart (ejecutado por DAG de entrenamiento)

- [x] 5.1 Verificar que las tablas de dimensión (dim_tiempo, dim_riesgo, dim_sector, dim_sucursal) fueron creadas y contienen datos
- [x] 5.2 Verificar que la tabla de hechos (fact_creditos_mensual) fue creada y contiene métricas agregadas
- [x] 5.3 Verificar que las vistas materializadas (mv_creditos_mensuales, mv_creditos, mv_predicciones) fueron creadas y contienen datos
- [x] 5.4 Ejecutar consultas de validación para confirmar que los datos del datamart son consistentes con los datos operativos

## 6. Configuración de Superset

- [x] 6.1 Acceder a la interfaz de Superset en `http://localhost:8088` con las credenciales admin/admin
- [x] 6.2 Configurar la conexión a PostgreSQL en Superset apuntando al datamart (host: localhost, puerto: 5434, base de datos: postgres_db)
- [x] 6.3 Crear un dashboard de tendencia de crisis que muestre la evolución temporal de créditos en crisis por sucursal y sector
- [x] 6.4 Crear un dashboard de predicciones que muestre las predicciones de probabilidad de crisis por período
- [x] 6.5 Crear un dashboard de resumen por sucursal que muestre métricas agregadas (total créditos, monto, mora, judicial)

## 7. Verificación del flujo de datos

- [x] 7.1 Verificar que los datos fluyen desde PostgreSQL → Datamart → Superset ejecutando consultas en Superset que retornen datos del datamart
- [x] 7.2 Ejecutar el DAG de inferencia manualmente y verificar que actualiza los datos en Superset
- [x] 7.3 Verificar que los dashboards de Superset se actualizan automáticamente cuando se ejecuta el DAG de inferencia

## 8. Preparación para RAG (en ts_train)

- [x] 8.1 Verificar que la tabla de embeddings existe en ts_train ejecutando `psql -h localhost -p 5434 -U postgres_usr -d postgres_db -c "SELECT COUNT(*) FROM embeddings.embeddings"`
- [x] 8.2 Generar embeddings para el datamart ejecutando `python -m src.ts_embeddings.pipeline` y verificar que se almacenan correctamente en ts_train
- [x] 8.3 Probar la búsqueda semántica ejecutando `python -c "from src.ts_embeddings.store import query_documents; docs = query_documents('creditos', n_results=3); print(len(docs), 'documentos encontrados')"` y verificar que retorna resultados de ts_train

## 9. Verificación de ts_mlflow (independiente)

- [x] 9.1 Verificar que ts_mlflow está corriendo independientemente con `curl -s http://localhost:5000` y confirmar que NO usa la base de datos de ts_train
- [x] 9.2 Documentar que ts_mlflow tiene su propia base de datos del proveedor y NO debe modificarse

## 10. ts_mcp Docker (OPCIONAL - NO requerido para RAG)

- [x] 10.1 Verificar que ts_mcp Docker NO es necesario para el sistema RAG (el RAG usa MCP Python local en puerto 8000)
- [x] 10.2 Si se necesita acceso MCP externo, desplegar ts_mcp ejecutando `cd Contenedores/ts_mcp && ./ejecutar.sh` y verificar puertos 5009 y 5011
- [x] 10.3 Documentar que ts_mcp Docker es opcional y puede omitirse en despliegues estándar

## 11. Documentación y limpieza

- [x] 11.1 Actualizar README.md con instrucciones claras de cómo levantar la arquitectura core (pre-requisitos, despliegue en orden, configuración de Superset)
- [x] 11.2 Crear script de verificación `verify_architecture.sh` que verifique que todos los servicios core están corriendo y conectados
- [x] 11.3 Documentar los dashboards creados en Superset con capturas de pantalla y descripciones
- [x] 11.4 Verificar que no hay errores en los logs de los servicios y que el sistema funciona de extremo a extremo
- [x] 11.5 Documentar explícitamente que ts_train es la fuente de datos principal y ts_mlflow es independiente con base de datos del proveedor
- [x] 11.6 Documentar la distribución de memoria Docker core: ts_train(6GB) + ts_airflow(6GB) + ts_superset(4GB) + ts_mlflow(3GB) = 19GB
- [x] 11.7 Documentar que ts_mcp Docker es OPCIONAL y NO necesario para el RAG (el RAG usa MCP Python local en puerto 8000)