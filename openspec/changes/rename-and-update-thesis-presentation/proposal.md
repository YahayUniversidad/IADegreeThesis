# Proposal

## Why

La presentación `tesis/presentacionAnteProyecto/` corresponde al anteproyecto (julio 2026) y ya no refleja el estado final de la tesis. El título, los modelos, los dashboards y el alcance cambiaron durante el desarrollo. Además, el nombre del folder y del archivo (`presentacion_anteproyecto`) no corresponde a una presentación final.

## What Changes

- Renombrar folder `tesis/presentacionAnteProyecto/` → `tesis/presentacion/`
- Renombrar archivos `presentacion_anteproyecto.*` → `presentacion.*` (md, css, html, pdf, pptx)
- Actualizar referencias internas a los nombres de archivo (CSS, HTML, links)
- Actualizar el contenido de la presentación para que corresponda a la tesis final:
  - Título oficial: "Sistema Integrado de Inteligencia de Negocio para la Predicción de Crisis Crediticias"
  - Modelos: CNN + MLP + LightGBM (no solo CNN + LightGBM)
  - Dashboards: 5 (3 históricos + 2 de predicción por horizonte)
  - Estado: sistema completado, no "en desarrollo"
- Reorganizar las diapositivas para empatar con la estructura de capítulos de la tesis:
  1. Introducción (contexto, problema, objetivos)
  2. Marco teórico (conceptos clave)
  3. Estado del arte (brechas)
  4. Metodología (arquitectura, datos, modelos)
  5. Resultados (comparación, dashboards)
  6. Conclusiones (contribuciones, trabajo futuro)

## Capabilities

### New Capabilities

_(ninguna)_

### Modified Capabilities

_(ninguna — cambio de contenido documental, sin cambios de requisitos)_

## Impact

- `tesis/presentacionAnteProyecto/` → `tesis/presentacion/` (rename)
- 5 archivos renombrados (`presentacion_anteproyecto.*` → `presentacion.*`)
- Contenido de `presentacion.md` reescrito para alinearse con `tesis/final/chapters/`
- Sin cambios en código, servicios ni specs
