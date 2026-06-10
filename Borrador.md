## Capítulo 1: Introducción

### 1.1 "Background" y contexto

Las instituciones financieras, en especial las pertenecientes al sector de la economía social y solidaria, manejan grandes volúmenes de datos crediticios que, correctamente analizados, pueden revelar patrones predictivos sobre el comportamiento de pago de sus socios y clientes. Tradicionalmente, el análisis de cartera se realiza mediante indicadores retrospectivos —tasa de morosidad, índice de castigos, relación cartera vencida / cartera total— que informan sobre lo que ya ocurrió, pero no ofrecen capacidad de anticipación.

En los últimos anios, la armonizacion de tres tecnologías ha abierto una nueva frontera:

1. **Aprendizaje profundo (Deep Learning)**: Los modelos CNN (Redes Neuronales Convolucionales) han demostrado capacidad para extraer patrones temporales en series financieras, superando a métodos estadísticos clásicos como ARIMA o regresión logística en tareas de clasificación del riesgo.

2. **Arquitecturas de datos modernas**: Los datawarehouses y los datamarts analíticos permiten consolidar datos operativos y predicciones en un solo repositorio optimizado para consultas de negocio, eliminando la fricción entre los equipos de datos y los usuarios de negocio.

3. **Asistentes de IA conversacionales**: La irrupción de Modelos de Lenguaje de Gran Escala (LLMs) como GPT-4, Claude y Llama, junto con protocolos de integración como el Model Context Protocol (MCP), permite que los usuarios interactúen con sus datos en lenguaje natural, sin necesidad de conocimientos técnicos.

La integración de estas tres tecnologías son los pilares de la presente trabajo.

### 1.2 La Motivación

La motivación de este trabajo surge de la experiencia práctica en el área de desarrollo y el análisis de datos en una institución financiera ecuatoriana; y, el cursar la maestría en inteligencia artificial nos ha permitido identificar las siguientes problemáticas recurrentes:

- Los reportes de cartera se generan de forma manual, consumiendo días de trabajo cada mes.
- Los modelos predictivos existentes tienen alta exactitud (accuracy > 93%) pero precisión y recall en cero, lo que indica que no detectan crisis reales (problema de clases desbalanceadas).
- No existe un datamart unificado que permita a los analistas cruzar datos históricos con predicciones del modelo.
- Los dashboards son estáticos y requieren intervención de personal técnico para su actualización.
- Los dashboards estan limitados a usuarios con un nivel alto de permisos, lo que restringe su acceso a un grupo reducido de analistas, lo que limita la democratización de la información en la institución que tiene politica de puertas abiertas a los usuarios.
- No se tiene una herramienta predictiva para mejorar la colocación de capitales en prestamos, lo que podría reducir la tasa de morosidad y mejorar los rendimientos de la cartera.
- No hay un canal de consulta en lenguaje natural accesible para los usuarios de negocio.

"En temas de datos, la falta de acceso es tan útil como no tenerla" 

### 1.3 Planteamiento del problema

Las instituciones financieras que son parte de la economia social y solidaria, generan diariamente millones de registros transaccionales. Sin embargo, el valor de estos datos se difumina cuando:

1. **Los modelos predictivos no se integran con los sistemas de reporte**: El modelo CNN multi-horizonte desarrollado produce predicciones a 1, 3, 6, 12 y 18 meses, pero estas no están disponibles en un datamart accesible para los analistas de negocio.

2. **Los dashboards no son dinámicos ni auto-gestionados**: La creación y actualización de dashboards requiere intervención manual de personal técnico, creando cuellos de botella.

3. **No existe un canal conversacional para consultar los datos**: Los usuarios de negocio deben depender del equipo de datos para responder preguntas que podrían resolverse con lenguaje natural, requiere de interpretación técnica.

4. **El monitoreo del modelo no está integrado con las alertas de negocio**: No hay un mecanismo que notifique automáticamente cuando las predicciones superan umbrales críticos o que indiquen un riesgo crediticio.

**Pregunta de investigación**: ¿Cómo integrar un modelo CNN de predicción de crisis crediticia multi-horizonte con un datamart analítico, dashboards potenciados por IA (Apache Superset MCP) y un agente conversacional LLM, para proporcionar una plataforma unificada de inteligencia de negocio crediticia para control de la mora?

### 1.4 Objetivo general

Diseñar e implementar un sistema integrado de inteligencia de negocio crediticio para el control de la mora que combine un modelo CNN multi-horizonte para predicción del riesgo crediticio, un datamart analítico unificado, dashboards automatizados vía Apache Superset con capacidades de IA (MCP), y un asistente conversacional basado en LLM para consultas en lenguaje natural sobre el desempeño crediticio y las predicciones del modelo.

### 1.5 Objetivos específicos

1. **Realizar una revisión bibliográfica** sobre el estado del arte en: predicción de riesgo crediticio con deep learning, datamarts analíticos para instituciones financieras, integración de LLMs con plataformas BI mediante MCP, y agentes conversacionales para análisis de datos.

2. **Analizar el modelo CNN multi-horizonte existente**, identificando sus fortalezas (arquitectura y su capacidad predictiva multi-temporal) y debilidades (desbalanceo de clases, precisión/recall en cero); y, proponer mejoras y actualizaciones.

3. **Diseñar e implementar un datamart crediticio** que consolide datos históricos de cartera, predicciones del modelo y métricas de error, en una vista materializada optimizada para consultas analíticas.


//TODO para analizar

**Evaluar el sistema completo** mediante métricas de rendimiento del datamart (tiempos de consulta), usabilidad del agente conversacional (tasa de éxito en respuestas) y calidad predictiva del modelo mejorado (precisión, recall, F1-score, AUC-ROC).

**Configurar Apache Superset con MCP habilitado**, conectarlo al datamart y crear dashboards automatizados mediante interacción en lenguaje natural con asistentes de IA. <- Pendiente ver si a en mis observaciones PREGUNTA al profe

**Desarrollar un agente conversacional LLM** que, mediante el protocolo MCP de Superset, permita a los usuarios realizar consultas en lenguaje natural sobre la cartera crediticia, las predicciones del modelo y la precisión de las mismas. <- Revisar con el profe si es alcanzable en el teimpo.

