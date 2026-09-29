# Spec Delta

## Purpose

El sistema RAG permite a los usuarios hacer preguntas en lenguaje natural sobre la base de datos de créditos y obtener respuestas precisas con SQL generado automáticamente, resultados ejecutados y explicaciones claras.

## ADDED Requirements

### Requirement: Generación de embeddings
El sistema SHALL generar embeddings vectoriales de los documentos de la base de datos (esquemas, datos de muestra, ejemplos few-shot) y almacenarlos en PostgreSQL con pgvector.

#### Scenario: Generación exitosa de embeddings
- **WHEN** se ejecuta el pipeline de embeddings
- **THEN** el sistema genera embeddings para todos los documentos y los almacena en la tabla embeddings.embeddings

#### Scenario: Reconstrucción de embeddings
- **WHEN** se ejecuta el pipeline con rebuild=True
- **THEN** el sistema elimina los embeddings existentes y los regenera desde cero

### Requirement: Búsqueda semántica de documentos
El sistema SHALL recuperar los documentos más relevantes para una consulta del usuario usando búsqueda por similitud de coseno en los embeddings.

#### Scenario: Búsqueda con resultados
- **WHEN** un usuario hace una pregunta y existen embeddings en la base de datos
- **THEN** el sistema retorna los N documentos más similares con su contenido y metadata

#### Scenario: Búsqueda sin resultados
- **WHEN** un usuario hace una pregunta y no existen embeddings en la base de datos
- **THEN** el sistema retorna una lista vacía y continúa con la generación de respuesta

### Requirement: Generación de respuestas con LLM
El sistema SHALL generar respuestas en lenguaje natural usando DeepSeek, incorporando el contexto recuperado por RAG.

#### Scenario: Respuesta con contexto
- **WHEN** se recupera contexto relevante de los embeddings
- **THEN** el LLM genera una respuesta que incluye SQL válido y explicación clara

#### Scenario: Respuesta sin contexto
- **WHEN** no se recupera contexto relevante
- **THEN** el LLM genera una respuesta indicando que no tiene suficiente información

### Requirement: Generación y validación de SQL
El sistema SHALL generar consultas SQL basadas en las preguntas del usuario y validarlas antes de ejecutarlas.

#### Scenario: SQL válido generado
- **WHEN** el LLM genera una consulta SQL válida
- **THEN** el sistema valida que sea solo lectura (SELECT) y la ejecuta

#### Scenario: SQL inválido rechazado
- **WHEN** el LLM genera SQL con operaciones de escritura (INSERT, UPDATE, DELETE)
- **THEN** el sistema rechaza la ejecución y muestra un mensaje de error

### Requirement: Ejecución de consultas SQL
El sistema SHALL ejecutar las consultas SQL válidas y retornar los resultados formateados.

#### Scenario: Ejecución exitosa
- **WHEN** se ejecuta una consulta SQL válida
- **THEN** el sistema retorna columnas, filas y conteo de resultados

#### Scenario: Error en ejecución
- **WHEN** la consulta SQL falla por error de sintaxis o permisos
- **THEN** el sistema retorna un mensaje de error descriptivo

### Requirement: Presentación de resultados
El sistema SHALL presentar los resultados de las consultas de forma clara y legible.

#### Scenario: Resultados con formato
- **WHEN** se obtienen resultados de una consulta
- **THEN** el sistema genera una respuesta final que presenta los datos en formato markdown con tabla

#### Scenario: Resultados vacíos
- **WHEN** la consulta retorna 0 filas
- **THEN** el sistema indica que no se encontraron resultados para la consulta

### Requirement: Interfaz de chat REST
El sistema SHALL exponer un endpoint REST POST /chat para recibir preguntas y retornar respuestas.

#### Scenario: Request válido
- **WHEN** se envía un POST a /chat con question y execute_sql
- **THEN** el sistema retorna response, sql, query_results y context_docs

#### Scenario: Health check
- **WHEN** se envía un GET a /health
- **THEN** el sistema retorna {"status": "ok", "service": "chatbot-rag"}

### Requirement: CLI de interacción
El sistema SHALL proporcionar una CLI para interactuar con el chatbot desde la terminal.

#### Scenario: Inicio de sesión
- **WHEN** el usuario ejecuta chat_cli.py
- **THEN** el sistema muestra el prompt "Tu pregunta:" y espera input

#### Scenario: Salida de sesión
- **WHEN** el usuario escribe "salir", "exit" o "quit"
- **THEN** el sistema termina la sesión con "Hasta luego!"