# Airflow

Apache Airflow es una plataforma de gestión de flujo de trabajo de código abierto escrita en Python, donde los flujos de trabajo se crean a través de scripts de Python. Fue creada por Airbnb en octubre de 2014 como solución para la gestión de flujos de trabajo dentro de la empresa.

> [!NOTE]
> Airflow está diseñado bajo el principio de "configuración como código"

## Comandos:

- `ejecutar.sh`: Bash para ejecutar el server de Airflow, de ejecución periódica.
- `instalar.sh`: Bash para instalar el aplicativo, se debe ejecutar una única vez
- `parar.sh`: Bash para parar el server Airflow, de ejecución periódica
- `remove.sh`: Bash para remover el server y sus configuraciones
- `update.sh`: Bash para actualizar los **DAG** (Grafo Acíclico Dirigido)

> [!IMPORTANT]
> Luego de iniciar el proyecto el script indicaran la dirección de ingreso al proyecto.

## Configuración

Para la configuración del sistema tenemos los siguientes volúmenes:

- *data*: Carpeta para cargar la data al sistema
- *dags*: Espacio para cargar los DAG (Grafo Acíclico Dirigido)
- *logs*: en serio?
- *plugins*: Espacio para los componentes extras a la configuración.
- *config*: Carpeta con cambios de configuraciones personalizados.

## Variables de Airflow

Los DAGs del proyecto requieren tres **Variables** de Airflow configuradas desde la UI (Admin → Variables) o por CLI. Estas variables se leen en tiempo de ejecución y pueden sobreescribirse por parámetro al lanzar cada DAG.

| Variable | Tipo | Descripción | Usada por | Valor ejemplo |
|---|---|---|---|---|
| `string_conexion` | string | Cadena de conexión a PostgreSQL (base de datos del proyecto) | Entrenamiento, Inferencia | `postgresql://postgres_usr:admin123@host.docker.internal:5434/postgres_db` |
| `mlflow_uri` | string | URI del servidor MLflow Tracking | Entrenamiento, Inferencia | `http://192.168.0.97:5000` |
| `mlflow_experiment_id` | string | ID del experimento MLflow con el mejor modelo seleccionado | Inferencia | `1` (se obtiene de MLflow tras entrenar) |

> [!NOTE]
> La base de datos de PostgreSQL (`ts_train`) puede darse de baja y recrearse arbitrariamente. Las variables de Airflow apuntan a ella pero no gestionan su ciclo de vida. Si la base se reinicia, hay que reejecutar el DAG de entrenamiento para repoblar los datos.

> [!IMPORTANT]
> `mlflow_experiment_id` se setea manualmente después de revisar los resultados del DAG de entrenamiento. El entrenamiento empuja el mejor experimento a XCom (`mejor_experiment_id`), pero es responsabilidad del operador revisar el resultado en MLflow y persistirlo como Variable antes de ejecutar el DAG de inferencia.

### Crear variables por CLI

```bash
# Desde el contenedor del scheduler
docker exec airflow-scheduler airflow variables set string_conexion "postgresql://postgres_usr:admin123@host.docker.internal:5434/postgres_db"
docker exec airflow-scheduler airflow variables set mlflow_uri "http://192.168.0.97:5000"

# Tras ejecutar el DAG de entrenamiento, revisar MLflow y setear el experiment_id del mejor modelo
docker exec airflow-scheduler airflow variables set mlflow_experiment_id "1"
```

## Flujo de Riesgo Crediticio:

Los flujos de riesgo son dos, el primero para la fase de entrenamiento y el segundo es para la aprobación en la puesta a producción o liberado el dashboard a los usuarios finales.

**Pasos de entrenamiento:** 

- [x] Up datos CSV a la base de datos entrenamiento
- [x] Validación de data completa por consolas a la Base de datos
- [x] Lanzamiento de modelo CNN
- [x] Lanzamiento de modelo lightgbm
- [x] Lanzamiento de modelo MLP
- [x] Comparativa de lanzamiento
- [x] Orden de validación por el usuario experto 

**Pasos de producción**

- [x] Creación/actualización de data mart
- [x] Generación de data predictiva con usos de modelos de IA
- [x] Creación/actualización de Dashboards
- [x] Informe al usuario de para su análisis

---
![icon](../../DocumentosBase/yachayCuadrado.jpg)<br/>***<omar.velez@yachaytech.edu.ec>***<br/>*julio 2026*