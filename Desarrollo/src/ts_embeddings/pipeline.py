##
## @file pipeline.py
##
## Orquesta la generación de documentos para embeddings y su almacenamiento en PostgreSQL (pgvector).
##
## @version septiembre 2026
##

from __future__ import annotations

from .document_builder import build_all_documents
from .store import add_documents, collection_count, delete_collection


def run_embedding_pipeline(
    collection_name: str = "tesis_db",
    rebuild: bool = False,
) -> dict:
    """Ejecuta el pipeline completo de embeddings.

    Args:
        collection_name: Nombre de la coleccion (no utilizado, mantenido por compatibilidad)
        rebuild: Si True, elimina la coleccion existente y la recrea

    Returns:
        Dict con estadisticas del pipeline
    """
    if rebuild:
        print(f"Eliminando coleccion '{collection_name}' existente...")
        delete_collection(collection_name)

    print("Generando documentos para embeddings...")
    docs = build_all_documents()
    print(f"  Documentos generados: {len(docs)}")

    stats = {"schema": 0, "sample": 0, "fewshot": 0}
    for d in docs:
        dtype = d.get("metadata", {}).get("type", "unknown")
        if dtype in stats:
            stats[dtype] += 1

    print(f"  - Esquemas: {stats['schema']}")
    print(f"  - Muestras: {stats['sample']}")
    print(f"  - Few-shot: {stats['fewshot']}")

    print("Generando embeddings y almacenando en PostgreSQL (pgvector)...")
    inserted = add_documents(docs, collection_name)
    total = collection_count(collection_name)

    print(f"  Documentos insertados: {inserted}")
    print(f"  Total en coleccion: {total}")
    print("Pipeline de embeddings completado.")

    return {
        "documents_generated": len(docs),
        "inserted": inserted,
        "total_in_collection": total,
        "breakdown": stats,
    }


if __name__ == "__main__":
    run_embedding_pipeline(rebuild=True)
