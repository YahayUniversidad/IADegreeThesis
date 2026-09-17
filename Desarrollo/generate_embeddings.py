"""Script para generar/regenerar los embeddings del esquema y datos."""

import argparse
import sys

sys.path.insert(0, ".")

from src.ts_embeddings.pipeline import run_embedding_pipeline


def main():
    parser = argparse.ArgumentParser(description="Genera embeddings del esquema y datos")
    parser.add_argument("--rebuild", action="store_true", help="Eliminar y recrear la coleccion")
    parser.add_argument("--collection", default="tesis_db", help="Nombre de la coleccion (no utilizado, mantenido por compatibilidad)")
    args = parser.parse_args()

    result = run_embedding_pipeline(
        collection_name=args.collection,
        rebuild=args.rebuild,
    )

    print(f"\nResumen: {result}")


if __name__ == "__main__":
    main()
