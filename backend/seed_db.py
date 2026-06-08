"""One-time: load products.json (the seed) into MongoDB (the real catalog).

Run once after setting MONGODB_URI in .env:
    python seed_db.py

This is idempotent — it clears and reloads, so you can re-run it safely.
MongoDB creates the database and collection automatically on first write.
"""
import json
import config
from db import get_collection
from generate_catalog import generate
from reviews import make_reviews


def seed() -> int:
    # 20 hand-crafted "hero" products + ~100 generated ones for catalog scale.
    curated = json.loads(config.DATA_FILE.read_text(encoding="utf-8"))
    generated = generate()
    products = curated + generated

    # Attach representative parent reviews (powers "what do parents say?").
    for p in products:
        p["reviews"] = make_reviews(p)

    # Precompute embeddings ONCE and store them in Mongo, so the deployed web
    # service builds its vector index from these — no model, no startup API calls.
    from rag import _searchable_text, _embed
    print(f"Embedding products via {config.LLM_PROVIDER} (one-time)...")
    vectors = _embed([_searchable_text(p) for p in products])
    for p, v in zip(products, vectors):
        p["embedding"] = v

    col = get_collection()
    col.delete_many({})                       # fresh start
    col.insert_many(products)
    col.create_index("id", unique=True)       # fast lookups by product id
    return len(curated), len(generated)


if __name__ == "__main__":
    n_curated, n_generated = seed()
    total = n_curated + n_generated
    print(f"Seeded {total} products into MongoDB "
          f"({config.MONGODB_DB}.{config.PRODUCTS_COLLECTION}) "
          f"= {n_curated} hero + {n_generated} generated.")
