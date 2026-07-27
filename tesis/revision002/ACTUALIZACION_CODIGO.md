# Actualización revision002 - Análisis del Código Fuente

## Fecha: Julio 2026

## Archivos actualizados

### 1. chapters/metodology.tex
**Cambios realizados:**

| Sección | Cambio | Color |
|---------|--------|-------|
| Diccionario de variables | Ahora incluye las 21 variables completas con grupo e interpretación | VERDE |
| crisis_flag | Se documentaron las 8 condiciones exactas con pesos y umbral | VERDE |
| crisis_flag | Se añadió advertencia de target leakage (variables judiciales en etiqueta) | ROJO |
| CNN configuración | Se documentó arquitectura completa: kernel=3, dropout=0.3/0.4, batch=32, loss=binary_crossentropy | VERDE |
| MLP configuración | Se documentó arquitectura completa: Dense(128,64), dropout=0.3/0.2, batch=32 | VERDE |
| MLP | Se identificó que NO usa sample_weights (diferencia crítica con CNN) | ROJO |
| LightGBM | Se añadió seed=42, n_jobs=-1, metric=binary_logloss | VERDE |
| Tabla comparativa | Se actualizó con valores reales: batch_size, loss, sample_weights, seed | VERDE |
| División de datos | Se corrigió a 49% train / 21% val / 30% test (no 70/30) | VERDE |
| Validación | Se confirmó que existe conjunto de validación para early stopping | VERDE |

### 2. chapters/conclusions.tex
**Cambios realizados:**

| Sección | Cambio | Color |
|---------|--------|-------|
| Síntesis | Se añadió que el análisis documentó completamente las 8 condiciones, 21 features, arquitecturas y splits | VERDE |
| Objetivo 1 | Se añadió que MLP no usa sample_weights | VERDE |
| Objetivo 2 | Se mencionó la asimetría en fijación de semillas | ROJO |
| Limitaciones | Se cambió "no están documentadas" por "quedó documentada" para crisis_flag | VERDE |
| Limitaciones | Se confirmó riesgo de target leakage con variables judiciales | ROJO |
| Limitaciones | Se documentó protocolo de split 49/21/30 | VERDE |
| Trabajo futuro | Se priorizó ablación de leakage | ROJO |
| Trabajo futuro | Se añadió fijar semillas y añadir sample_weights a MLP | VERDE |

---

## Hallazgos críticos del análisis

### H1: Target Leakage CONFIRMADO
- **Evidencia**: En `queries.py` líneas 318-338, las condiciones 1, 2 y 3 de crisis_flag usan:
  - `creditos_judiciales` (condiciones 1 y 2)
  - `total_costo_judicial` (condición 3)
- **Impacto**: Estas mismas variables aparecen como características de entrada con alta importancia
- **Acción**: Documentar y recomendar ablación excluyendo variables judiciales

### H2: MLP sin sample_weights
- **Evidencia**: En `pipelineMLP.py` línea 269-277, el modelo.fit() NO incluye sample_weight
- **Impacto**: Explica parcialmente por qué MLP predice todo como "no crisis"
- **Acción**: Documentar como limitación y recomendar corrección

### H3: División real 49/21/30
- **Evidencia**: En `pipelineCNN.py` líneas 278-318 y `pipelineMLP.py` líneas 175-204
- **Cálculo**: 70% train initial → 30% de ese se va a val → queda 49% train, 21% val, 30% test
- **Acción**: Corregir en metodología

### H4: CNN usa sample_weights, MLP no
- **CNN** (`pipelineCNN.py` líneas 201-253): Calcula pesos por clase
- **MLP** (`pipelineMLP.py`): No incluye esta función
- **Impacto**: Asimetría en el manejo del desbalance

### H5: Semillas
- **LightGBM**: seed=42 (fija, reproducible)
- **CNN/MLP**: No fijan semilla (no reproducible entre ejecuciones)

---

## Preguntas respondidas del feedback

| # | Pregunta | Respuesta | Fuente |
|---|----------|-----------|--------|
| 1 | Definición crisis_flag | 8 condiciones con pesos, umbral ≥ 5 | queries.py:318-338 |
| 2 | Trazabilidad 20,025 → 293 | Solo bloques con ≥24 meses generan secuencias | pipelineCNN.py:116 |
| 3 | Variables judiciales en crisis_flag | SÍ (leakage confirmado) | queries.py:320-325 |
| 4 | Validación independiente | SÍ (49/21/30) | pipelineCNN.py:278-318 |
| 5 | Test aislado de tuning | SÍ (early stopping usa val_loss) | pipelineCNN.py:362 |
| 6 | Config CNN completa | kernel=3, dropout=0.3-0.4, batch=32, binary_crossentropy | pipelineCNN.py:158-199 |
| 7 | Config MLP completa | Dense(128,64), dropout=0.3-0.2, batch=32, NO sample_weights | pipelineMLP.py:127-160 |

---

## Pendiente para siguientes pasos

1. **Bibliografía**: Agregar las 48 referencias del documento 4
2. **Tablas faltantes**: Crear tablas de trazabilidad, config experimental completa
3. **Figuras**: Corregir captions y recortar imágenes
4. **Gramática**: Revisión ortográfica y de estilo completa
