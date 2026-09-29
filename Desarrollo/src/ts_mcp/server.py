"""MCP Server: FastAPI que expone herramientas de consulta a la BD y datamart."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from . import tools

app = FastAPI(
    title="MCP Server - Tesis Datamart",
    description="Herramientas MCP para consultar la base de datos y datamart de creditos",
    version="0.1.0",
)


class QueryRequest(BaseModel):
    sql: str
    limit: int = 100


class SampleRequest(BaseModel):
    table: str
    n: int = 5


class DatamartQueryRequest(BaseModel):
    query_type: str
    params: dict | None = None


class SchemaRequest(BaseModel):
    tables: list[str] | None = None


# --- Endpoints MCP (estilo JSON-RPC simplificado) ---

@app.get("/mcp/info")
def mcp_info():
    """Informacion del servidor MCP y herramientas disponibles."""
    return {
        "name": "mcp-tesis-datamart",
        "version": "0.1.0",
        "tools": [
            {"name": "get_schema", "description": "Obtiene el esquema de tablas (columnas, tipos, comentarios)"},
            {"name": "query_sql", "description": "Ejecuta una consulta SQL de solo lectura"},
            {"name": "get_datamart_info", "description": "Devuelve info del datamart (dimensiones, hechos, conteos)"},
            {"name": "get_sample_data", "description": "Muestra N filas de una tabla"},
            {"name": "query_datamart", "description": "Consultas predefinidas al datamart"},
        ],
    }


@app.post("/mcp/tools/get_schema")
def mcp_get_schema(req: SchemaRequest | None = None):
    """Devuelve el esquema de las tablas de la BD y datamart."""
    tables = req.tables if req else None
    return tools.get_schema(tables)


@app.post("/mcp/tools/query_sql")
def mcp_query_sql(req: QueryRequest):
    """Ejecuta SQL de solo lectura contra la base de datos."""
    return tools.query_sql(req.sql, req.limit)


@app.get("/mcp/tools/get_datamart_info")
def mcp_get_datamart_info():
    """Devuelve informacion del datamart."""
    return tools.get_datamart_info()


@app.post("/mcp/tools/get_sample_data")
def mcp_get_sample_data(req: SampleRequest):
    """Devuelve filas de muestra de una tabla."""
    return tools.get_sample_data(req.table, req.n)


@app.post("/mcp/tools/query_datamart")
def mcp_query_datamart(req: DatamartQueryRequest):
    """Ejecuta una consulta predefinida al datamart."""
    return tools.query_datamart(req.query_type, req.params)


# --- Endpoints de conveniencia ---

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tables")
def list_tables():
    """Lista todas las tablas publicas."""
    return {
        "operativas": list(tools._TABLES_OPS),
        "datamart": list(tools._TABLES_DM),
    }


if __name__ == "__main__":
    import uvicorn
    from src.ts_config import MCP_HOST, MCP_PORT

    uvicorn.run(app, host=MCP_HOST, port=MCP_PORT)
