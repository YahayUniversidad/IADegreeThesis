# Proposal

## Why

El sistema RAG (Retrieval-Augmented Generation) del chatbot no está funcionando correctamente. Se ha implementado la infraestructura de embeddings con pgvector, el pipeline de documentos, y el chatbot con DeepSeek, pero el flujo completo no ha sido probado ni integrado exitosamente. El proyecto necesita ser relanzado con todas las funcionalidades operativas, especialmente el RAG que es el componente central de interacción con el usuario.

## What Changes

- **Configuración del entorno**: Crear archivo `.env` con las variables de configuración necesarias (DATABASE_URL, DEEPSEEK_API_KEY, etc.)
- **Verificación de dependencias**: Asegurar que todas las dependencias Python estén instaladas correctamente
- **Inicialización de la base de datos**: Ejecutar la migración de pgvector y crear las tablas necesarias para embeddings
- **Generación de embeddings**: Ejecutar el pipeline de embeddings para poblar la base de datos con los documentos
- **Integración del chatbot**: Asegurar que el chatbot RAG pueda conectarse a la base de datos y al LLM
- **Documentación de inicio**: Actualizar documentación con instrucciones claras de cómo levantar el sistema

## Capabilities

### New Capabilities
- `rag-pipeline`: Pipeline completo de RAG que incluye generación de embeddings, almacenamiento en pgvector, y chatbot con DeepSeek para consultas en lenguaje natural

### Modified Capabilities
(No existing capabilities to modify)

## Impact

- **Código afectado**: 
  - `Desarrollo/src/ts_embeddings/` - Pipeline de embeddings
  - `Desarrollo/src/ts_chatbot/` - Chatbot RAG
  - `Desarrollo/src/ts_mcp/` - Servidor MCP
  - `Desarrollo/run_servers.py` - Script de inicio
  - `Desarrollo/chat_cli.py` - CLI del chatbot

- **Dependencias**:
  - PostgreSQL con pgvector (contenedor Docker)
  - sentence-transformers para embeddings
  - openai para conexión con DeepSeek
  - psycopg2 para conexión a PostgreSQL
  - FastAPI y uvicorn para servidores

- **Sistemas afectados**:
  - Base de datos PostgreSQL (esquema embeddings)
  - Servidor MCP (puerto 8000)
  - Chatbot RAG (puerto 8001)