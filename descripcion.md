mi proyecto va ha realizar lo siguiente:

usando airflow, se va crear un flujo de trabajo que:

- 1 Inicia leyendo tres archivos csv el primero tiene informacion de creditos, el segundo la amortizacion mensual de los creditos y el tercero tiene los datos de los creditos demandados y su recuperacion.

- 2 Luego sube estos datos a una base de datos PostgreSQL relacional e incremental.

- 3 Luego ocupa esta data para crear e incrementar un datamart, que contenga la informacion de los creditos, su amortizacion y recuperacion, y la categoriza en diferentes dimensiones, como por ejemplo: tipo de credito, estado del credito, fecha de amortizacion, entre otros, y en especial una dimensión de tiempo que permita analizar la evolución de los creditos a lo largo del tiempo en anios, semestres, trimestres y meses.

- 4 La data del paso 2 se usa para entrenar un modelo de inteligencia artificial que permita predecir la probabilidad el riesgo de incumplimiento de los creditos, y que permita categorizar los creditos en diferentes niveles de riesgo, este modelo utiliza el producto mlflow para el versionamiento de los modelos y la gestion de experimentos, y se entrena con diferentes algoritmos la momento modelo CNN multi-horizonte y de manera paralela un LightGBM, y se comparan los resultados de ambos modelos para seleccionar el mejor modelo que permita predecir el riesgo de incumplimiento de los creditos.

- 5 Luego de la revision de un experto en el area de creditos, se selecciona el mejor modelo y se implementa en un endpoint de prediccion que permite a los usuarios consultar la probabilidad de incumplimiento de los creditos, esto lo hara revisando los estados en mlflow y seleccionando el modelo que tenga el mejor desempeño, tarea que informara por un pequeno cliente aprobando o rechazando el modelo.

- 6 Si el modelo seleccionado es aprobado, este se usara para predecir la probabilidad de incumplimiento de los creditos y se guardara en el datamart que fue creado o actualizado en el paso 3. 

- 7 finalmente Usando el MCP de apache Superset, se crean/actualizan dashboards que permitan visualizar la información de los creditos, su amortizacion y recuperacion, y la prediccion del riesgo de incumplimiento de los creditos, permitiendo a los usuarios analizar la informacion de manera interactiva y tomar decisiones informadas.
