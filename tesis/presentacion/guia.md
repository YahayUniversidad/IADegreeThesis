# Guía para responder las observaciones del revisor

**Proyecto:** Sistema Integrado de Inteligencia de Negocio para la Predicción de Crisis Crediticias mediante técnicas de inteligencia artificial y analítica de negocios
**Autor:** Omar Vélez
**Revisor:** Israel Pineda, Ph.D. — 2026/08/25
**Fuente de observaciones:** `DocumentosBase/FILEOBSERPRE_UITEY-CRP-2026-48.md`

---

## Cómo usar esta guía

Este documento no aplica los cambios a la tesis. Entrega:

1. Estrategia de respuesta por cada observación (O1–O12).
2. Tips de redacción de la carta de respuesta al revisor.
3. Ubicación real en el código fuente `.tex` y Python.
4. Recomendación de acción: aceptar, aceptar con ajuste o justificar con evidencia.

Las referencias `archivo:línea` apuntan al estado actual del manuscrito en `tesis/final/chapters/`. Antes de redactar la carta, verifique que las líneas no hayan cambiado.

---

## Cómo responder al revisor (tips generales)

**Tono y actitud:**

- Agradecer la revisión y reconocer los comentarios positivos (el revisor valora el trabajo como relevante y oportuno).
- Aceptar y corregir primero. Solo justificar cuando exista evidencia verificable en el código o en los datos.
- No discutir el estilo editorial del revisor. Si una sugerencia es de normas editoriales, aplicarla sin debate.
- Ser concreto: citar sección, figura o tabla corregida. Evitar respuestas vagas como "se corrigió" sin indicar dónde.

**Estructura recomendada de la carta:**

- Separar claramente **cambios de contenido** (objetivos, figuras, reproducibilidad, metodología) de **cambios editoriales** (itálicas, captions, redacción).
- Responder punto por punto, en el mismo orden de las observaciones.
- Para cada punto: (a) cita de la observación, (b) respuesta, (c) cambios realizados con ubicación.

**Reglas de oro:**

| Regla | Detalle |
|-------|---------|
| Aceptar primero | Si el revisor tiene razón, corregir y reportar. No justificar lo incorrecto. |
| Evidencia o silencio | Si se justifica, citar código, tabla o figura. No inventar razones. |
| No discutir estilo | Las normas editoriales (itálicas, captions, saltos de párrafo) se aplican sin objeción. |
| Ubicación concreta | Decir "Sección X, página Y" o "Figura Z corregida", no "se revisó el documento". |
| Contradicciones | Si la tesis decía algo incorrecto (ej. semillas), corregir el texto y reportar la verificación. |

---

## Prioridades

| Prioridad | Observaciones | Naturaleza |
|-----------|---------------|------------|
| **P1 — Sustantivas** | O1, O3, O4, O5, O6 | Contenido, metodología, reproducibilidad, figuras |
| **P2 — Representación** | O2 | Diagramas de arquitectura |
| **P3 — Editoriales** | O7–O12 | Redacción, formato, normalización |

**Punto más delicado: O4 (semilla 42).** Existe una contradicción entre el código y la tesis. El código SÍ fija `SEED=42` en los tres modelos, pero el manuscrito afirma que CNN y MLP "no fijan semilla". No basta con decir "se fijó la semilla": hay que corregir el texto que dice lo contrario y reportar la verificación de reproducibilidad.

---

## Fichas por observación

### O1 — Objetivo "diseñar e implementar"

**Observación del revisor:** "Diseñar e implementar" rara vez son un buen objetivo, ya que no queremos construir un sistema solo por el ejercicio de hacerlo, sino para resolver un problema. El objetivo debe alinearse a cómo el sistema resuelve el problema.

**Clasificación:** Contenido / objetivos.

**Estado actual en la tesis:**

| Ubicación | Texto actual | Estado |
|-----------|-------------|--------|
| `introduction.tex:31` | "¿Cómo diseñar e implementar una plataforma..." (pregunta) | Pendiente |
| `introduction.tex:41` | "Diseñar e implementar un prototipo..." (objetivo general) | Pendiente |
| `introduction.tex:49` | "Diseñar e implementar un datamart..." (obj. específico 4) | Pendiente |

**Recomendación:** Aceptar. Reformular los verbos de los objetivos para que enfaticen el *propósito* (integrar, automatizar, comparar, evaluar) en lugar del *acto de construir*.

**Tips de redacción de la respuesta:**

> "Se reformuló el objetivo general y los objetivos específicos 1.7 para alinearlos con el problema que resuelve el sistema: la integración de datos, la comparación multi-horizonte de modelos y la visualización de predicciones para apoyar la identificación anticipada de mora. Los verbos 'diseñar e implementar' se sustituyeron por verbos orientados al resultado (integrar, automatizar, comparar, evaluar)."

**Acción sugerida en el manuscrito:**

- Pregunta de investigación (`introduction.tex:31`): reformular como "¿Cómo puede una plataforma de inteligencia de negocio integrar predicción multi-horizonte de riesgo crediticio...?"
- Objetivo general (`introduction.tex:41`): "Integrar un prototipo de inteligencia de negocio crediticia que automatice el procesamiento de datos, compare modelos de deep learning y gradient boosting para predicción multi-horizonte, y conecte el modelo seleccionado con un datamart y dashboards interactivos."
- Obj. específico 4 (`introduction.tex:49`): "Integrar un datamart en esquema estrella y dashboards que conecten datos históricos y predicciones."

---

### O2 — Diagramas de arquitectura CNN 1D y MLP

**Observación del revisor:** Las arquitecturas de la CNN 1D y del MLP se explicarían mejor con un diagrama que con el extracto del código.

**Clasificación:** Representación visual / metodología.

**Estado actual en la tesis:**

- Las arquitecturas se presentan como `itemize` con capas extraídas del código en `metodology.tex:229-290` (CNN `:231-262`, MLP `:264-288`).
- Existe `images/MM-03 Comparacion de Arquitecturas de Modelos.png` (comparación LightGBM/CNN/MLP) pero no diagramas dedicados por capa de CNN y MLP.

**Recomendación:** Aceptar. Generar diagramas de bloques por capa (tipo "layer diagram") para CNN y MLP, y mantener el `itemize` como complemento técnico.

**Tips de redacción de la respuesta:**

> "Se incorporaron diagramas de bloques que representan la arquitectura por capas de la CNN 1D y del MLP (Figuras nuevas). Los extractos de código se conservan en un anexo para trazabilidad, pero la explicación principal se apoya en los diagramas."

**Acción sugerida:**

- Crear dos figuras nuevas (ej. con draw.io, TikZ o PowerPoint): una para CNN (Input → Conv1D → BN → Dropout → Conv1D → BN → MaxPool → Dropout → Flatten → Dense → Dense → 18 salidas) y otra para MLP (Input → Flatten → Dense → Dropout → Dense → Dropout → 18 salidas).
- Insertar en `metodology.tex` antes de los `itemize` correspondientes.
- Mantener los `itemize` como referencia técnica detallada.

---

### O3 — Reproducibilidad de datamarts y dashboards

**Observación del revisor:** No se evidencia cómo se garantiza la reproducibilidad de los datamarts y dashboards. Incluir cómo se pudieran exportar/importar, y mucho mejor si se puede incluir en el repositorio.

**Clasificación:** Reproducibilidad / operaciones.

**Estado actual en la tesis:**

- `appendix.tex:45` lista lo que *debería* documentarse (incl. reconstruir dashboards) pero sin procedimiento export/import.
- Código real en `Desarrollo/`:
  - `Desarrollo/src/ts_datamart/pipeline.py` (DDL dim_*/fact_*/MVs)
  - `Desarrollo/src/ts_sql/queries.py`
  - `Desarrollo/src/herramientasPersonales/apiDashboards004.py` (creación de dashboards vía REST API de Superset)
  - `Desarrollo/airflow/dag_inferencia.py`, `dag_entrenamiento.py`
- No hay dumps/exportaciones de Superset ni scripts de import en el repositorio (laguna real que señala el revisor).
- Secciones relevantes: `metodology.tex:433-442` (4.12 datamart), `metodology.tex:484-495` (4.14 reproducibilidad), `results.tex:203-214` (5.6 dashboards).

**Recomendación:** Aceptar. Documentar el procedimiento de export/import y, si es posible, incluir artefactos en el repositorio.

**Tips de redacción de la respuesta:**

> "Se documentó el procedimiento de exportación e importación de los datamarts (DDL de dimensiones y tablas de hechos) y de los dashboards de Apache Superset (exportación JSON vía API REST). Los scripts de reconstrucción se incluyen en el repositorio bajo `Desarrollo/src/ts_datamart/` y `Desarrollo/src/herramientasPersonales/`. Se agrega un anexo con los pasos para recrear el entorno analítico desde cero."

**Acción sugerida:**

1. Documentar en `appendix.tex` (o nueva sección de reproducibilidad) el flujo: ejecutar `pipeline.py` → crear MVs → ejecutar `apiDashboards004.py` → importar dashboards desde JSON.
2. Exportar los dashboards de Superset a JSON y agregarlos al repositorio (ej. `Desarrollo/superset_export/`).
3. Mencionar en `metodology.tex:484-495` (sección de reproducibilidad) que los artefactos de datamart y dashboards están versionados.

---

### O4 — Semilla fijada a 42

**Observación del revisor:** El código fija la semilla a 42. Se necesita verificar esta para garantizar la validez de los resultados.

**Clasificación:** Reproducibilidad / contradicción tesis ↔ código.

**Estado actual — HALLAZGO CRÍTICO:**

El código SÍ fija `SEED = 42` en los tres modelos:

| Modelo | Ubicación en código | Evidencia |
|--------|---------------------|-----------|
| CNN | `Desarrollo/src/ts_cnn/__init__.py:29` | Aplicado en `pipelineCNN.py:335-337` (`np.random.seed`, `random.seed`, `tf.random.set_seed`) |
| MLP | `Desarrollo/src/ts_mlp/__init__.py:24` | Aplicado en `pipelineMLP.py:217-219` |
| LightGBM | `Desarrollo/src/ts_lightgbm/__init__.py:38` | `"seed": 42` |

Pero la tesis afirma lo contrario:

| Ubicación | Texto problemático |
|-----------|-------------------|
| `metodology.tex:340` | Tabla `tab:config_modelos`: "Semilla: No fijada" para CNN y MLP |
| `metodology.tex:399` | "la semilla no está fijada para CNN y MLP" |
| `metodology.tex:489` | "CNN y MLP no fijan semilla" |
| `metodology.tex:495` | "CNN y MLP no fijan semilla, por lo que los resultados pueden variar" |
| `conclusions.tex:19` | "CNN y MLP no fijan semilla" |
| `conclusions.tex:45` | "no se fijan semillas para CNN y MLP" |
| `conclusions.tex:56` | "fijar semillas para todos los modelos" (trabajo futuro) |

**Recomendación:** Aceptar. Corregir la documentación de la tesis (los tres modelos fijan semilla 42), verificar reproducibilidad re-ejecutando y comparando métricas, y aclarar que fijar la semilla no sustituye repeticiones multi-semilla.

**Tips de redacción de la respuesta:**

> "Se verificó el código fuente y se confirmó que los tres modelos (CNN, MLP y LightGBM) fijan la semilla en 42. La tesis contenía una afirmación incorrecta al respecto, la cual fue corregida en las secciones 4.8 (Tabla de configuración), 4.10 (limitaciones del protocolo), 4.14 (versionado y reproducibilidad) y en las conclusiones. Se aclara que fijar una semilla garantiza reproducibilidad de una ejecución, pero no sustituye la estimación de variabilidad mediante repeticiones con múltiples semillas, lo cual se mantiene como trabajo futuro."

**Acción sugerida:**

1. Corregir `metodology.tex:340` — cambiar "No fijada" por "42 (fija)" en la tabla `tab:config_modelos` para CNN y MLP.
2. Corregir `metodology.tex:399` — "la semilla está fijada en 42 para los tres modelos; sin embargo, no se realizan repeticiones con múltiples semillas".
3. Corregir `metodology.tex:489` — "Semilla fija: los tres modelos utilizan `seed=42`."
4. Corregir `metodology.tex:495` — actualizar limitación: "no se realizan repeticiones con múltiples semillas para estimar variabilidad".
5. Corregir `conclusions.tex:19,45` — eliminar "no fijan semilla"; mantener la limitación de repeticiones.
6. `conclusions.tex:56` — reformular trabajo futuro: "realizar repeticiones con múltiples semillas (al menos 10)" (ya no "fijar semillas").
7. Opcional pero recomendado: re-ejecutar el pipeline y comparar métricas con las reportadas para confirmar reproducibilidad.

---

### O5 — `crisis_flag` como heurística sin justificación

**Observación del revisor:** `crisis_flag` es una heurística y al parecer no existe una justificación sobre la misma. Esto pudiera incluir un sesgo en el trabajo dependiendo de cómo se esté calculando.

**Clasificación:** Metodología / variable objetivo / sesgo.

**Estado actual en la tesis:**

- La justificación existe en `metodology.tex:197-199`: pesos 3/2/1 basados en "experiencia operativa del equipo de riesgos" y validación experta cualitativa.
- La circularidad de constructo está documentada en `metodology.tex:208-210`: las variables judiciales (`tasa_judicial`, `creditos_judiciales`, `total_costo_judicial`) se usan tanto para definir la etiqueta como características de entrada.
- Figura: `images/MM-07 Definicion de crisis_flag.png`.
- Definición SQL en `Desarrollo/src/ts_sql/queries.py:320+`.
- En `conclusions.tex:43` se reconoce el riesgo de circularidad.

**Recomendación:** Aceptar con matices. La justificación ya existe pero debe ser más visible y robusta. Reforzar la sección y proponer la ablación como respuesta al sesgo.

**Tips de redacción de la respuesta:**

> "La definición de `crisis_flag` se justifica en la Sección 4.5: las ocho condiciones y sus pesos fueron diseñados en colaboración con el equipo de riesgos de la institución, basados en puntos de quiebre históricos observados en la cartera, y validados mediante revisión cualitativa de casos históricos. Se reconoce que la regla es heurística y que las variables judiciales generan una circularidad de constructo (documentada en la misma sección). Para cuantificar el sesgo potencial, se propone como trabajo prioritario una ablación que excluya las variables judiciales del conjunto de predictores (Sección 6.7, Trabajo futuro). Se fortaleció la justificación de los umbrales y pesos en el manuscrito."

**Acción sugerida:**

1. En `metodology.tex:197-199`, expandir la justificación: incluir tabla de umbrales con referencia a percentiles históricos si están disponibles, o al menos reforzar la validación experta.
2. Asegurar que la sección de limitaciones (`conclusions.tex:43`) mantenga la advertencia de circularidad.
3. En la carta, ser transparente: la regla es heurística, está validada cualitativamente, y la ablación es el experimento necesario para cuantificar el sesgo.

---

### O6 — Figura de importancia de características (inconsistencia)

**Observación del revisor:** La figura muestra nombres como `num_creditos_trend`, `*_median`, `*_std`, `*_mean` y `*_last`. Esas variables no forman parte del vector aplanado de 6×21 descrito en la tesis ni de los nombres generados por el código final (`variable_t-6` a `variable_t-1`). Además, la leyenda afirma que predominan `tasa_judicial` y `creditos_judiciales`, pero ninguna aparece entre las 20 barras mostradas.

**Clasificación:** Figura / inconsistencia técnica crítica.

**Estado actual — CONFIRMADO:**

- `images/lgbm_importancia_features.png` muestra 20 barras con sufijos agregados (`*_trend`, `*_median`, `*_std`, `*_mean`, `*_last`, `*_min`) y **ninguna** variable judicial.
- El caption en `results.tex:124` (`fig:lgbm_features`, Figura 5.5) afirma que predominan `tasa_judicial` y `creditos_judiciales` — **lo cual no coincide con la imagen**.
- El código final nombra features `{col}_t-{1..6}` (`Desarrollo/src/ts_lightgbm/model.py:152`, flatten en `:77-102`) → vector aplanado 6×21=126 (`metodology.tex:117,234,269-270,312`).
- Nombres correctos ya persistidos en `Desarrollo/noteBooks/output/modelos_lightgbm/config_lgbm_18m.json` (ej. `num_creditos_t-6`).
- La figura proviene de un pipeline agregado previo, no del pipeline de ventanas actual.

**Recomendación:** Aceptar. Regenerar la figura desde el pipeline actual y corregir el caption. Respuesta técnica extensa en Anexo C.

**Tips de redacción de la respuesta:**

> "Se identificó que la figura de importancia de características correspondía a una versión previa del pipeline que utilizaba features agregadas (tendencia, mediana, desviación, media, último valor), y no al pipeline final basado en ventanas temporales de 6 meses × 21 características (vector de 126 nombres `{variable}_t-6` a `{variable}_t-1`). Se regeneró la figura con los nombres de features del modelo final y se corrigió el caption para reflejar fielmente las variables mostradas. Se agradece la observación que permitió detectar esta inconsistencia."

**Acción sugerida:** Ver Anexo C para el plan detallado de regeneración.

---

### O7 — Línea fuera de bordes en el Resumen

**Observación del revisor:** En el resumen existe una línea fuera de los bordes del párrafo.

**Clasificación:** Editorial / tipografía.

**Estado actual:** `resumen.tex` — posible desborde tipográfico. Revisar compilación PDF.

**Recomendación:** Aceptar.

**Tip de respuesta:** "Se corrigió el desborde tipográfico en el resumen."

**Acción sugerida:** Compilar el PDF y verificar visualmente el resumen. Ajustar `\sloppy`, `\emergencystretch` o reformular la línea problemática.

---

### O8 — Saltos de línea entre párrafos

**Observación del revisor:** No se necesitan los saltos de línea entre párrafo y párrafo según las normas editoriales.

**Clasificación:** Editorial / formato.

**Estado actual:** `resumen.tex` y `abstract.tex` usan `\\` al final de cada párrafo. También aparecen en `introduction.tex`, `metodology.tex`, `conclusions.tex` y otros capítulos.

**Recomendación:** Aceptar. Eliminar los `\\` entre párrafos en todo el documento.

**Tip de respuesta:** "Se eliminaron los saltos de línea manuales entre párrafos en todo el documento, conforme a las normas editoriales."

**Acción sugerida:** Buscar y eliminar `\\` al final de párrafos en todos los `.tex` de `chapters/`. Mantener `\\` solo dentro de tablas o donde sea tipográficamente necesario.

---

### O9 — Palabras extranjeras en itálica

**Observación del revisor:** Las palabras diferentes al idioma principal (español) deben ir en itálica. Por ejemplo: "credit risk prediction", "et al.".

**Clasificación:** Editorial / estilo.

**Estado actual:**

| Término | Ubicación | Estado |
|---------|-----------|--------|
| `et al.` | `fundamentals.tex:77`, `state_of_art.tex:9,11` | Sin itálica |
| `credit risk prediction` | `state_of_art.tex:5` | Sin itálica |
| `multilayer perceptron` | `fundamentals.tex:21` | Sin itálica |

**Recomendación:** Aceptar.

**Tip de respuesta:** "Se aplicó itálica a las palabras extranjeras en todo el documento (*credit risk prediction*, *et al.*, *multilayer perceptron*, etc.)."

**Acción sugerida:** Envolver en `\textit{}` todos los términos en inglés que no sean nombres propios de tecnologías (Apache Airflow, PostgreSQL, etc. no llevan itálica).

---

### O10 — Caption de tablas sobre la tabla

**Observación del revisor:** El *caption* de las tablas va sobre la tabla.

**Clasificación:** Editorial / formato.

**Estado actual:** En `results.tex` y `metodology.tex`, los `\caption` de tablas van **después** del `\end{tabular}` (ej. `results.tex:20,58,108`; `metodology.tex:107`). El estándar editorial (normas APA, IEEE, y la mayoría de universidades) coloca el caption **antes** de la tabla.

**Recomendación:** Aceptar.

**Tip de respuesta:** "Se reposicionaron los captions de todas las tablas para que aparezcan encima de la tabla, conforme a las normas editoriales."

**Acción sugerida:** En cada `\begin{table}`, mover `\caption{...}` y `\label{...}` a una línea inmediatamente después de `\centering`, antes de `\begin{tabular}`.

---

### O11 — Tabla de ejemplos de cambios sugeridos

**Observación del revisor:** Tabla con 9 ejemplos puntuales de cambios de redacción.

**Clasificación:** Editorial / redacción.

**Estado actual detallado:**

| Ubicación | Fragmento original | Sugerencia del revisor | Estado |
|-----------|-------------------|----------------------|--------|
| Título | "mediante las técnicas de análisis de Inteligencia artificial y de negocio" | "mediante técnicas de inteligencia artificial y analítica de negocios" | Parcial — `main.tex:189` ya tiene "…técnicas de Inteligencia Artificial y Analítica de negocios"; falta normalizar a minúsculas |
| Resumen párr. 2 | "registro sistemático de experimentos que facilita el registro" | "registro sistemático que facilita la trazabilidad de los experimentos" | **Aplicado** (`resumen.tex:3`) |
| Resumen párr. 4 | "procesamiento modelado" | "procesamiento, modelado" | **Aplicado** (`resumen.tex:7`) — falta "de extremo a extremo **de** procesamiento…" |
| Sección 2.1 | "Lo que es el origen del desbalance." | "Esta asimetría origina el desbalance de clases." | **Pendiente** (`fundamentals.tex:7`) |
| Sección 2.3 | "MLP (del Multilayer Perceptron)" | "MLP (del inglés *multilayer perceptron*)" | Parcial — falta itálica en `fundamentals.tex:21` |
| Sección 1.7 obj. 2 | Punto y coma antes de "mediante" | Sustituir por coma o eliminar | **Aplicado** (`introduction.tex:47`) |
| Sección 4.4 | "mediante la combinaciones" | "mediante la combinación" | **Aplicado** (`metodology.tex:115`) |
| Figura 5.2 | `variablepredictora` | `variable predictora` | **Aplicado** (`results.tex:65`) |
| Cap. 3 | "Varios set de datos" | "Varios conjuntos de datos" | **Aplicado** (`state_of_art.tex:39`) |

**Recomendación:** Aceptar. Completar los pendientes y verificar los ya aplicados.

**Tip de respuesta:** "Se aplicaron las nueve correcciones de redacción sugeridas. Los cambios se realizaron en las secciones indicadas. Se adjunta tabla de equivalencias."

**Acción sugerida:**

1. Título (`main.tex:189`): normalizar a "mediante técnicas de inteligencia artificial y analítica de negocios" (minúsculas).
2. `fundamentals.tex:7`: cambiar "lo que es el origen del problema de desbalance de clases" por "esta asimetría origina el desbalance de clases".
3. `fundamentals.tex:21`: agregar itálica → "MLP (del inglés *multilayer perceptron*)".
4. `resumen.tex:7`: revisar si falta "de extremo a extremo de procesamiento, modelado…".

---

### O12 — Normalización de mayúsculas, anglicismos y acrónimos

**Observación del revisor:** Normalizar mayúsculas (`gradient boosting`, `deep learning`, inteligencia artificial), anglicismos y acrónimos. XAI debe expandirse en su primera aparición. Para DAG, la traducción correcta es "grafo acíclico dirigido", no "gráfico".

**Clasificación:** Editorial / normalización terminológica.

**Estado actual:**

| Problema | Ubicación | Corrección |
|----------|-----------|------------|
| "Gráfico Acíclico Dirigido" | `metodology.tex:115` | "grafo acíclico dirigido" |
| XAI sin expandir | `state_of_art.tex:13` | Expandir: "Explicabilidad en Inteligencia Artificial (XAI, del inglés *eXplainable AI*)" |
| "Gradient Boosting" vs "gradient boosting" | `introduction.tex:37` vs `resumen.tex:5` | Unificar (recomendado: minúscula salvo inicio de oración) |
| "deep learning" inconsistente | Varios | Unificar; itálica si se considera extranjerismo |

**Recomendación:** Aceptar.

**Tip de respuesta:** "Se normalizaron las mayúsculas de los términos técnicos (*gradient boosting*, *deep learning*, inteligencia artificial), se expandió XAI en su primera aparición y se corrigió la traducción de DAG a 'grafo acíclico dirigido'."

**Acción sugerida:**

1. `metodology.tex:115`: "Gráfico Acíclico Dirigido" → "grafo acíclico dirigido".
2. `state_of_art.tex:13`: expandir XAI en primera aparición.
3. Búsqueda global de "Gradient Boosting" / "gradient boosting" / "Deep Learning" / "deep learning" y unificar criterio (minúscula, itálica si aplica).
4. Verificar que el glosario (`glosaries.tex`) sea coherente con las formas normalizadas.

---

## Anexo A — Plantilla de carta de respuesta

```
Estimado Dr. Israel Pineda:

Agradezco sus observaciones al proyecto de graduación "Sistema Integrado de
Inteligencia de Negocio para la Predicción de Crisis Crediticias...". Sus
comentarios han sido de gran utilidad para fortalecer el manuscrito.

A continuación se presenta la respuesta punto por punto.

─────────────────────────────────────────────────────────
1. [Observación: copiar texto del revisor]

   Respuesta: [Aceptar / Aceptar con ajustes / Justificar con evidencia]
   Cambios realizados:
   - Sección X.X (página N): [descripción del cambio]
   - Figura Y / Tabla Z: [descripción del cambio]

─────────────────────────────────────────────────────────
2. [Observación: copiar texto del revisor]

   Respuesta: [...]
   Cambios realizados:
   - [...]

[Repetir para cada observación]

─────────────────────────────────────────────────────────

Los cambios de contenido (objetivos, figuras, reproducibilidad) se detallan
en los puntos X–Y. Los cambios editoriales (itálicas, captions, redacción)
se detallan en los puntos Z–W.

Quedo atento a sus comentarios.

Cordialmente,
Omar Vélez
```

---

## Anexo B — Checklist editorial rápido

Use esta lista antes de compilar la versión corregida:

- [ ] Itálicas en palabras extranjeras (*credit risk prediction*, *et al.*, *multilayer perceptron*)
- [ ] Captions de tablas **encima** de la tabla
- [ ] "grafo acíclico dirigido" (no "gráfico")
- [ ] XAI expandido en primera aparición
- [ ] Sin saltos de línea `\\` entre párrafos
- [ ] Minúsculas normalizadas: *gradient boosting*, *deep learning*, inteligencia artificial
- [ ] Título con "inteligencia artificial y analítica de negocios" (minúsculas)
- [ ] `resumen.tex:7` — verificar "de extremo a extremo de procesamiento, modelado…"
- [ ] `fundamentals.tex:7` — "Esta asimetría origina el desbalance de clases"
- [ ] `fundamentals.tex:21` — itálica en *multilayer perceptron*
- [ ] Tabla `tab:config_modelos` (`metodology.tex:340`) — semilla "42 (fija)" para CNN y MLP
- [ ] `conclusions.tex` — sin afirmaciones de "no fijan semilla"
- [ ] Figura `lgbm_importancia_features.png` regenerada con nombres correctos
- [ ] Caption `fig:lgbm_features` (`results.tex:124`) coherente con la imagen
- [ ] Resumen sin líneas fuera de bordes (verificar PDF compilado)

---

## Anexo C — Figura de importancia de características (O6): respuesta técnica y plan de regeneración

### Origen de la discrepancia

La figura `images/lgbm_importancia_features.png` proviene de un **pipeline agregado previo** que calculaba estadísticas por variable (`*_trend`, `*_median`, `*_std`, `*_mean`, `*_last`, `*_min`). El pipeline final de la tesis utiliza **ventanas temporales** de 6 meses × 21 características, generando un vector aplanado de 126 features con nombres `{variable}_t-6` a `{variable}_t-1`.

| Aspecto | Figura actual (incorrecta) | Pipeline final (correcto) |
|---------|---------------------------|--------------------------|
| Nombres | `num_creditos_trend`, `*_median`, etc. | `num_creditos_t-6`, `num_creditos_t-5`, …, `num_creditos_t-1` |
| N features | ~20 barras agregadas | 126 features (6×21) |
| Variables judiciales | No aparecen | `tasa_judicial_t-k`, `creditos_judiciales_t-k`, `total_costo_judicial_t-k` |
| Origen | Pipeline agregado previo | `model.py` flatten (`Desarrollo/src/ts_lightgbm/model.py:77-102,152`) |

### Plan de regeneración

1. **Obtener los nombres correctos de features** desde `Desarrollo/noteBooks/output/modelos_lightgbm/config_lgbm_18m.json` (ya persistidos, ej. `num_creditos_t-6`).
2. **Extraer las importancias** del modelo LightGBM entrenado (o re-entrenar con el pipeline actual si no se conservan los artefactos).
3. **Regenerar la figura** con los 126 nombres (o las top-20 si se prefiere legibilidad), usando `Desarrollo/src/ts_lightgbm/dashboard.py` o un script dedicado.
4. **Corregir el caption** en `results.tex:124` (`fig:lgbm_features`): describir fielmente las variables mostradas. Si las variables judiciales aparecen entre las top features, mencionar la circularidad de constructo (Sección 4.5). Si no aparecen, corregir la afirmación del caption.
5. **Verificar coherencia** con el texto de `results.tex:119` ("La Figura 5.5 muestra la importancia interna de las características…").

### Párrafo modelo para la carta de respuesta

> "Se identificó que la Figura 5.5 (importancia de características de LightGBM) correspondía a una versión previa del pipeline que utilizaba features agregadas por variable (tendencia, mediana, desviación estándar, media, último valor y mínimo), generando nombres como `num_creditos_trend` y `monto_total_median`. El pipeline final de la tesis, en cambio, utiliza ventanas temporales de 6 meses × 21 características, produciendo un vector aplanado de 126 features con nombres `{variable}_t-6` a `{variable}_t-1` (ver Sección 4.4 y 4.6). En consecuencia, la figura no representaba el modelo descrito en el manuscrito y la leyenda que mencionaba la predominancia de `tasa_judicial` y `creditos_judiciales` no correspondía a las barras mostradas. Se regeneró la figura a partir de las importancias del modelo final (nombres verificables en `config_lgbm_18m.json`) y se corrigió el caption para reflejar fielmente las variables visualizadas. Se agradece la observación que permitió detectar esta inconsistencia entre la figura y el texto."

---

*Fin de la guía.*
