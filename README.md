# Mumz Assistant 🌸

An AI shopping concierge for **Mumzworld** — a parent asks a question in plain
language (English or Arabic) and gets a **grounded** answer plus real product
cards from the catalog. Built for the Mumzworld AI Native Intern interview.

> A mom types *"safe car seat for my 3-month-old under AED 1500"* → in ~2s she
> gets a warm answer + product cards (image, AED price, Tabby installments,
> rating, age, ISOFIX badge), and can flip the whole UI to Arabic.

---

## Architecture

```
 React / Next.js  ──HTTP──>  FastAPI (Python)
 (Vercel)                     │
                              ├── MongoDB Atlas      ← product catalog (source of truth)
                              ├── ChromaDB           ← vector search index (built from Mongo)
                              ├── Sentence Transformers ← embeddings (meaning)
                              └── Gemini / Claude     ← grounded answer (structured output)
```

**The RAG loop:** question → **hybrid retrieve** (vector + keyword, fused with
RRF) → **ground** (build context from only the retrieved products) → **generate**
(LLM, forced into a Pydantic schema) → **enforce grounding in code** (drop any
recommended product that wasn't retrieved) → cards + answer.

**Why two data stores?** MongoDB is the catalog (system of record); ChromaDB is
the search index built from it. Same separation Mumzworld runs in production
with **PostgreSQL + Elasticsearch**.

---

## Tech stack

| Layer | Tech |
|---|---|
| Frontend | Next.js (React + TypeScript), EN/AR toggle with RTL |
| Backend | FastAPI (Python) |
| Catalog DB | MongoDB Atlas (PyMongo) |
| Vector store | ChromaDB |
| Embeddings | Sentence Transformers (`paraphrase-multilingual-MiniLM-L12-v2`, EN+AR) |
| Retrieval | Hybrid (semantic + keyword) fused with Reciprocal Rank Fusion |
| LLM | **Gemini** (free, default) — one-line switch to **Claude** |
| Validation | Pydantic v2 + provider structured outputs |
| Evals | `backend/evals/` (recall / precision on a test set) |
| Observability | JSONL request log (`backend/logs/queries.jsonl`) |
| Conversation memory | recent turns + on-screen products sent back as context (follow-ups like "compare them" work) |
| Voice input | browser Web Speech API, English + Arabic, no API cost |
| Catalog | 120 products in MongoDB (20 hand-crafted + 100 generated for scale) |

The LLM lives behind one file (`backend/llm.py`). Switch free Gemini → Claude
(Mumzworld's stack) by setting `LLM_PROVIDER=claude` in `.env`. No code changes.

---

## Run it locally

> 🪟 **On Windows?** See **[WINDOWS.md](WINDOWS.md)** — just double-click the
> `setup.bat` → `seed.bat` → `run.bat` scripts in `backend/`, then `setup.bat` →
> `run.bat` in `frontend/`. The steps below are the Mac/Linux equivalents.

### Prerequisites
- Python 3.11+, Node.js 18+
- A free **MongoDB Atlas** connection string
- A free **Gemini API key** (https://aistudio.google.com/apikey)

### 1) Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # then fill in GEMINI_API_KEY + MONGODB_URI

python seed_db.py                  # load products.json -> MongoDB (run once)
python ingest.py                   # build the vector index in ChromaDB (run once)
python evals/run_evals.py          # (optional) prove retrieval works

uvicorn main:app --reload --port 8000
```
Backend is now at http://localhost:8000 (try http://localhost:8000/health).

### 2) Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```
Open http://localhost:3000 and start chatting.

---

## How it maps to the job description

| JD requirement | Where |
|---|---|
| RAG pipelines over the product catalog | `rag.py` (hybrid) + `assistant.py` |
| Vector stores | ChromaDB |
| Claude / frontier models | `llm.py` — Gemini now, Claude via one env flag |
| Pydantic / structured output | `models.py` + enforced LLM output |
| Evals | `evals/run_evals.py` |
| Production observability | `observability.py` |
| Bilingual EN + AR | UI toggle + Arabic catalog data |
| Deployed demo | Vercel (frontend) + Render (backend) |

---

## Talking points for the interview

- **"Why is it grounded?"** The LLM only sees retrieved products, and after it
  replies I drop any product ID that wasn't actually retrieved — grounding is
  enforced in *code*, not just the prompt. Can't hallucinate a product.
- **"Why hybrid search?"** Vector search catches meaning ("newborn" → "Group 0+");
  keyword search catches exact terms ("lactose", a brand). RRF fuses both. Best
  of both, no score tuning.
- **"Catalog vs search index?"** Mongo is the source of truth; Chroma is the
  index built from it — exactly your Postgres + Elasticsearch split. At scale I'd
  put the embeddings in Elasticsearch's kNN index and reuse infra you already run.
- **"Why not LangChain?"** I kept retrieval explicit so it's auditable and I can
  explain every step. I'd reach for LangChain/LlamaIndex for multi-step agents.
- **"Model choice?"** Provider-agnostic by design — free Gemini for building,
  one env flag to run on Claude (your stack) for production.
- **"What would you build next?"** WhatsApp Personal Shopper — same backend, swap
  the React frontend for the WhatsApp Business API.

---

## Honest limitations (say these before the CTO does)

- 120 dummy products (20 hand-crafted + 100 generated), not the 250k-SKU
  catalog. The pipeline doesn't change at scale — point the vector index at the
  full catalog.
- Product images are real Mumzworld CDN photos picked by category (a few
  categories use a branded placeholder); they're representative, not the exact SKU.
- Voice input works in Chrome/Edge only (browser limitation), and needs mic permission.
- No live inventory / pricing — static seed data.
- `0.0.0.0/0` MongoDB access and open CORS are demo settings; lock both in prod.
- Arabic copy is machine-drafted; a native reviewer would polish it for launch.
