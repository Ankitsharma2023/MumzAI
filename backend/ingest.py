"""One-time: build the vector search index from the MongoDB catalog.

Run AFTER seed_db.py:
    python ingest.py

Reads products from MongoDB, embeds them with Sentence Transformers, and stores
the vectors in ChromaDB. Re-run any time the catalog changes.
"""
import rag

if __name__ == "__main__":
    col = rag.get_collection(rebuild=True)
    print(f"Built vector index with {col.count()} products in ChromaDB.")
