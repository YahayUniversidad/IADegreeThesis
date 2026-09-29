"""Chatbot RAG: FastAPI endpoint para consultas en lenguaje natural."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from .rag import ask

app = FastAPI(
    title="Chatbot RAG - Tesis Datamart",
    description="Chatbot con DeepSeek + RAG para consultar la base de datos y datamart en lenguaje natural",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    question: str
    execute_sql: bool = True
    n_context: int = 5


class ChatResponse(BaseModel):
    response: str
    sql: str | None = None
    query_results: dict | None = None
    context_docs: list[dict] | None = None


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    """Responde una pregunta sobre la base de datos usando RAG + DeepSeek."""
    result = ask(
        question=req.question,
        n_context=req.n_context,
        execute_sql=req.execute_sql,
    )
    return ChatResponse(**result)


@app.get("/health")
def health():
    return {"status": "ok", "service": "chatbot-rag"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
