# Design

## Context

El sistema tiene una infraestructura de contenedores Docker que incluye PostgreSQL con pgvector (puerto 5434), Apache Airflow, Apache Superset, MLflow y un servidor MCP. El código de desarrollo está en `Desarrollo/` con módulos separados para embeddings, chatbot, MCP y utilidades compartidas. La configuración se carga desde variables de entorno usando dotenv.

El pipeline de embeddings ya está implementado pero no probado. El chatbot RAG está implementado pero necesita configuración y verificación de dependencias. La base de datos PostgreSQL necesita la extensión pgvector habilitada y la tabla de embeddings creada.

## Goals / Non-Goals

**Goals:**
- Hacer funcional el pipeline completo de RAG (embeddings → búsqueda → LLM → SQL → resultados)
- Asegurar que todos los componentes estén correctamente configurados y conectados
- Proporcionar documentación clara para levantar el sistema

**Non-Goals:**
- Modificar la arquitectura existente del sistema
- Cambiar el modelo de LLM (DeepSeek)
- Implementar nuevos componentes más allá del RAG existente
- Modificar la infraestructura Docker existente

## Decisions

### 1. Configuración del entorno
**Decisión**: Crear archivo `.env` en `Desarrollo/` con todas las variables necesarias.
**Razón**: El código ya usa `dotenv` para cargar configuración desde `.env`. Centralizar la configuración evita errores de conexión.
**Alternativas consideradas**: 
- Variables de entorno del sistema (rechazado: menos portable)
- Archivo de configuración JSON (rechazado: no es el patrón existente)

### 2. Inicialización de pgvector
**Decisión**: Ejecutar migración SQL para crear la extensión y tabla de embeddings.
**Razón**: La tabla `embeddings.embeddings` necesita existir antes de generar embeddings. La migración ya está en `migrate_pgvector.sql`.
**Alternativas consideradas**:
- Crear tabla manualmente (rechazado: no reproducible)
- Usar ORM para crear tablas (rechazado: no es el patrón existente)

### 3. Generación de embeddings
**Decisión**: Ejecutar el pipeline existente `run_embedding_pipeline(rebuild=True)`.
**Razón**: El pipeline ya implementa la lógica completa: extraer esquema, generar documentos, crear embeddings y almacenar en PostgreSQL.
**Alternativas consideradas**:
- Implementar nuevo pipeline (rechazado: duplicación innecesaria)

### 4. Verificación de dependencias
**Decisión**: Crear script de verificación que compruebe todas las dependencias antes de iniciar.
**Razón**: El sistema tiene múltiples dependencias (sentence-transformers, openai, psycopg2, etc.) que pueden faltar.
**Alternativas consideradas**:
- Documentar dependencias manualmente (rechazado: propenso a errores)
- Usar requirements.txt (ya existe pero puede estar incompleto)

### 5. Orden de inicio de servicios
**Decisión**: Definir secuencia clara: PostgreSQL → embeddings → MCP → chatbot.
**Razón**: Cada servicio depende del anterior. El chatbot necesita embeddings generados y MCP corriendo.
**Alternativas consideradas**:
- Iniciar todos los servicios en paralelo (rechazado: puede causar errores de conexión)

## Risks / Trade-offs

### Riesgo 1: Conexión a PostgreSQL fallida
**Mitigación**: Verificar que el contenedor Docker de PostgreSQL esté corriendo antes de intentar conectar. Agregar reintentos con backoff exponencial.

### Riesgo 2: API key de DeepSeek inválida
**Mitigación**: Validar la API key al inicio y mostrar mensaje claro si es inválida.

### Riesgo 3: Modelo de embeddings no descargado
**Mitigación**: sentence-transformers descarga automáticamente el modelo, pero puede tomar tiempo en la primera ejecución. Mostrar progreso.

### Riesgo 4: Tabla de embeddings no existe
**Mitigación**: La función `ensure_table()` en `store.py` ya maneja la creación automática de la tabla y el índice.

### Riesgo 5: Puerto 8000/8001 en uso
**Mitigación**: Verificar puertos disponibles antes de iniciar servidores y mostrar mensaje claro si están ocupados.

## Migration Plan

1. **Pre-requisitos**:
   - Contenedor Docker de PostgreSQL corriendo (`docker compose up -d` en `Contenedores/ts_train/`)
   - Variables de entorno configuradas en `Desarrollo/.env`

2. **Secuencia de inicio**:
   ```bash
   # 1. Verificar PostgreSQL
   docker compose -f Contenedores/ts_train/docker-compose.yml ps
   
   # 2. Crear .env con configuración
   cp Desarrollo/.env.example Desarrollo/.env  # o crear manualmente
   
   # 3. Ejecutar migración de pgvector
   python -c "from src.ts_embeddings.store import ensure_table; ensure_table()"
   
   # 4. Generar embeddings
   python -m src.ts_embeddings.pipeline
   
   # 5. Levantar servidores
   python run_servers.py
   ```

3. **Rollback**:
   - Si falla la generación de embeddings, ejecutar con `rebuild=True` para limpiar y regenerar
   - Si falla la conexión a PostgreSQL, reiniciar el contenedor Docker

## Open Questions

- ¿La API key de DeepSeek ya está configurada en el entorno del usuario?
- ¿El contenedor de PostgreSQL está actualmente corriendo?
- ¿Hay datos en la base de datos para generar embeddings o necesitamos cargar datos de ejemplo primero?