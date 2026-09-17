"""Orquestacion RAG: retrieve -> augment -> generate."""

from __future__ import annotations

from src.ts_embeddings.store import query_documents
from src.ts_mcp.tools import query_sql

from .llm import chat
from .prompts import build_rag_prompt
from .validator import extract_sql_from_response, validate_sql


def ask(question: str, n_context: int = 5, execute_sql: bool = True) -> dict:
    """Proceso RAG completo: recupera contexto, genera respuesta, opcionalmente ejecuta SQL.

    Args:
        question: Pregunta del usuario en lenguaje natural
        n_context: Numero de documentos a recuperar de embeddings (pgvector)
        execute_sql: Si True, ejecuta el SQL generado y agrega los resultados

    Returns:
        Dict con: response, sql, query_results, context_docs
    """
    context_docs = query_documents(question, n_results=n_context)

    messages = build_rag_prompt(question, context_docs)
    response = chat(messages)

    result = {
        "response": response,
        "sql": None,
        "query_results": None,
        "context_docs": [{"id": d["id"], "type": d.get("metadata", {}).get("type")} for d in context_docs],
    }

    sql = extract_sql_from_response(response)
    if sql:
        ok, msg = validate_sql(sql)
        if ok:
            result["sql"] = sql
            if execute_sql:
                qr = query_sql(sql)
                result["query_results"] = qr

                if "error" not in qr and qr.get("rows"):
                    followup_messages = messages + [
                        {"role": "assistant", "content": response},
                        {
                            "role": "user",
                            "content": (
                                f"Los resultados de la consulta son:\n\n"
                                f"Columnas: {qr['columns']}\n"
                                f"Filas ({qr['count']}): {qr['rows'][:20]}\n\n"
                                f"Por favor, presenta estos resultados de forma clara y "
                                f"responde a la pregunta original del usuario con estos datos."
                            ),
                        },
                    ]
                    final_response = chat(followup_messages)
                    result["response"] = final_response
        else:
            result["response"] += f"\n\n_Nota: El SQL generado no es seguro ({msg}). No se ejecuto._"

    return result
