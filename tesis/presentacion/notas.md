# Notas de Presentación — Tarjetas de Referencia Rápida

**Defensa de tesis:** Sistema Integrado de Inteligencia de Negocio para la Predicción de Crisis Crediticias
**Autor:** Omar Vélez Bayas — Maestría en Inteligencia Artificial, Universidad Yachay Tech

---

## Tarjeta 1 — Contexto y Problema

| Dato | Valor |
|------|-------|
| Mora crediticia saludable | **< 5%** |
| Sector | Economía social y solidaria (cooperativas) |
| Institución | Cooperativa de Ahorro y Crédito Jardín Azuayo |
| Periodo de datos | 2015–2026 (la presentación dice 2019–2026; verificar) |
| Volumen | ~1.8 millones de registros/año |
| Fuentes | Préstamos, amortizaciones, juicios |

**Tres brechas del problema:**

1. **Datos:** no hay flujo único para integrar, limpiar y agregar la información crediticia.
2. **Analítica:** los modelos no se comparan bajo un protocolo multi-horizonte común.
3. **Operativa:** los resultados del modelado no se registran, almacenan y visualizan de forma automatizada.

---

## Tarjeta 2 — Conceptos Clave

| Concepto | Definición corta (para decir en voz alta) |
|----------|------------------------------------------|
| **Riesgo crediticio** | Probabilidad de incumplimiento de obligaciones financieras. |
| **Inteligencia de negocio (BI)** | Consolidación de datos operativos en datamarts + dashboards para apoyar decisiones. |
| **Datamart** | Subconjunto de un data warehouse enfocado en un dominio (cartera/riesgo). |
| **Esquema estrella** | Tabla de hechos central + tablas de dimensión (tiempo, riesgo, sector, sucursal). |
| **Predicción multi-horizonte** | Estimar la probabilidad de crisis para varios plazos simultáneamente (h = 1 … 18 meses). |
| **Clases desbalanceadas** | La clase positiva (crisis) es minoritaria: ~12% vs ~88%. |
| **Validación temporal** | Split cronológico (no aleatorio) para evitar fuga de información del futuro. |
| **Fuga de información (data leakage)** | Cuando una feature contiene datos que no estarían disponibles al momento de predecir. |
| **Circularidad de constructo** | Las mismas variables (judiciales) definen la etiqueta y son predictores → infla la importancia. |
| **MLOps** | Prácticas para automatizar el ciclo de vida de modelos ML: entrenamiento, registro, inferencia. |
| **ETL** | Extract, Transform, Load — integración de fuentes operativas al repositorio analítico. |
| **AUC-ROC** | Área bajo la curva ROC; mide la capacidad de discriminar entre clases (0.5 = azar, 1.0 = perfecto). |
| **Recall** | Proporción de crisis reales que el modelo logra identificar (sensibilidad). |
| **Early stopping** | Detener el entrenamiento cuando la pérdida en validación deja de mejorar. |
| **XAI** | *eXplainable AI* — inteligencia artificial explicable (ej. SHAP, importancia de features). |
| **DAG** | *Grafo acíclico dirigido* — estructura de tareas orquestadas en Airflow. |

---

## Tarjeta 3 — Variable Objetivo: `crisis_flag`

| Parámetro | Valor |
|-----------|-------|
| Tipo | Binaria (1 = crisis, 0 = no crisis) |
| Regla | 8 condiciones con pesos acumulativos (3 / 2 / 1) |
| Umbral | Suma de pesos **≥ 5** → crisis |
| Distribución | 39.660 sin crisis (88%) · 5.417 con crisis (12%) |
| Total bloques-mes | 45.077 |
| Validación | Juicio experto del equipo de riesgos (cualitativa) |

**Las 8 condiciones (resumen):**

| # | Condición | Peso |
|---|-----------|------|
| 1 | `tasa_judicial > 5%` | 3 |
| 2 | `tasa_judicial > 2%` | 1 |
| 3 | `costo_judicial > 0` y costo/promedio > 10% | 2 |
| 4 | `gestión_cobro > 0` y gestión/promedio > 5% | 1 |
| 5 | `tasa_cierre > 30%` (peso 2) o `> 20%` (peso 1) | 2 / 1 |
| 6 | `plazo_promedio > 36 meses` | 1 |
| 7 | `plazo_promedio > 60 meses` | 1 |
| 8 | `tasa_interes_promedio > 15%` | 1 |

**Advertencia (posible pregunta del tribunal):** las variables judiciales (`tasa_judicial`, `creditos_judiciales`, `total_costo_judicial`) se usan tanto para definir la etiqueta como para predecirla → **circularidad de constructo**. Respuesta: está documentada en la Sección 4.5; la ablación excluyendo esas variables es trabajo futuro prioritario.

---

## Tarjeta 4 — Modelos: Nombres y Arquitecturas

| Modelo | Nombre completo | Tipo | Salida |
|--------|----------------|------|--------|
| **CNN** | *Convolutional Neural Network* (1D) | Red neuronal convolucional | 18 × `Dense(1, sigmoid)` |
| **MLP** | *Multilayer Perceptron* (perceptrón multicapa) | Red neuronal densa | 18 × `Dense(1, sigmoid)` |
| **LightGBM** | *Light Gradient Boosting Machine* | Gradient boosting (GBDT) | 18 clasificadores independientes |

### CNN — Arquitectura

CNN = Convolutional Neural Network (red neuronal convolucional): es un tipo de red neuronal que aplica filtros convolucionales para detectar patrones locales en secuencias, como tendencias o formas en series temporales. En este caso, la entrada es una matriz 6×21 y la red aprende representaciones jerárquicas antes de clasificar.

```
Input(6×21) → Conv1D(64, k=3, relu) → BatchNorm → Dropout(0.3)
            → Conv1D(128, k=3, relu) → BatchNorm → MaxPool(2) → Dropout(0.3)
            → Flatten → Dense(128, relu) → BatchNorm → Dropout(0.4)
            → Dense(64, relu) → Dropout(0.3)
            → 18 × Dense(1, sigmoid)
```

| Hiperparámetro | Valor |
|----------------|-------|
| Pérdida | `binary_crossentropy` |
| Optimizador | Adam (lr = 0.001) |
| Épocas máximas | 100 |
| Batch size | 32 |
| Early stopping | paciencia = 10, monitorea `val_loss` |
| Sample weights | **SÍ** (`total / (2 × n_clase)`) |
| Escalado | MinMaxScaler (fit solo en train) |
| Clipping | Quantiles 0.01–0.99 |
| Semilla | **42** |

### MLP — Arquitectura

(MLP significa *Multilayer Perceptron* o perceptrón multicapa: una red neuronal formada por capas de neuronas densamente conectadas. Cada capa transforma la información recibida para aprender relaciones entre las variables. En este caso, la secuencia de 6 × 21 datos se aplana a 126 valores y pasa por dos capas ocultas antes de generar las predicciones.)

```
Input(6×21) → Flatten(126) → Dense(128, relu) → Dropout(0.3)
            → Dense(64, relu) → Dropout(0.2)
            → 18 × Dense(1, sigmoid)
```

| Hiperparámetro | Valor |
|----------------|-------|
| Pérdida | `binary_crossentropy` |
| Optimizador | Adam (lr = 0.001) |
| Épocas máximas | 100 |
| Batch size | 32 |
| Early stopping | paciencia = 10, monitorea `val_loss` |
| Sample weights | **NO** (no compensa desbalance) |
| Escalado | MinMaxScaler (fit solo en train) |
| Clipping | Quantiles 0.01–0.99 |
| Semilla | **42** |

### LightGBM — Configuración

LightGBM (*Light Gradient Boosting Machine*) es un algoritmo de boosting basado en árboles de decisión, desarrollado por Microsoft y optimizado para trabajar con conjuntos de datos grandes, con muchas columnas y alta dimensionalidad. A diferencia de otros métodos de boosting, construye árboles con crecimiento hoja a hoja (*leaf-wise*), lo que suele mejorar la velocidad y la capacidad de captura de interacciones complejas. Además, usa técnicas como histogramas y muestreo de datos para acelerar el entrenamiento sin perder mucho rendimiento predictivo. En esta tesis, LightGBM se usa como modelo de referencia para la predicción de crisis crediticia, aprovechando su rapidez, robustez y buen desempeño en tareas de clasificación binaria con variables tabulares.

| Hiperparámetro | Valor |
|----------------|-------|
| `objective` | binary |
| `metric` | binary_logloss |
| `boosting_type` | gbdt |
| `num_leaves` | 31 |
| `learning_rate` | 0.05 |
| `feature_fraction` | 0.8 |
| `bagging_fraction` | 0.8 |
| `bagging_freq` | 5 |
| `seed` | **42** |
| `scale_pos_weight` | 5.67 |
| Early stopping | 50 rondas sin mejora |
| Max boost rounds | 1000 |
| Clipping | No |

---

## Tarjeta 5 — Datos Numéricos del Dataset

| Métrica | Valor |
|---------|-------|
| Registros en MV (bloque-mes) | **45.077** |
| Características numéricas | **21** |
| Ventana temporal | **6 meses** (entrada) |
| Horizontes de predicción | **18** (h1 … h18) |
| Vector aplanado por muestra | 6 × 21 = **126 valores** |
| Secuencias válidas (≥24 meses historial) | **25.434** |
| Entrenamiento (49%) | **12.463** |
| Validación (21%) | **5.340** |
| Prueba (30%) | **7.631** |
| Sin crisis (clase 0) | 39.660 (88%) |
| Con crisis (clase 1) | 5.417 (12%) |

**Fuentes de datos:**

| Fuente | Filas aprox. |
|--------|-------------|
| CABECERA_PRESTAMOS | 1.044.194 |
| AMORTIZACAL_PRESTAMOS | 24.350.210 |
| RECUPERACION_PRESTAMOS | 15.741 |

**Predicciones almacenadas:**

| Dato | Valor |
|------|-------|
| Predicciones en `fact_predicciones` | **56.541** filas |
| Horizontes | 18 (`prob_h01` … `prob_h18`) |
| Rangos de plazo | corto (1–3M), medio (4–6M), largo (7–18M) |
| Períodos | 133 |
| Sucursales | 65 |
| Sectores | 21 |
| Vista `vw_predicciones_horizonte` | 1.017.738 filas (formato largo) |

---

## Tarjeta 6 — Resultados de los Modelos

### Tabla de comparación (según tesis — resultados reales)

| Métrica | LightGBM (promedio) | CNN (global) | MLP (global) |
|---------|---------------------|--------------|--------------|
| **Accuracy** | 0,917 | 0,090 | 0,910 |
| **Precision** | 0,571 | 0,090 | 0,000 |
| **Recall** | 0,391 | 1,000 | 0,000 |
| **AUC-ROC** | **0,800** | 0,500 | 0,500 |

> **NOTA:** La presentación muestra métricas diferentes (CNN AUC 0.85, MLP 0.84, LGBM 0.87). Verificar cuál cifra usar en la defensa. Los valores de la tesis son los documentados en `results.tex`.

### LightGBM por horizonte (selección)

| Horizonte | Accuracy | Precision | Recall | AUC-ROC |
|-----------|----------|-----------|--------|---------|
| 1 mes | 0,937 | 0,694 | 0,542 | **0,874** |
| 3 meses | 0,942 | 0,837 | 0,512 | 0,869 |
| 6 meses | 0,927 | 0,632 | 0,525 | 0,838 |
| 12 meses | 0,906 | 0,447 | 0,369 | 0,765 |
| 18 meses | 0,897 | 0,500 | 0,034 | **0,702** |
| **Promedio** | **0,917** | **0,571** | **0,391** | **0,800** |

**Dato clave para la defensa:** a partir de h=8, el recall cae a 0 → el modelo no detecta crisis en horizontes largos con umbral 0.5. **La utilidad operativa se concentra en h ≤ 6.**

### Selección del modelo

- **Criterio:** AUC-ROC promedio de los 18 horizontes.
- **Seleccionado:** LightGBM.
- **Comparación inicial vs automatizada:** Accuracy 0,917 → 0,878; AUC-ROC 0,800 → 0,846.

---

## Tarjeta 6b — ¿Por qué solo h ≤ 6 es fiable?

### Tabla completa de métricas de LightGBM por horizonte

| Horizonte | Accuracy | Precision | Recall | AUC-ROC | ¿Operativo? |
|-----------|----------|-----------|--------|---------|-------------|
| 1 mes | 0,937 | 0,694 | 0,542 | **0,874** | Sí |
| 3 meses | 0,942 | 0,837 | 0,512 | 0,869 | Sí |
| 6 meses | 0,927 | 0,632 | 0,525 | 0,838 | Sí |
| 8 meses | — | — | **0,000** | — | **No** |
| 12 meses | 0,906 | 0,447 | 0,369 | 0,765 | No |
| 18 meses | 0,897 | 0,500 | **0,034** | **0,702** | No |
| **Promedio** | **0,917** | **0,571** | **0,391** | **0,800** | — |

### Tres razones

1. **Incertidumbre temporal creciente.** A mayor distancia entre la información actual y el evento futuro, mayor la incertidumbre. Predecir a 18 meses es intrínsecamente más difícil que a 1 mes (`fundamentals.tex:17-19`).

2. **Recall inutilizable en h > 6.** A partir de **h = 8**, el recall cae a **0** bajo el umbral de 0,5: el modelo no identifica *ningún* caso de crisis. A h = 18, el recall es 0,034 (detecta solo el 3% de las crisis reales). Un AUC moderado (> 0,70) puede coexistir con detección casi nula (`results.tex:220`, `conclusions.tex:21`).

3. **Sin calibración ni umbral optimizado.** El umbral 0,5 es una decisión de implementación, no un umbral de negocio validado. Sin análisis de costos de error (falsos negativos vs falsos positivos), los horizontes largos no pueden considerarse operativamente útiles (`results.tex:220`, `conclusions.tex:21`).

### Cifras clave para recordar

| Número | Significado |
|--------|-------------|
| **h ≤ 6** | Rango de utilidad operativa |
| **h = 8** | Punto donde recall = 0 |
| **0,874** | Mejor AUC-ROC (h = 1) |
| **0,838** | AUC-ROC en el límite operativo (h = 6) |
| **0,702** | Peor AUC-ROC (h = 18) |
| **0,542 → 0,034** | Caída de recall de h=1 a h=18 |
| **0,5** | Umbral de clasificación utilizado |

### Respuesta modelo para la defensa

> "Aunque el sistema genera predicciones para los 18 horizontes, el análisis muestra que a partir del horizonte 8 el recall cae a cero: el modelo no detecta ninguna crisis con el umbral de 0,5. Por eso la utilidad operativa se concentra en los horizontes cortos (h ≤ 6), donde el AUC-ROC se mantiene por encima de 0,83 y el recall en niveles aceptables (~0,52). Los horizontes largos requieren calibración, selección de umbral y análisis de costos de error antes de ser considerados útiles."

---

## Tarjeta 7 — Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|-----------|---------|
| Base de datos | PostgreSQL | 15 |
| Orquestación | Apache Airflow | 2.10 |
| Tracking ML | MLflow | 3.14.0 |
| Visualización | Apache Superset | 6.1.0 |
| Deep Learning | TensorFlow | 2.21.0 |
| Gradient Boosting | LightGBM | 4.6.0 |
| Procesamiento | Python + Polars | 3.12 |
| Sistema operativo | Ubuntu | 24.04 LTS |
| Hardware | Intel i7 12va gen, 32 GB RAM, sin GPU | — |

---

## Tarjeta 8 — Pipeline MLOps y DAGs

| DAG | Cron | Flujo |
|-----|------|-------|
| **DAG-Entrenamiento** | `0 3 1 * *` (mensual) | estructura → CSV → datamart → EDA/EVA → [CNN ∥ MLP ∥ LGBM] → selección (AUC) → MLflow |
| **DAG-Inferencia** | `0 6 * * *` (diario) | estructura → CSV → datamart → predicción → Superset |

**Pasos del flujo:**

1. **Entrenamiento** (`dag_entrenamiento.py`): CSV → EDA → CNN + MLP + LightGBM → MLflow.
2. **Inferencia** (`dag_inferencia.py`): CSV → Datamart → Predicción (`prob_h01`…`prob_h18`) → Superset.
3. **Registro** (MLflow): métricas, artefactos, versionado de modelos.
4. **Aprobación humana:** experto revisa y aprueba/rechaza antes de producción.

---

## Tarjeta 9 — Datamart y Dashboards

### Esquema estrella

| Tabla | Contenido |
|-------|-----------|
| `dim_tiempo` | Mes, año, trimestre |
| `dim_riesgo` | Código y descripción de riesgo |
| `dim_sector` | Código y descripción de sector |
| `dim_sucursal` | Sucursal y provincia |
| `fact_creditos_mensual` | 27 métricas por bloque |
| `fact_predicciones` | Predicciones multi-horizonte (56.541 filas) |

### 5 Dashboards en Superset

| Dashboard | Contenido |
|-----------|-----------|
| Tendencia de Crisis | Evolución temporal por sucursal y sector |
| Predicciones de Crisis | Probabilidad de crisis por período |
| Resumen por Sucursal | Métricas agregadas (créditos, mora, judicial) |
| Predicción por Horizonte | Evolución por rango de plazo (corto/medio/largo) |
| Comparación por Segmento | Rangos por sucursal y sector + heatmap |

**Filtros interactivos:** rango de plazo, período, sucursal, sector.

---

## Tarjeta 10 — Análisis EVA (Evaluación de Variables Analíticas)

| Métrica | Uso |
|---------|-----|
| Pearson / Spearman | Correlación lineal y monótona |
| VIF | Multicolinealidad |
| Chi-cuadrado | Asociación categórica |
| Cohen's d / t-test | Diferencia entre grupos |
| Shapiro-Wilk / KS | Normalidad |

**Dashboard 3×3:** heatmap de correlaciones, distribución del target, boxplots de mora, VIF, recomendaciones automáticas (INCLUIR/EXCLUIR).

**EDA optimizado:** Polars Lazy Mode + procesamiento por año (2015–2025) → resuelve el problema de 12M+ registros que agotaban RAM.

---

## Tarjeta 11 — Preguntas Probables y Respuestas

### "¿Por qué LightGBM y no una red neuronal?"

> LightGBM obtuvo el mayor AUC-ROC promedio (0,800 vs 0,500 de CNN y MLP) bajo las configuraciones documentadas. Las redes tuvieron problemas: CNN no convergió (loss ~12,5) y MLP predijo todo como "no crisis" (no usa sample_weights). La literatura confirma que los árboles potenciados suelen superar a las redes en datos tabulares con muestras moderadas.

### "¿Qué es la circularidad de constructo?"

> Las variables judiciales (`tasa_judicial`, `creditos_judiciales`, `total_costo_judicial`) se usan en las condiciones 1-3 de `crisis_flag` y también como features de entrada. Esto puede inflar artificialmente la importancia de esas variables. Está documentado en la Sección 4.5 y la ablación correspondiente es trabajo futuro prioritario.

### "¿Por qué el recall cae tanto en horizontes largos?"

> A mayor distancia temporal, mayor incertidumbre. A partir de h=8, el recall cae a 0 con umbral 0.5. Esto significa que el modelo no detecta crisis en horizontes intermedios/largos. La utilidad operativa se concentra en h ≤ 6. Se recomienda calibración y selección de umbral antes de uso productivo.

### "¿El sistema es reproducible?"

> Sí: los tres modelos fijan semilla=42, MLflow registra experimentos, los contenedores Docker versionan el entorno y el código está en GitHub. Limitación: no se hicieron repeticiones multi-semilla para estimar variabilidad (trabajo futuro).

### "¿Cuál es la contribución principal?"

> La integración end-to-end: ETL automatizado → datamart → comparación multi-horizonte de 3 modelos → MLOps (Airflow + MLflow) → dashboards para toma de decisiones. No es solo un modelo, es un sistema completo y reproducible.

### "¿La mora se redujo?"

> No se afirma eso. El prototipo genera predicciones y las visualiza. La validación operativa y la evaluación de impacto en decisiones quedan a cargo de la institución. Es un prototipo funcional, no un sistema productivo validado.

### "¿Cuántos datos se usaron?"

> 45.077 bloques-mes con 21 características, generando 25.434 secuencias válidas (ventana de 6 meses + 24 meses de historial mínimo). División: 12.463 train / 5.340 validación / 7.631 prueba. Las 3 fuentes originales suman ~25 millones de filas.

---

## Tarjeta 12 — Diferencias entre Presentación y Tesis (verificar antes de defender)

| Tema | Presentación dice | Tesis dice | Recomendación |
|------|-------------------|------------|---------------|
| Umbral `crisis_flag` | score ≥ 4 | score ≥ 5 | Usar **≥ 5** (el de la tesis) |
| Métricas CNN | AUC 0.85 | AUC 0.500 | Usar los de la **tesis** (resultados reales) |
| Métricas MLP | AUC 0.84 | AUC 0.500 | Usar los de la **tesis** |
| Métricas LGBM | AUC 0.87 | AUC 0.800 (promedio) | Aclarar: 0.874 es el AUC del horizonte h=1 |
| Periodo datos | 2019–2026 | 2015–2026 | Usar **2015–2026** (más completo) |
| N° de dashboards | 5 | 7 (metodology.tex:435) | Verificar cuál es el número real |
| CSVs | 51 archivos | 3 fuentes institucionales | Aclarar: 3 fuentes, múltiples archivos CSV |

---

## Tarjeta 13 — Datos Rápidos para Decir de Memoria

| Número | Qué es |
|--------|--------|
| **21** | Características por bloque-mes |
| **6** | Meses de ventana de entrada |
| **18** | Horizontes de predicción (h1–h18) |
| **126** | Valores del vector aplanado (6×21) |
| **45.077** | Bloques-mes en la vista materializada |
| **25.434** | Secuencias válidas generadas |
| **88% / 12%** | Distribución no crisis / crisis |
| **42** | Semilla fijada en los 3 modelos |
| **0,874** | Mejor AUC-ROC (LightGBM, h=1) |
| **0,702** | Peor AUC-ROC (LightGBM, h=18) |
| **56.541** | Predicciones almacenadas |
| **5** | Dashboards en Superset |
| **≥ 5** | Umbral de crisis_flag (suma de pesos) |
| **5.67** | `scale_pos_weight` de LightGBM |
| **3** | Modelos comparados (CNN, MLP, LightGBM) |
| **1** | Modelo seleccionado (LightGBM) |

---

*Fin de las notas.*
