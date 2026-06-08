"""FastAPI server — the API the React frontend talks to.

Endpoints:
    GET  /health   -> simple liveness check
    POST /chat     -> { message, lang } -> grounded answer + product cards

Run locally:
    uvicorn main:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import assistant
import rag
from models import ChatRequest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build the vector index from MongoDB if it isn't built yet.
    rag.get_collection()
    yield


app = FastAPI(title="Mumz Assistant API", lifespan=lifespan)

# Allow the React frontend (different origin) to call this API.
# For the demo we allow all origins; in prod you'd list your Vercel domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/chat")
def chat(req: ChatRequest):
    # Keep the last ~10 turns for context (bounds token usage).
    history = [{"role": t.role, "content": t.content} for t in req.history[-10:]]
    return assistant.get_response(req.message, req.lang, history, req.context_ids[-6:])
