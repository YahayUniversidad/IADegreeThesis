##
## @file mcpUso.py
##
## Ejemplo de comunicacion con MCP de Superset y consulta a DeepSeek para analizar su estado.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##
import json
import os
import time
from typing import Any

import requests

MCP_URL = "http://127.0.0.1:5008/mcp"
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

def send_mcp_request(method, params=None, request_id=None):
    """Envio de solicitud a MCP de Superset.
    
    Aca se hace el envio de la solicitud al MCP de Superset, sin enviar el header Authorization.

    Args:
        method (str): Nombre del método MCP a invocar.
        params (dict, optional): Parámetros del método. Defaults to None.
        request_id (int, optional): ID de la solicitud. Defaults to None.

    Returns:
        dict: Respuesta del MCP.
    """
    if request_id is None:
        request_id = int(time.time() * 1000)
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params or {},
        "id": request_id
    }
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream"
    }
    # No se envía Authorization esto es porque el MCP esta arrancado como developer
    response = requests.post(MCP_URL, json=payload, headers=headers, stream=True)
    response.raise_for_status()
    
    if response.headers.get("content-type", "").startswith("text/event-stream"):
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue
            
            if isinstance(line, bytes):
                line = line.decode("utf-8", errors="replace")
            
            if line.startswith("data: "):
                data_json = line[6:]
                if data_json == "[DONE]":
                    break
                try:
                    return json.loads(data_json)
                except json.JSONDecodeError:
                    continue
        return None
    else:
        return response.json()

def initialize_mcp():
    """Inicializa la sesión MCP.

    Se inicializa la sesión MCP enviando la solicitud "initialize" y luego se envía la 
    notificación "notifications/initialized".

    Returns:
        dict: Resultado de la inicialización.
    """
    init_params = {
        "protocolVersion": "2025-06-18",
        "clientInfo": {"name": "python-mcp-client", "version": "1.0.0"},
        "capabilities": {}
    }
    result: Any | None = send_mcp_request("initialize", init_params)
    # El protocolo MCP requiere enviar esta notificación tras el initialize
    send_mcp_request("notifications/initialized")
    return result

def list_tools():
    """Listar las herramientas disponibles en el MCP.

    Returns:
        list: Lista de herramientas disponibles.
    """
    result: Any | None = send_mcp_request("tools/list")
    
    # si no se instanca devuelve un diccionario vacio
    if not isinstance(result, dict):
        return {}

    return result.get("result", {}).get("tools", [])

def call_tool(tool_name, arguments):
    """Llamar a una herramienta específica del MCP.

    Args:
        tool_name (str): Nombre de la herramienta a invocar.
        arguments (dict): Argumentos para la herramienta.


    Returns:
        dict: Resultado de la herramienta.
    """
    params = {"name": tool_name, "arguments": arguments}
    result = send_mcp_request("tools/call", params)
    
    # si no se instanca devuelve un diccionario vacio
    if not isinstance(result, dict):
        return {}
    
    return result.get("result", {})

def ask_deepseek(prompt, context):
    """Consultar a DeepSeek sobre el estado de Superset.

    Args:
        prompt (str): Pregunta del usuario.
        context (str): Contexto del estado de Superset.

    Returns:
        dict: Respuesta de DeepSeek.
    """
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system", 
                "content": "Eres un asistente que analiza el estado de un servidor Superset."},
            {
                "role": "user", 
                "content": f"Contexto: {context}\n\nPregunta: {prompt}"}
        ],
        "temperature": 0.7
    }
    response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    """Función principal que inicializa la sesión MCP, lista las herramientas disponibles.
    
    Luego llama a la herramienta "get_instance_info" para obtener el estado de Superset y 
    finalmente consulta a DeepSeek con una pregunta del usuario sobre el estado obtenido.
    
    """
    
    print("Inicializando sesión MCP...")
    try:
        init_result = initialize_mcp()
        print(f"\nEstado de inicialización: {init_result}")
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return

    print("Listando herramientas...")
    try:
        tools = list_tools()
        print("\nHerramientas disponibles:")
        for t in tools:
            print(f"  - {t.get('name')}: {t.get('description', 'Sin descripción')}")
    except Exception as e:
        print(f"❌ Error listando herramientas: {e}")
        return

    # Por ejecuciones previas se que ya tengo el get_instance_info y obtener el estado de Superset 
    tool_name = "get_instance_info"
    if not any(t.get('name') == tool_name for t in tools):
        if not tools:
            print("❌ No hay herramientas disponibles.")
            return
        tool_name = tools[0].get('name')
        print(f"⚠️  Usando '{tool_name}' en su lugar.")

    print(f"Test a '{tool_name}':")
    try:
        result = call_tool(tool_name, {})
        if result.get("content") and isinstance(result["content"], list):
            state_text = result["content"][0].get("text", str(result))
        else:
            state_text = str(result)
        print("\nEstado de Superset obtenido:")
        # Se pasa a formato JSON, no entendia la respuesta.
        try:
            print(json.dumps(json.loads(state_text), indent=2, ensure_ascii=False))
        except (json.JSONDecodeError, TypeError):
            print(state_text)
    except Exception as e:
        print(f"❌ Error llamando a la herramienta: {e}")
        return

    user_question = input("\n¿Pregunta sobre el estado de Superset? ")
    if not user_question.strip():
        user_question = "Resume el estado actual de Superset."

    try:
        deepseek_response = ask_deepseek(user_question, state_text)
        print("\nRespuesta de DeepSeek:")
        print(deepseek_response['choices'][0]['message']['content'])
    except Exception as e:
        print(f"❌ Error consultando DeepSeek: {e}")

if __name__ == "__main__":
    main()