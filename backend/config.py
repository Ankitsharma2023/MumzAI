"""Central config — loads everything from the .env file in one place."""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ---- AI provider ----
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

# ---- OpenAI (optional provider; reliable paid quotas) ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBED_MODEL = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

# ---- MongoDB (catalog / source of truth) ----
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "mumzworld")
PRODUCTS_COLLECTION = "products"

# ---- ChromaDB (vector search index) ----
CHROMA_DIR = str(BASE_DIR / "chroma_db")
CHROMA_COLLECTION = "mumzworld_products"
# Embeddings via the Gemini API (multilingual EN+AR) — no local PyTorch model,
# so memory stays tiny and it runs on small/free hosts (e.g. Render 512MB).
GEMINI_EMBED_MODEL = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")

# ---- Files ----
DATA_FILE = BASE_DIR / "data" / "products.json"     # seed data
PROMPT_FILE = BASE_DIR / "prompts" / "system.prompt"
LOG_FILE = BASE_DIR / "logs" / "queries.jsonl"      # observability

# ---- Retrieval ----
TOP_K = 3          # products shown to the user
RETRIEVE_POOL = 8  # candidates pulled from each search before fusion
