# Resumen de Cambios - revision002

## Codificación de Colores

- **\textcolor{green}{VERDE}**: Contenido **NUEVO** que no existía en revision001
- **\textcolor{red}{ROJO}**: Contenido **MODIFICADO/CORREGIDO** de revision001

## Archivos Creados en revision002

### main.tex
- **ROJO**: Título del capítulo cambiado de "Estado del Arte" a "Revisión de Literatura"
- **ROJO**: Capítulo 5 renombrado de "Resultados" a "Resultados y Discusión"
- **VERDE**: Capítulo 2 "Marco Teórico" (antes estaba vacío en revision001)

### chapters/introduction.tex (COMPLETAMENTE REESCRITO)
- **ROJO**: Toda la introducción reescrita con tono prudente
- **ROJO**: Contexto, Motivación y Planteamiento del problema reformulados
- **ROJO**: Pregunta de investigación cambiada (eliminado "control de mora")
- **ROJO**: Objetivos reformulados (sin causalidad no demostrada)
- **ROJO**: Contribuciones con lenguaje más conservador
- **ROJO**: Organización del documento actualizada

### chapters/fundamentals.tex (COMPLETAMENTE NUEVO)
- **VERDE**: Capítulo 2 "Marco Teórico" - NO EXISTÍA en revision001
- **VERDE**: Riesgo crediticio y clasificación binaria
- **VERDE**: Inteligencia de negocio, data warehouse y datamart
- **VERDE**: Predicción multi-horizonte
- **VERDE**: Clases desbalanceadas
- **VERDE**: Modelos evaluados (LightGBM, CNN, MLP)
- **VERDE**: Validación temporal y fuga de información
- **VERDE**: Métricas de evaluación (con ecuaciones)
- **VERDE**: MLOps y observabilidad

### chapters/state_of_art.tex (REESCRITO)
- **ROJO**: Denominado "Revisión de Literatura" (no "revisión sistemática")
- **ROJO**: Protocolo de búsqueda documentado
- **ROJO**: Tabla comparativa de estudios (CUADRO 3.1)
- **ROJO**: Brechas reformuladas con tono prudente

### chapters/metodology.tex (REESTRUCTURADO + ACTUALIZADO CON CÓDIGO)
- **ROJO**: Diseño de investigación añadido (aplicado, cuantitativo, experimental)
- **ROJO**: Tabla de fuentes de datos mejorada
- **VERDE**: Tabla de trazabilidad de datos (20,025 → conjuntos)
- **VERDE**: Diccionario de variables COMPLETO (21 de 21) extraído del código
- **VERDE**: Definición completa de crisis_flag (8 condiciones con pesos)
- **VERDE**: Advertencia de target leakage (variables judiciales en etiqueta)
- **VERDE**: Configuración CNN completa (kernel=3, dropout=0.3-0.4, batch=32, loss)
- **VERDE**: Configuración MLP completa (Dense 128/64, dropout=0.3-0.2, batch=32)
- **VERDE**: Diferencia crítica: MLP NO usa sample_weights
- **VERDE**: LightGBM seed=42, n_jobs=-1, metric=binary_logloss
- **VERDE**: Tabla comparativa completa con valores reales
- **VERDE**: División real: 49% train / 21% val / 30% test
- **VERDE**: Tabla de recursos computacionales
- **VERDE**: Sección de versionado y reproducibilidad
- **ROJO**: Error 128→126 corregido
- **VERDE**: Generación de horizontes (nueva sección)

### chapters/results.tex (REESCRITO)
- **ROJO**: Tono prudente en todas las interpretaciones
- **ROJO**: Eliminado "Alta confiabilidad" / "Baja confianza"
- **ROJO**: Tabla 5.4 con caption corregido
- **ROJO**: CNN/MLP descritos como "requiere auditoría"
- **ROJO**: Discusión añadida al final del capítulo
- **VERDE**: Caption Fig 5.1 (heatmap) mejorado con descripción de correlaciones
- **VERDE**: Caption Fig 5.2 (AUC individual) definido como "AUC-ROC calculada individualmente"
- **VERDE**: Caption Fig 5.3 (crisis temporal) con lenguaje descriptivo, sin causalidad COVID
- **VERDE**: Caption Fig 5.5 (feature importance) definido método "split importance"
- **VERDE**: Caption Fig 5.6 (CNN loss) explicado comportamiento de pérdida

### chapters/conclusions.tex (COMPLETAMENTE REESCRITO + ACTUALIZADO)
- **ROJO**: Estructura: Síntesis → Objetivo General → Objetivos Específicos → Contribuciones → Limitaciones → Trabajo Futuro
- **ROJO**: Eliminado "cumplimiento satisfactorio"
- **ROJO**: Eliminado "sistema completo" / "modelo ganador"
- **VERDE**: Se documentó completamente crisis_flag (ya no "no están documentadas")
- **VERDE**: Se confirmó target leakage con variables judiciales
- **VERDE**: Se documentó protocolo de split 49/21/30
- **ROJO**: Limitaciones incluyen leakage, validación, estadística, calibración
- **ROJO**: Trabajo futuro prioriza ablación de leakage y fijar semillas

### chapters/resumen.tex (REESCRITO)
- **ROJO**: Ortografía corregida
- **ROJO**: Tono prudente (sin "demostrar superioridad")

### chapters/abstract.tex (NUEVO)
- **VERDE**: Abstract en inglés (NO EXISTÍA en revision001)

### chapters/appendix.tex (MEJORADO)
- **VERDE**: Sección de reproducibilidad añadida
- **VERDE**: Repositorios con commit/etiqueta estable

### bib/referencias.bib (COMPLETAMENTE ACTUALIZADA)
- **ROJO**: Mismas 23 referencias originales
- **VERDE**: +48 referencias recomendadas del documento 4_Lista_referencias
- **VERDE**: Organizadas por categoría: revisiones, árboles/redes, multi-periodo, interpretabilidad, MLOps, BI, cooperativas, regulatorio
- **VERDE**: Incluye fuentes ecuatorianas (cooperativas, SEPS)
- **VERDE**: Incluye documentos regulatorios (NIST, EBA, Basel, PRISMA)
- **Total**: 71 referencias

## Cambios Críticos Aplicados

1. **Error aritmético**: 6×21=128 → 126 (CORREGIDO)
2. **Leakage de variables judiciales**: CONFIRMADO y documentado con evidencia del código
3. **"Comparación rigurosa"**: Cambiada a "comparación experimental" (CORREGIDO)
4. **"Pipeline MLOps completo"**: Cambiado a "pipeline automatizado" (CORREGIDO)
5. **"Control de mora"**: Eliminado de pregunta/objetivos (CORREGIDO)
6. **Tabla 5.4 caption**: Corregido de "1 mes" a "promedio" (CORREGIDO)
7. **Conclusiones**: Reestructuradas con tono prudente (REESCRITO)
8. **Marco Teórico**: Capítulo 2 completo añadido (NUEVO)
9. **crisis_flag**: 8 condiciones documentadas con pesos y umbral (NUEVO)
10. **Configuración CNN/MLP**: Arquitecturas completas documentadas (NUEVO)
11. **División datos**: Corregido a 49/21/30 (no 70/30) (CORREGIDO)
12. **MLP sample_weights**: Identificado que NO los usa (NUEVO)
13. **Diccionario variables**: 21 variables completas (NUEVO)

## Estado de Preguntas Críticas

| # | Pregunta | Estado | Respuesta |
|---|----------|--------|-----------|
| 1 | Definición crisis_flag | ✅ RESUELTO | 8 condiciones con pesos, umbral ≥ 5 |
| 2 | Trazabilidad 20,025 → 293 | ✅ RESUELTO | Solo bloques con ≥24 meses generan secuencias |
| 3 | Variables judiciales en crisis_flag | ✅ RESUELTO | SÍ (leakage confirmado) |
| 4 | Validación independiente | ✅ RESUELTO | SÍ (49/21/30) |
| 5 | Test aislado de tuning | ✅ RESUELTO | SÍ (early stopping usa val_loss) |
| 6 | Config CNN completa | ✅ RESUELTO | kernel=3, dropout=0.3-0.4, batch=32 |
| 7 | Config MLP completa | ✅ RESUELTO | Dense(128,64), dropout=0.3-0.2, batch=32, NO sample_weights |

## Pendiente (Requiere Input del Usuario)

- [ ] Validación de expertos (número, perfil, procedimiento)
- [ ] Hardware y tiempos de ejecución
- [ ] Repeticiones con múltiples semillas
- [ ] Conteos exactos por horizonte
- [ ] PR-AUC y calibración (si se calcularon)

## Pendiente (Puedo Yo Hacer)

- [x] Agregar 48 referencias del documento 4_Lista_referencias ✅ COMPLETADO
- [x] Crear tablas faltantes (trazabilidad, config completa, recursos) ✅ COMPLETADO
- [x] Corregir captions de figuras ✅ COMPLETADO
- [x] Revisión ortográfica y gramatical ✅ COMPLETADO

## Estructura de Capítulos

```
Capítulo 1: Introducción (REESCRITO)
Capítulo 2: Marco Teórico (NUEVO - no existía)
Capítulo 3: Revisión de Literatura (REESCRITO)
Capítulo 4: Metodología (REESTRUCTURADO)
Capítulo 5: Resultados y Discusión (REESCRITO + COMBINADO)
Capítulo 6: Conclusiones (REESCRITO COMPLETAMENTE)
Bibliografía (MISMAS + 1 NUEVA)
Apéndices (MEJORADO)
```
