"""The full pipeline: question -> retrieve -> ground -> generate -> validate.

This is the RAG loop. Note the GROUNDING step: even after the AI replies, we
drop any recommended product that wasn't actually retrieved — so the code itself
enforces "only recommend real, retrieved products," not just the prompt.
"""
import re
import time

import config
import db
import rag
from llm import generate_structured
from observability import log_event

# Words that signal a follow-up about products already shown.
_PRONOUNS = {"them", "these", "those", "it", "they", "this", "that", "both", "ones"}
_COMPARE = {"compare", "cheaper", "cheapest", "first", "second", "third", "which",
            "difference", "differ", "better", "cheap", "expensive", "one", "mean"}
# If any of these appear, it's a NEW product search, not a follow-up.
_PRODUCT_WORDS = {"seat", "seats", "stroller", "strollers", "pram", "prams", "formula",
                  "milk", "monitor", "monitors", "gift", "gifts", "diaper", "diapers",
                  "bath", "wash", "toy", "toys", "pump", "bottle", "bottles", "pillow",
                  "cot", "crib", "wipes", "walker", "car", "feeding", "nursing",
                  "maternity", "skincare", "lotion"}


def _is_followup(query: str, has_context: bool) -> bool:
    """True if the query refers to already-shown products (e.g. 'compare them')."""
    if not has_context:
        return False
    toks = set(re.findall(r"[a-z]+", query.lower()))
    if toks & _PRODUCT_WORDS:
        return False                       # names a product type → new search
    if toks & _PRONOUNS:
        return True
    return len(toks) <= 4 and bool(toks & _COMPARE)


# Qualifiers that make a query specific enough to answer directly (no MCQ needed).
_QUALIFIERS = {"under", "budget", "aed", "month", "months", "year", "years", "newborn",
               "infant", "toddler", "lactose", "isofix", "lightweight", "wifi", "travel",
               "heat", "shower", "boy", "girl", "premium", "cheap", "cheapest", "best",
               "spin", "rotation", "video", "audio", "organic", "sensitive", "compact"}


def _looks_vague(query: str) -> bool:
    """True for broad bare-category queries ('gift', 'stroller') → ask MCQs first."""
    toks = re.findall(r"[a-z0-9]+", query.lower())
    if any(t.isdigit() for t in toks):
        return False
    if set(toks) & _QUALIFIERS:
        return False
    if not (set(toks) & _PRODUCT_WORDS):
        return False
    return len(toks) <= 4


def _load_system_prompt() -> str:
    return config.PROMPT_FILE.read_text(encoding="utf-8")


def _format_line(p: dict) -> str:
    price = p.get("sale_price_aed") or p.get("price_aed")
    line = (
        f"- id: {p['id']} | {p['name_en']} | brand: {p['brand']} "
        f"| category: {p['category']} | price: AED {price} "
        f"| rating: {p['rating']} ({p['rating_count']} ratings) "
        f"| age: {p['recommended_age']} | weight: {p['weight_range_kg']} "
        f"| isofix: {p['isofix']} | in_stock: {p['in_stock']} "
        f"| desc: {p['description_en']}"
    )
    if p.get("reviews"):
        line += " | parent reviews: " + " // ".join(r["text"] for r in p["reviews"][:3])
    if p.get("warnings"):
        line += f" | WARNING: {p['warnings']}"
    return line


def _format_context(shown: list[dict], retrieved: list[dict]) -> str:
    """Two labeled groups: products already on screen, and fresh matches."""
    sections = []
    if shown:
        sections.append(
            "PRODUCTS ALREADY SHOWN IN THIS CONVERSATION (the shopper may refer to "
            "these as 'them', 'these', 'it', or by position like 'the first one' — "
            "use these for follow-ups such as comparing or asking about what was shown):\n"
            + "\n".join(_format_line(p) for p in shown)
        )
    sections.append(
        "PRODUCTS MATCHING THE CURRENT QUESTION:\n"
        + ("\n".join(_format_line(p) for p in retrieved) if retrieved else "(none)")
    )
    return "\n\n".join(sections)


def get_response(user_query: str, lang: str = "en", history: list | None = None,
                 context_ids: list | None = None) -> dict:
    start = time.time()
    history = history or []           # [{"role": "user"|"assistant", "content": str}, ...]
    context_ids = context_ids or []   # products already shown earlier in this chat

    # Products already on screen — so "compare them", "is the first cheaper",
    # "tell me more about the second one" reason over the right items.
    shown = db.get_products_by_ids(context_ids)
    shown_ids = {p["id"] for p in shown}

    # 1. RETRIEVE — for a follow-up ("compare them"), reuse the already-shown
    #    products and skip a fresh search (which would pull in unrelated items).
    followup = _is_followup(user_query, bool(shown))
    if followup:
        retrieved_ids, retrieved = [], []
    else:
        retrieved_ids = rag.hybrid_retrieve(user_query)
        retrieved = [p for p in db.get_products_by_ids(retrieved_ids) if p["id"] not in shown_ids]

    # 2. GROUND — context = already-shown products + fresh matches
    context = _format_context(shown, retrieved)
    lang_line = "Reply in Arabic." if lang == "ar" else "Reply in English."
    user_prompt = f"{context}\n\n{lang_line}\nShopper question: {user_query}"

    # For broad bare-category queries ("gift", "stroller"), force clarifying MCQs.
    if not followup and _looks_vague(user_query):
        user_prompt += (
            "\n\nIMPORTANT: This request is broad. Do NOT recommend products yet. Instead ask "
            "1-3 short multiple-choice clarifying questions (age group, budget, or key feature) "
            "in clarifying_questions, and leave recommended_products empty."
        )

    # 3. GENERATE — ask the AI (one retry if the provider hiccups)
    system_prompt = _load_system_prompt()
    try:
        result = generate_structured(system_prompt, user_prompt, history)
    except Exception:
        result = generate_structured(system_prompt, user_prompt, history)

    # 4. ENFORCE GROUNDING — allow already-shown products + freshly retrieved ones
    allowed = shown_ids | {p["id"] for p in retrieved}
    valid_ids = [i for i in result.recommended_products if i in allowed]
    recommended = db.get_products_by_ids(valid_ids)

    latency_ms = int((time.time() - start) * 1000)

    # 5. OBSERVE — log the whole interaction
    log_event({
        "query": user_query,
        "lang": lang,
        "provider": config.LLM_PROVIDER,
        "context_ids": context_ids,
        "retrieved_ids": retrieved_ids,
        "recommended_ids": valid_ids,
        "confidence": result.confidence,
        "latency_ms": latency_ms,
    })

    return {
        "answer": result.answer,
        "confidence": result.confidence,
        "safety_notes": result.safety_notes,
        "products": recommended,        # full product objects for the cards
        "retrieved_ids": retrieved_ids, # transparency: what the search found
        "latency_ms": latency_ms,
        "lang": lang,
        "clarifying_questions": [
            {"question": c.question, "options": c.options}
            for c in result.clarifying_questions
        ],
    }
