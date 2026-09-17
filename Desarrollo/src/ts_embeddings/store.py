"""Almacenamiento y busqueda de embeddings con pgvector."""

from __future__ import annotations

import json

import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer

from src.ts_config import DATABASE_URL, EMBEDDING_MODEL

EMBEDDINGS_TABLE = "embeddings.embeddings"

_model: SentenceTransformer | None = None


def _get_conn():
    return psycopg2.connect(DATABASE_URL)


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model


def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_model()
    embeddings = model.encode(texts, show_progress_bar=False)
    return embeddings.tolist()


def ensure_table():
    """Crea la tabla embeddings y el indice si no existen."""
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cur.execute("CREATE SCHEMA IF NOT EXISTS embeddings")
            cur.execute(f"""
                CREATE TABLE IF NOT EXISTS {EMBEDDINGS_TABLE} (
                    id TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB DEFAULT '{{}}',
                    embedding vector(384) NOT NULL
                )
            """)
            cur.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw
                ON {EMBEDDINGS_TABLE} USING hnsw (embedding vector_cosine_ops)
            """)
        conn.commit()
    finally:
        conn.close()


def add_documents(
    docs: list[dict],
    collection_name: str = "tesis_db",
    batch_size: int = 50,
) -> int:
    """Agrega documentos con embeddings a PostgreSQL.

    Args:
        docs: Lista de dicts con 'id', 'text', 'metadata'
        collection_name: No utilizado, mantenido por compatibilidad de API
        batch_size: Tamano del lote para insertar

    Returns:
        Numero de documentos insertados
    """
    ensure_table()
    conn = _get_conn()
    total = 0
    try:
        with conn.cursor() as cur:
            for i in range(0, len(docs), batch_size):
                batch = docs[i : i + batch_size]
                texts = [d["text"] for d in batch]
                ids = [d["id"] for d in batch]
                metadatas = [json.dumps(d.get("metadata", {})) for d in batch]
                embeddings = embed_texts(texts)

                for doc_id, content, meta, emb in zip(ids, texts, metadatas, embeddings):
                    vec_str = "[" + ",".join(str(v) for v in emb) + "]"
                    cur.execute(
                        f"""
                        INSERT INTO {EMBEDDINGS_TABLE} (id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s::vector)
                        ON CONFLICT (id) DO UPDATE
                        SET content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                        """,
                        (doc_id, content, meta, vec_str),
                    )
                total += len(batch)
        conn.commit()
    finally:
        conn.close()
    return total


def query_documents(
    query_text: str,
    n_results: int = 5,
    collection_name: str = "tesis_db",
    filter_metadata: dict | None = None,
) -> list[dict]:
    """Busca los documentos mas similares a una consulta.

    Returns:
        Lista de dicts con: id, text, metadata, distance
    """
    ensure_table()
    query_embedding = embed_texts([query_text])[0]
    vec_str = "[" + ",".join(str(v) for v in query_embedding) + "]"

    conn = _get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if filter_metadata:
                meta_filter = json.dumps(filter_metadata)
                cur.execute(
                    f"""
                    SELECT id, content, metadata,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM {EMBEDDINGS_TABLE}
                    WHERE metadata @> %s::jsonb
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (vec_str, meta_filter, vec_str, n_results),
                )
            else:
                cur.execute(
                    f"""
                    SELECT id, content, metadata,
                           1 - (embedding <=> %s::vector) AS similarity
                    FROM {EMBEDDINGS_TABLE}
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s
                    """,
                    (vec_str, vec_str, n_results),
                )
            rows = cur.fetchall()

        docs = []
        for row in rows:
            docs.append({
                "id": row["id"],
                "text": row["content"],
                "metadata": row["metadata"] if isinstance(row["metadata"], dict) else {},
                "distance": 1.0 - row["similarity"],
            })
        return docs
    finally:
        conn.close()


def collection_count(collection_name: str = "tesis_db") -> int:
    """Retorna el numero de documentos en la tabla."""
    ensure_table()
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {EMBEDDINGS_TABLE}")
            return cur.fetchone()[0]
    finally:
        conn.close()


def delete_collection(collection_name: str = "tesis_db"):
    """Elimina todos los embeddings."""
    ensure_table()
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(f"TRUNCATE TABLE {EMBEDDINGS_TABLE}")
        conn.commit()
    finally:
        conn.close()
