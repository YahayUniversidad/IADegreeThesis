# Design

## Context

El sistema tiene una infraestructura de contenedores Docker ya definida pero no ejecutándose de forma coordinada. Los componentes son:

**Contenedor principal (fuente de datos):**
- `ts_train`: PostgreSQL con pgvector (puerto 5434) - Base de datos principal del sistema
  - Ejecuta `initPostgres/init.sh` al iniciar para crear extensiones y esquemas
  - Esquemas creados: `datamart`, `embeddings`, `airflow`, `superset`
  - Extensión pgvector habilitada para embeddings
  - **Este contenedor es la fuente de verdad para todos los datos**

**Contenedores dependientes:**
- `ts_airflow`: Orquestador de pipelines (puerto 8080) - Conecta a ts_train
- `ts_superset`: Visualización de datos (puerto 8088) - Conecta a ts_train

**Contenedor independiente (NO MODIFICAR):**
- `ts_mlflow`: Tracking de experimentos (puerto 5000) - Base de datos propia del proveedor
  - Tiene su propio contenedor de base de datos sugerido por el proveedor
  - **NO se debe modificar ni conectar a ts_train**

**Servidor MCP local (NO es Docker):**
- `src/ts_mcp/`: Servidor MCP Python (puerto 8000) - **Este es el que usa el RAG**
  - Se ejecuta localmente con `python run_servers.py`
  - Proporciona herramientas: get_schema, query_sql, get_datamart_info, get_sample_data, query_datamart
  - El chatbot RAG importa directamente: `from src.ts_mcp.tools import query_sql`

**Contenedor OPCIONAL (NO parte del flujo principal):**
- `ts_mcp`: Servidores MCP Docker (puertos 5009, 5011) - Para acceso externo vía protocolo MCP
  - NO es necesario para el sistema RAG
  - NO está funcionando actualmente
  - OPCIONAL: se puede desplegar después si se necesita acceso MCP externo

Cada componente tiene su propio docker-compose.yml y scripts de gestión. El script `ejectuarAll.sh` intenta levantar todos los servicios pero no verifica dependencias ni maneja errores correctamente.

## Goals / Non-Goals

**Goals:**
- Levantar los contenedores Docker core (ts_train, ts_airflow, ts_superset, ts_mlflow) en el orden correcto
- Verificar que cada servicio esté saludable antes de continuar
- Cargar datos históricos en PostgreSQL
- Construir el datamart con el esquema estrella
- Configurar Superset para visualizar el datamart
- Preparar la infraestructura para el sistema RAG

**Non-Goals:**
- Modificar la arquitectura existente de los contenedores
- Cambiar el esquema de la base de datos
- Implementar nuevos modelos de ML
- Modificar los DAGs de Airflow existentes
- Desplegar ts_mcp Docker (opcional, no requerido para RAG)

## Decisions

### 1. Orden de despliegue
**Decisión**: ts_train (PostgreSQL) → ts_airflow → ts_superset → ts_mlflow
**Razón**: 
- ts_train DEBE ser el primero porque es la fuente de datos y ejecuta init.sh para crear esquemas
- ts_airflow y ts_superset dependen de ts_train para conectarse a la base de datos
- ts_mlflow es INDEPENDIENTE y tiene su propia base de datos del proveedor, se levanta al final sin modificar
- ts_mcp Docker es OPCIONAL y NO parte del flujo principal (el RAG usa MCP Python local)
**Alternativas consideradas**:
- Despliegue paralelo (rechazado: puede causar errores de conexión)
- Despliegue manual (rechazado: propenso a errores)
- Incluir ts_mcp en el flujo principal (rechazado: no es necesario para el RAG)

### 2. Independencia de ts_mlflow
**Decisión**: ts_mlflow se levanta independientemente y NO se modifica su base de datos
**Razón**: ts_mlflow usa un contenedor de base de datos sugerido por el proveedor del producto. Modificarlo podría romper la integración soportada.
**Alternativas consideradas**:
- Conectar ts_mlflow a ts_train (rechazado: no es la arquitectura soportada por el proveedor)
- Compartir base de datos (rechazado: viola el aislamiento recomendado)

### 3. Verificación de salud
**Decisión**: Usar scripts de verificación con timeout de 5 minutos por servicio.
**Razón**: Los servicios pueden tardar en iniciar, especialmente Airflow que necesita inicializar la BD. 5 minutos es un límite razonable.
**Alternativas consideradas**:
- Verificación sin timeout (rechazado: puede colgar indefinidamente)
- Verificación con timeout más corto (rechazado: puede fallar en servicios lentos)

### 4. Carga de datos
**Decisión**: Ejecutar el DAG de entrenamiento de Airflow para cargar datos históricos.
**Razón**: El DAG ya implementa todo el flujo: crear estructura → cargar CSV → datamart → EDA → entrenar modelos.
**Alternativas consideradas**:
- Carga manual de datos (rechazado: no reproducible)
- Script separado de carga (rechazado: duplicación innecesaria)

### 5. Configuración de Superset
**Decisión**: Configurar la conexión a PostgreSQL desde la interfaz de Superset.
**Razón**: Superset tiene una interfaz web para configurar conexiones a bases de datos. Es más flexible que configuración manual.
**Alternativas consideradas**:
- Configuración via API (rechazado: más complejo)
- Configuración via archivo (rechazado: menos flexible)

### 6. Variables de entorno
**Decisión**: Usar archivos .env existentes con validación de credenciales.
**Razón**: Los archivos .env ya existen para cada servicio. Solo necesitamos verificar que las credenciales sean correctas.
**Alternativas consideradas**:
- Variables de entorno del sistema (rechazado: menos portable)
- Archivo de configuración centralizado (rechazado: no es el patrón existente)

### 7. Asignación de recursos Docker
**Decisión**: Configurar límites de memoria para cada contenedor core totalizando ~19GB de los 32GB disponibles.
**Razón**: El sistema ejecuta múltiples servicios pesados (PostgreSQL con pgvector, Airflow con pipelines ML, Superset). Sin límites, un contenedor puede consumir toda la memoria y afectar a los demás.
**Distribución propuesta (servicios core):**
- `ts_train` (PostgreSQL + pgvector): **6GB** - Base de datos principal, necesita memoria para queries y embeddings
- `ts_airflow` (Airflow + workers): **6GB** - Ejecuta pipelines ML, necesita memoria para procesamiento
- `ts_superset` (Superset): **4GB** - Motor de visualización y consultas
- `ts_mlflow` (MLflow): **3GB** - Tracking de experimentos (configuración del proveedor)
- **Total core: 19GB** (deja ~13GB para OS, MCP Python local y otros procesos)

**Servicio opcional (no incluido en límites core):**
- `ts_mcp` (MCP servers Docker): **2GB** - OPCIONAL, solo si se despliega para acceso externo

**Alternativas consideradas**:
- Sin límites de memoria (rechazado: riesgo de OOM kill)
- Límites más bajos (rechazado: puede causar rendimiento degradado en pipelines ML)
- Límites más altos (rechazado: puede afectar al sistema operativo)
- Incluir ts_mcp en límites core (rechazado: ts_mcp es opcional)

## Risks / Trade-offs

### Riesgo 1: Puertos ya en uso
**Mitigación**: Verificar puports disponibles antes de iniciar servicios. Mostrar mensaje claro si un puerto está ocupado.

### Riesgo 2: Credenciales incorrectas
**Mitigación**: Validar credenciales al inicio y mostrar mensaje claro si son incorrectas.

### Riesgo 3: Datos CSV no disponibles
**Mitigación**: Verificar que los archivos CSV existan en la ruta esperada antes de ejecutar el DAG.

### Riesgo 4: Contenedores Docker no instalados
**Mitigación**: Verificar que Docker y Docker Compose estén instalados antes de intentar desplegar.

### Riesgo 5: Espacio en disco insuficiente
**Mitigación**: Verificar espacio disponible antes de iniciar el despliegue.

## Migration Plan

1. **Pre-requisitos**:
   - Docker y Docker Compose instalados
   - Archivos CSV históricos disponibles
   - Archivos .env configurados para cada servicio

2. **Secuencia de despliegue (orden crítico)**:
   ```bash
   # 1. Verificar Docker
   docker --version && docker compose --version
   
   # 2. Verificar puertos disponibles
   netstat -tuln | grep -E ':(5434|8080|8088|5000)\s'
   
   # 3. PRIMERO: Desplegar ts_train (fuente de datos)
   cd Contenedores/ts_train
   ./ejecutar.sh
   # Esperar a que init.sh cree los esquemas: datamart, embeddings, airflow, superset
   
   # 4. SEGUNDO: Desplegar ts_airflow (depende de ts_train)
   cd ../ts_airflow
   ./ejecutar.sh
   
   # 5. TERCERO: Desplegar ts_superset (depende de ts_train)
   cd ../ts_superset
   ./ejecutar.sh
   
   # 6. CUARTO: Desplegar ts_mlflow (INDEPENDIENTE, no modificar)
   cd ../ts_mlflow
   ./ejecutar.sh
   
   # 7. Verificar servicios core
   pg_isready -h localhost -p 5434  # PostgreSQL
   curl -s http://localhost:8080/health  # Airflow
   curl -s http://localhost:8088  # Superset
   curl -s http://localhost:5000  # MLflow
   
   # 8. Ejecutar DAG de entrenamiento (carga datos en ts_train)
   # (desde la interfaz de Airflow o CLI)
   
   # 9. Configurar Superset (conectar a ts_train)
   # (desde la interfaz web de Superset)
   
   # OPCIONAL: ts_mcp Docker (solo si se necesita acceso MCP externo)
   # cd ../ts_mcp
   # ./ejecutar.sh
   ```

3. **Rollback**:
   - Si falla algún servicio, detener todos los contenedores con `./script/pararAll.sh`
   - Verificar logs de Docker para identificar el problema
   - Corregir el problema y reintentar el despliegue
   - **NOTA**: ts_mlflow tiene su propio proceso de rollback independiente

## Open Questions

- ¿Los archivos CSV históricos están disponibles en la ruta esperada?
- ¿Las credenciales en los archivos .env son correctas?
- ¿Hay espacio suficiente en disco para los contenedores y datos?
- ¿La red permite conexiones entre contenedores?