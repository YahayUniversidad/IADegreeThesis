# mcp-servers Specification

## Purpose

Proporcionar servidores MCP (Model Context Protocol) opcionales para acceso externo a PostgreSQL y Superset vía HTTP. Esta capacidad es OPCIONAL y no afecta el funcionamiento del sistema RAG principal.

## Requirements

### Requirement: MCP Server para PostgreSQL (Opcional)
El sistema SHALL poder exponer un servidor MCP para PostgreSQL en el puerto 5009, permitiendo consultas externas vía protocolo MCP.

#### Scenario: Servidor MCP PostgreSQL activo
- **WHEN** se despliega el contenedor ts_mcp con el servicio postgres_mcp
- **THEN** el servidor MCP está disponible en `http://localhost:5009/mcp` y acepta consultas

#### Scenario: Servidor MCP PostgreSQL no desplegado
- **WHEN** no se despliega ts_mcp
- **THEN** el sistema RAG funciona correctamente usando el MCP Python local (puerto 8000)

### Requirement: MCP Server para Superset (Opcional)
El sistema SHALL poder exponer un servidor MCP para Superset en el puerto 5011, permitiendo consultas externas vía protocolo MCP.

#### Scenario: Servidor MCP Superset activo
- **WHEN** se despliega el contenedor ts_mcp con el servicio superset_mcp
- **THEN** el servidor MCP está disponible en `http://localhost:5011/mcp` y acepta consultas

#### Scenario: Servidor MCP Superset no desplegado
- **WHEN** no se despliega ts_mcp
- **THEN** el sistema funciona correctamente sin acceso MCP externo a Superset

### Requirement: Independencia del sistema RAG
El sistema RAG SHALL funcionar correctamente sin necesidad de ts_mcp Docker, usando el servidor MCP Python local.

#### Scenario: RAG sin ts_mcp Docker
- **WHEN** ts_mcp Docker no está desplegado
- **THEN** el chatbot RAG puede conectarse al MCP Python local en puerto 8000 y ejecutar consultas

#### Scenario: RAG con ts_mcp Docker
- **WHEN** ts_mcp Docker está desplegado
- **THEN** el chatbot RAG sigue usando el MCP Python local (no cambia su comportamiento)
