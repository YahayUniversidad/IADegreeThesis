# Airflow

Apache Airflow es una plataforma de gestión de flujo de trabajo de código abierto escrita en Python, donde los flujos de trabajo se crean a través de scripts de Python. Fue creada por Airbnb en octubre de 2014 como solución para la gestión de flujos de trabajo dentro de la empresa.

> [!NOTE]
> Airflow está diseñado bajo el principio de "configuración como código"

## Comandos:

- `instalar.sh`: Bash para instalar el aplicativo, se debe ejecutar una única vez
- `ejecutar.sh`: Bash para ejecutar el server de Airflow, de ejecución periódica.
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

## Flujo de Riesgo Crediticio:

Los flujos de riesgo son dos, el primero para la fase de entrenamiento y el segundo es para la aprobación en la puesta a producción o liberado el dashboard a los usuarios finales.

**Pasos de entrenamiento:** 

- [x] Up datos CSV a la base de datos entrenamiento
- [ ] Validación de data completa por consolas a la Base de datos
- [ ] Lanzamiento de modelo CNN
- [ ] Lanzamiento de modelo TODO
- [ ] Comparativa de lanzamiento
- [ ] Orden de validación por el usuario experto 

**Pasos de producción**

- [ ] Creación/actualización de data mart
- [ ] Generación de data predictiva con usos de modelos de IA
- [ ] Creación/actualización de Dashboards
- [ ] Informe al usuario de para su análisis

---
![icon](../../DocumentosBase/yachayCuadrado.jpg)<br/>***<omar.velez@yachaytech.edu.ec>***<br/>*julio 2026*