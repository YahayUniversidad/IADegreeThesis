# Design

## Context

La presentación actual (`presentacion_anteproyecto.md`) tiene 402 líneas con ~20 diapositivas organizadas por tema (MORA, DATA, Problema, Objetivos, Arquitectura, ETL, EVA, EDA, Modelos, Predicción, Dashboards, Estado, Perspectivas). El contenido refleja el anteproyecto: solo CNN + LightGBM, dashboards "en desarrollo", FastAPI como parte del alcance, y título diferente al final.

La tesis final (`tesis/final/chapters/`) tiene 6 capítulos: Introducción → Marco Teórico → Estado del Arte → Metodología → Resultados → Conclusiones. Los modelos evaluados son CNN, MLP y LightGBM. Los dashboards están completos (5 en total). No hay FastAPI en el alcance final.

## Goals / Non-Goals

**Goals:**

- Renombrar folder y archivos con `git mv` para preservar historial.
- Reorganizar las diapositivas siguiendo la estructura de capítulos de la tesis.
- Actualizar contenido: título, modelos (3), dashboards (5), estado (completado).
- Mantener el estilo visual (Marp, CSS, fondos) intacto.

**Non-Goals:**

- Cambiar el diseño visual, CSS o fondos de las diapositivas.
- Modificar la tesis LaTeX.
- Regenerar PDF/PPTX/HTML (el usuario puede hacerlo con Marp).

## Decisions

### D1: Estructura de diapositivas alineada a los 6 capítulos

**Decisión:** Organizar en 6 bloques temáticos que mapeen 1:1 con los capítulos:

| Bloque | Capítulo tesis | Diapositivas |
|--------|---------------|--------------|
| 1. Introducción | Ch.1 | Portada, Contexto/Mora, Data, Problema, Objetivos |
| 2. Marco Teórico | Ch.2 | Conceptos clave (riesgo, BI, multi-horizonte, MLOps) |
| 3. Estado del Arte | Ch.3 | Brechas identificadas |
| 4. Metodología | Ch.4 | Arquitectura, ETL/Datamart, Modelos, Pipeline |
| 5. Resultados | Ch.5 | Comparación modelos, Dashboards, Métricas |
| 6. Conclusiones | Ch.6 | Hallazgos, Contribuciones, Trabajo futuro |

**Razón:** El usuario pidió explícitamente "empatar con el documento de tesis". La correspondencia 1:1 facilita la presentación oral siguiendo el documento.

### D2: Rename con `git mv`

**Decisión:** Usar `git mv` para folder y archivos, no `cp` + `rm`.

**Razón:** Preserva el historial de git y permite `git log --follow`.

### D3: Actualizar referencias internas en CSS/HTML

**Decisión:** Actualizar `presentacion_anteproyecto.css` → `presentacion.css` y las referencias dentro de `presentacion_anteproyecto.html` → `presentacion.html`. Las referencias a imágenes (`tech.jpg`, `negocio.jpg`, etc.) no cambian porque las imágenes no se renombran.

### D4: Contenido de Resultados con datos reales

**Decisión:** Usar los resultados del sistema actual: LightGBM seleccionado, 18 horizontes, 56.541 predicciones, 5 dashboards (3 históricos + 2 nuevos de horizonte temporal).

## Risks / Trade-offs

- [PDF/PPTX/HTML quedan desactualizados tras el rename] → El usuario debe regenerarlos con `marp presentacion.md`. No se generan en este cambio.
- [Contenido muy extenso para presentación oral] → Limitar a ~20-25 diapositivas. El usuario puede ajustar después.
- [Pérdida de referencias desde otros documentos] → Verificado: no hay referencias externas a los nombres antiguos.
