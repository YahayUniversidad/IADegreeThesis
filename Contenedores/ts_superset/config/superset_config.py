##
## Configuracion para Superset
## Habilita la configuracion de Superset para que funcione con el MCP.
##
import os
 
# Base de datos para Superset
SQLALCHEMY_DATABASE_URI = os.environ.get("SUPERSET__SQLALCHEMY_DATABASE_URI")
SECRET_KEY = os.environ.get("SUPERSET_SECRET_KEY", "your_secret_key_here")
 
# MCP server en modo desarrollo.
MCP_SERVICE_HOST = "0.0.0.0"
MCP_SERVICE_PORT = 5008
 
MCP_AUTH_ENABLED = False
MCP_DEV_USERNAME = os.environ.get("MCP_DEV_USERNAME", "admin")
 
# Opcional: modo debug para validar mcp, por ejemplo.
MCP_DEBUG = True