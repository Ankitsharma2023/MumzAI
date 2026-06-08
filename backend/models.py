"""Pydantic schemas — the fixed shapes our data and AI output must take."""
from typing import Literal
from pydantic import BaseModel, Field


class ClarifyingQuestion(BaseModel):
    """One multiple-choice question to narrow down a vague request."""
    question: str = Field(description="A short question to ask the shopper.")
    options: list[str] = Field(description="2-4 concrete answer options.")


class AssistantResponse(BaseModel):
    """The structured shape the AI MUST return. The provider is forced to fill
    exactly these fields, then we validate it here — so the app never has to
    deal with free-form text or broken JSON."""

    answer: str = Field(
        description="The reply shown to the parent, in the requested language."
    )
    recommended_products: list[str] = Field(
        default_factory=list,
        description="Product IDs to recommend. MUST come from the retrieved catalog.",
    )
    safety_notes: str = Field(
        default="",
        description="Age/weight/safety or pediatrician note when relevant; else empty.",
    )
    confidence: Literal["high", "medium", "low"] = Field(
        default="medium",
        description="How well the retrieved catalog matched the question.",
    )
    clarifying_questions: list[ClarifyingQuestion] = Field(
        default_factory=list,
        description="If the request is too vague, 1-3 MCQ questions to narrow it; else empty.",
    )


class ChatTurn(BaseModel):
    """One past turn of the conversation (for memory)."""
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    """What the React frontend sends to POST /chat."""
    message: str
    lang: Literal["en", "ar"] = "en"
    history: list[ChatTurn] = []      # recent turns so follow-ups have context
    context_ids: list[str] = []       # products already shown (for "compare them" etc.)
