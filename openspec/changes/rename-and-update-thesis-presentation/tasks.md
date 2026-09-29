# Tasks

## 1. Renombrar folder y archivos

- [x] 1.1 Renombrar folder `tesis/presentacionAnteProyecto/` → `tesis/presentacion/` con `git mv` — verificar con `ls tesis/presentacion/` que los archivos están presentes
- [x] 1.2 Renombrar `presentacion_anteproyecto.md` → `presentacion.md`, `presentacion_anteproyecto.css` → `presentacion.css`, `presentacion_anteproyecto.html` → `presentacion.html`, `presentacion_anteproyecto.pdf` → `presentacion.pdf`, `presentacion_anteproyecto.pptx` → `presentacion.pptx` — verificar con `ls tesis/presentacion/` que no queda ningún archivo con nombre `presentacion_anteproyecto`
- [x] 1.3 Actualizar referencia a `presentacion_anteproyecto.css` dentro de `presentacion.html` → `presentacion.css` — verificar con `grep -c 'presentacion_anteproyecto' tesis/presentacion/presentacion.html` = 0

## 2. Actualizar contenido de la presentación

- [x] 2.1 Actualizar portada con título oficial "Sistema Integrado de Inteligencia de Negocio para la Predicción de Crisis Crediticias" y fecha Agosto 2026 — verificar que el título aparece en la primera diapositiva
- [x] 2.2 Reorganizar diapositivas en 6 bloques alineados con capítulos de la tesis (Introducción, Marco Teórico, Estado del Arte, Metodología, Resultados, Conclusiones) — verificar que cada bloque tiene un header de sección que identifica el capítulo correspondiente
- [x] 2.3 Actualizar contenido de modelos: incluir MLP junto a CNN y LightGBM, reflejar que LightGBM fue el modelo seleccionado — verificar que las 3 arquitecturas aparecen en la sección de Metodología/Resultados
- [x] 2.4 Actualizar estado de dashboards: 5 dashboards completos (3 históricos + 2 de predicción por horizonte temporal) — verificar que la sección de Resultados menciona los 5 dashboards
- [x] 2.5 Actualizar tabla de estado del proyecto: todo completado, eliminar "En Desarrollo" y "Próximos Pasos" — verificar que no hay secciones de estado pendiente
- [x] 2.6 Agregar sección de Resultados con comparación de modelos (AUC-ROC, Precision, Recall) y métricas multi-horizonte — verificar que la sección incluye al menos una tabla comparativa
- [x] 2.7 Agregar sección de Conclusiones con contribuciones y trabajo futuro alineada con `conclusions.tex` — verificar que las contribuciones de la tesis aparecen en la presentación

## 3. Verificación final

- [x] 3.1 Verificar que no quedan referencias a `presentacion_anteproyecto` ni `presentacionAnteProyecto` en `tesis/presentacion/` — verificar con `grep -r 'anteproyecto\|AnteProyecto' tesis/presentacion/` = 0
- [x] 3.2 Verificar que el Markdown es válido para Marp (frontmatter YAML correcto, separadores `---` entre diapositivas) — verificar con `marp --version` si está disponible, o inspección manual del frontmatter
