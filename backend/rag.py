"""Retrieval — turn a shopper's words into the most relevant products.

HYBRID SEARCH = two retrievers fused:
  1. Vector search  (ChromaDB + Sentence Transformers) — matches MEANING, so
     "car seat for my newborn" finds "Group 0+ infant carrier" with no shared words.
  2. Keyword search — matches exact terms ("lactose", "isofix", a brand name).
We fuse the two ranked lists with Reciprocal Rank Fusion (RRF), a simple,
well-known technique that needs no score tuning.

ChromaDB only holds embeddings + product IDs. The full product data lives in
MongoDB (see db.py) — this is the catalog-vs-search-index separation.
"""
import re
import time
from functools import lru_cache

import chromadb
from google import genai

import config
import db


@lru_cache(maxsize=1)
def _genai_client() -> "genai.Client":
    return genai.Client(api_key=config.GEMINI_API_KEY)


def _embed(texts: list[str]) -> list[list[float]]:
    """Embed text via the configured provider (no local model — tiny memory)."""
    if config.LLM_PROVIDER == "openai":
        return _embed_openai(texts)
    return _embed_gemini(texts)


def _embed_openai(texts: list[str]) -> list[list[float]]:
    """Embed via OpenAI (paid — high limits, no throttling needed)."""
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    vectors: list[list[float]] = []
    BATCH = 256
    for i in range(0, len(texts), BATCH):
        resp = client.embeddings.create(
            model=config.OPENAI_EMBED_MODEL, input=texts[i:i + BATCH]
        )
        vectors.extend([d.embedding for d in resp.data])
    return vectors


def _embed_gemini(texts: list[str]) -> list[list[float]]:
    """Embed via Gemini, throttled to respect the free ~100 embeds/minute."""
    client = _genai_client()
    vectors: list[list[float]] = []
    BATCH = 90
    for i in range(0, len(texts), BATCH):
        batch = texts[i:i + BATCH]
        for _ in range(6):
            try:
                resp = client.models.embed_content(
                    model=config.GEMINI_EMBED_MODEL, contents=batch
                )
                vectors.extend([e.values for e in resp.embeddings])
                break
            except Exception as e:  # back off on rate limit, then retry
                if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                    time.sleep(62)
                else:
                    raise
        if i + BATCH < len(texts):
            time.sleep(62)  # stay under ~100 embeds/minute between batches
    return vectors


@lru_cache(maxsize=1)
def _chroma() -> "chromadb.api.ClientAPI":
    # In-memory: the index is rebuilt from MongoDB's precomputed embeddings at
    # startup, so there's no heavy model and no persistent files to ship.
    return chromadb.EphemeralClient()


def _searchable_text(p: dict) -> str:
    """The text we embed / keyword-match for a product."""
    return " ".join([
        p.get("name_en", ""),
        p.get("name_ar", ""),          # index Arabic too (bilingual search)
        p.get("brand", ""),
        p.get("category", ""),
        p.get("subcategory", ""),
        p.get("recommended_age", ""),
        p.get("age_group", ""),
        p.get("description_en", ""),
        p.get("description_ar", ""),    # index Arabic description
        " ".join(p.get("tags", [])),
        " ".join(p.get("key_features", [])),
    ])


def get_collection(rebuild: bool = False):
    """Return the Chroma collection, building it from MongoDB if it's empty."""
    client = _chroma()
    if rebuild:
        try:
            client.delete_collection(config.CHROMA_COLLECTION)
        except Exception:
            pass
    col = client.get_or_create_collection(config.CHROMA_COLLECTION)
    if col.count() == 0:
        ids, embeddings, docs = [], [], []
        for p in db.get_all_products_for_index():
            text = _searchable_text(p)
            emb = p.get("embedding") or _embed([text])[0]  # fallback if missing
            ids.append(p["id"])
            embeddings.append(emb)
            docs.append(text)
        if ids:
            col.add(ids=ids, embeddings=embeddings, documents=docs)
    return col


def _tokens(text: str) -> set[str]:
    # \w is Unicode-aware in Python 3, so this keeps Arabic letters too.
    return set(re.findall(r"\w+", text.lower(), re.UNICODE))


def vector_rank(query: str, k: int) -> list[str]:
    """Product IDs ranked by semantic similarity."""
    col = get_collection()
    count = col.count()
    if count == 0:
        return []
    res = col.query(
        query_embeddings=_embed([query]),
        n_results=min(k, count),
    )
    return res["ids"][0]


def keyword_rank(query: str, k: int) -> list[str]:
    """Product IDs ranked by how many query words appear in the product text."""
    q = _tokens(query)
    scored = []
    for p in db.get_all_products():
        overlap = len(q & _tokens(_searchable_text(p)))
        if overlap:
            scored.append((overlap, p["id"]))
    scored.sort(reverse=True)
    return [pid for _, pid in scored[:k]]


def hybrid_retrieve(query: str, k: int = config.TOP_K) -> list[str]:
    """Fuse vector + keyword rankings with Reciprocal Rank Fusion (RRF)."""
    pool = config.RETRIEVE_POOL
    ranked_lists = [vector_rank(query, pool), keyword_rank(query, pool)]

    C = 60  # RRF constant; dampens the weight of lower ranks
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, pid in enumerate(ranked):
            scores[pid] = scores.get(pid, 0.0) + 1.0 / (C + rank)

    return sorted(scores, key=scores.get, reverse=True)[:k]
