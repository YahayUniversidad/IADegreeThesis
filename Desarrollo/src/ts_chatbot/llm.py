"""Cliente DeepSeek (OpenAI-compatible API)."""

from __future__ import annotations

from openai import OpenAI

from src.ts_config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL,
        )
    return _client


def chat(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.1,
    max_tokens: int = 2048,
) -> str:
    """Envia mensajes a DeepSeek y retorna la respuesta.

    Args:
        messages: Lista de mensajes [{"role": ..., "content": ...}]
        model: Modelo a usar (default: DEEPSEEK_MODEL)
        temperature: Temperatura (baja para respuestas consistentes)
        max_tokens: Maximo de tokens en la respuesta

    Returns:
        Texto de la respuesta
    """
    client = get_client()
    response = client.chat.completions.create(
        model=model or DEEPSEEK_MODEL,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
