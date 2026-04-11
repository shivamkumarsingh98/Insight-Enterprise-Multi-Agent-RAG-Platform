# app/core/llm.py

from groq import Groq
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("llm")

_client = None

def get_groq_client() -> Groq:
    global _client
    if _client is None:
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set in .env")
        _client = Groq(api_key=settings.GROQ_API_KEY)
        logger.info("Groq client initialized")
    return _client


def call_llm(prompt: str, system: str = "", max_tokens: int = 500) -> str:
    """
    Groq LLaMA call — ye poore project mein use hoga.
    Ek jagah se sab LLM calls — easy to swap model later.
    """
    client = get_groq_client()

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",   # fast + free
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )
        result = response.choices[0].message.content.strip()
        logger.info("LLM call successful",
            model="llama-3.1-8b-instant",
            prompt_len=len(prompt),
            response_len=len(result)
        )
        return result

    except Exception as e:
        logger.error("LLM call failed", error=str(e))
        raise