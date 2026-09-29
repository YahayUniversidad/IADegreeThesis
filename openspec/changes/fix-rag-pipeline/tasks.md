# Tasks

## 1. Configuración del entorno

- [ ] 1.1 Crear archivo `Desarrollo/.env` con variables de entorno (DATABASE_URL, DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL, MCP_HOST, MCP_PORT, EMBEDDING_MODEL, EMBEDDING_DIM) y verificar que se carga correctamente con `python -c "from src.ts_config import DATABASE_URL; print(DATABASE_URL)"`
- [ ] 1.2 Verificar que el contenedor Docker de PostgreSQL está corriendo con `docker compose -f Contenedores/ts_train/docker-compose.yml ps` y confirmar que el puerto 5434 está accesible
- [ ] 1.3 Instalar dependencias Python faltantes ejecutando `pip install -r requirements.txt` (o instalar manualmente: psycopg2-binary, sentence-transformers, openai, fastapi, uvicorn, python-dotenv) y verificar importaciones con `python -c "import psycopg2; import sentence_transformers; import openai; print('OK')"`

## 2. Inicialización de la base de datos

- [ ] 2.1 Ejecutar migración de pgvector para crear la extensión y tabla de embeddings con `python -c "from src.ts_embeddings.store import ensure_table; ensure_table()"` y verificar que la tabla existe con una consulta SQL
- [ ] 2.2 Verificar que la extensión pgvector está habilitada en PostgreSQL con `psql -h localhost -p 5434 -U postgres_usr -d postgres_db -c "SELECT * FROM pg_extension WHERE extname = 'vector'"`

## 3. Generación de embeddings

- [ ] 3.1 Ejecutar el pipeline de embeddings con `python -m src.ts_embeddings.pipeline` y verificar que se generan documentos (esquemas, muestras, few-shot)
- [ ] 3.2 Verificar que los embeddings se almacenaron correctamente consultando el conteo con `python -c "from src.ts_embeddings.store import collection_count; print(collection_count())"`
- [ ] 3.3 Probar la búsqueda semántica ejecutando `python -c "from src.ts_embeddings.store import query_documents; docs = query_documents('creditos', n_results=3); print(len(docs), 'documentos encontrados')"` y verificar que retorna resultados

## 4. Verificación del chatbot

- [ ] 4.1 Verificar que la API key de DeepSeek es válida ejecutando una prueba de conexión simple con `python -c "from src.ts_chatbot.llm import chat; response = chat([{'role': 'user', 'content': 'Hola'}]); print(response)"`
- [ ] 4.2 Probar el endpoint de salud del chatbot levantando el servidor temporalmente con `python -m uvicorn src.ts_chatbot.app:app --host 127.0.0.1 --port 8001` y verificando GET /health retorna `{"status": "ok", "service": "chatbot-rag"}`
- [ ] 4.3 Probar el endpoint POST /chat con una pregunta simple como "¿Cuantos creditos hay?" y verificar que retorna response, sql, query_results y context_docs

## 5. Integración del sistema completo

- [ ] 5.1 Levantar todos los servidores con `python run_servers.py` y verificar que tanto MCP (puerto 8000) como chatbot (puerto 8001) están corriendo
- [ ] 5.2 Probar la CLI del chatbot ejecutando `python chat_cli.py`, haciendo una pregunta y verificando que retorna una respuesta con SQL y resultados
- [ ] 5.3 Verificar el flujo completo RAG: pregunta → embeddings → LLM → SQL → resultados → respuesta final

## 6. Documentación y limpieza

- [ ] 6.1 Actualizar README.md con instrucciones claras de cómo levantar el sistema (pre-requisitos, configuración, inicio de servicios)
- [ ] 6.2 Crear script de inicio rápido `start.sh` que verifique dependencias, inicialice la base de datos y levante los servidores
- [ ] 6.3 Verificar que no hay errores en los logs de los servidores y que el sistema funciona de extremo a extremo