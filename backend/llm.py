"""Provider-agnostic LLM layer.

This is the ONE file that knows which AI provider we use. Everything else just
calls `generate_structured(...)`. Switching from free Gemini to Claude (their
stack) is a single change in .env (LLM_PROVIDER=claude) — no code changes.

Every provider is asked to return JSON matching the AssistantResponse schema,
which we then validate with Pydantic.
"""
import config
from models import AssistantResponse


def generate_structured(
    system_prompt: str, user_prompt: str, history: list | None = None
) -> AssistantResponse:
    history = history or []   # list of {"role": "user"|"assistant", "content": str}
    provider = config.LLM_PROVIDER
    if provider == "gemini":
        return _gemini(system_prompt, user_prompt, history)
    if provider == "claude":
        return _claude(system_prompt, user_prompt, history)
    if provider == "openai":
        return _openai(system_prompt, user_prompt, history)
    raise ValueError(f"Unknown LLM_PROVIDER: {provider!r} (use 'gemini', 'openai', or 'claude')")


# ---------- OpenAI (paid; reliable quotas) ----------
def _openai(system_prompt: str, user_prompt: str, history: list) -> AssistantResponse:
    from openai import OpenAI

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": t["role"], "content": t["content"]} for t in history]
    messages.append({"role": "user", "content": user_prompt})

    completion = client.beta.chat.completions.parse(
        model=config.OPENAI_MODEL,
        messages=messages,
        response_format=AssistantResponse,  # structured output → validated object
    )
    return completion.choices[0].message.parsed


# ---------- Google Gemini (free, default) ----------
def _gemini(system_prompt: str, user_prompt: str, history: list) -> AssistantResponse:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=config.GEMINI_API_KEY)

    # Prior turns first (Gemini uses role "model" for the assistant), then the new turn.
    contents = []
    for turn in history:
        role = "model" if turn["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": turn["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_prompt}]})

    resp = client.models.generate_content(
        model=config.GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=AssistantResponse,   # Gemini fills exactly this shape
            temperature=0.3,
        ),
    )
    if getattr(resp, "parsed", None) is not None:
        return resp.parsed
    return AssistantResponse.model_validate_json(resp.text)


# ---------- Anthropic Claude (their stack; one-line switch) ----------
def _claude(system_prompt: str, user_prompt: str, history: list) -> AssistantResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    messages = [{"role": t["role"], "content": t["content"]} for t in history]
    messages.append({"role": "user", "content": user_prompt})

    resp = client.messages.parse(
        model=config.ANTHROPIC_MODEL,
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
        output_format=AssistantResponse,   # Claude structured outputs
    )
    return resp.parsed_output
