-- Migracion: ChromaDB -> pgvector
-- Ejecutar en la base de datos postgres_db

CREATE EXTENSION IF NOT EXISTS vector;

CREATE SCHEMA IF NOT EXISTS embeddings;

CREATE TABLE IF NOT EXISTS embeddings.embeddings (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(384) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw
    ON embeddings.embeddings USING hnsw (embedding vector_cosine_ops);
