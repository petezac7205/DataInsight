from openai import OpenAI

import os
from dotenv import load_dotenv

load_dotenv()

GROK_API_KEY = os.getenv("GROK_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.groq.com/openai/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")

if not GROK_API_KEY:
    raise RuntimeError("Missing GROK_API_KEY in project root .env")


_client = OpenAI(api_key=GROK_API_KEY, base_url=LLM_BASE_URL) if GROK_API_KEY else None


def ensure_ai_ready() -> None:
    if not GROK_API_KEY:
        raise RuntimeError("Missing GROK_API_KEY in environment/.env")


def chat_completion(messages: list[dict], temperature: float = 0.0, model: str | None = None):
    ensure_ai_ready()

    return _client.chat.completions.create(
        model=model or LLM_MODEL,
        messages=messages,
        temperature=temperature,
    )
