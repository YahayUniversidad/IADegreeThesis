# Airflow

Apache Airflow es una plataforma de gestión de flujo de trabajo de código abierto escrita en Python, donde los flujos de trabajo se crean a través de scripts de Python. Fue creada por Airbnb en octubre de 2014 como solución para la gestión de flujos de trabajo dentro de la empresa.

> > [!IMPORTANT]
> Airflow está diseñado bajo el principio de "configuración como código"

## Ejecución:

Para ejecutar el proyecto hay que recordar que hay dos instancias el mismo, una primera corrida y una en la que hay que levantar el proyecto de manera regular

### Init

Para iniciar el proyecto se usa los siguientes comandos:

```bash

./instalar.sh

./ejecutar.sh

./parar.sh

```

Para ejecutar el proyecto solo requiere `./ejecutar.sh` y para detenerlo `parar.sh`

> > [!IMPORTANT]
> Luego de iniciar el proyecto el script indicaran la dirección de ingreso al proyecto.

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
![icon](../../DocumentosBase/yachayCuadrado.jpg)

*<omar.velez@yachaytech.edu.ec>*
*julio 2026*