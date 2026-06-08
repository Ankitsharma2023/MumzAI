"""MongoDB access — the product catalog is the source of truth.

The vector store (ChromaDB) is built FROM this; this is the system of record.
Same separation Mumzworld has with PostgreSQL (catalog) + Elasticsearch (search).
"""
from functools import lru_cache
from pymongo import MongoClient
import config


@lru_cache(maxsize=1)
def _client() -> MongoClient:
    """One shared connection, created lazily on first use."""
    return MongoClient(config.MONGODB_URI)


def get_collection():
    return _client()[config.MONGODB_DB][config.PRODUCTS_COLLECTION]


def get_all_products() -> list[dict]:
    """Every product (without _id or the big embedding vector)."""
    return list(get_collection().find({}, {"_id": 0, "embedding": 0}))


def get_all_products_for_index() -> list[dict]:
    """Every product INCLUDING its precomputed embedding (for the vector index)."""
    return list(get_collection().find({}, {"_id": 0}))


def get_products_by_ids(ids: list[str]) -> list[dict]:
    """Fetch specific products and return them in the SAME order as `ids`."""
    docs = get_collection().find({"id": {"$in": ids}}, {"_id": 0, "embedding": 0})
    by_id = {d["id"]: d for d in docs}
    return [by_id[i] for i in ids if i in by_id]
