import logging
import random
import time

import requests
from sql_chatbot.config import OLLAMA_BASE_URL, OLLAMA_MODEL, GROQ_API_KEY, GROQ_MODEL, LLM_PROVIDER

logger = logging.getLogger(__name__)


def _call_ollama(prompt: str, model: str = None, max_retries: int = 2) -> str:
    payload = {
        "model": model or OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 1024},
    }
    url = OLLAMA_BASE_URL.rstrip("/") + "/api/generate"
    last_exc = None
    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(url, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            if "response" not in data:
                raise ValueError(f"Unexpected Ollama response format: {data}")
            return data["response"].strip()
        except requests.RequestException as e:
            last_exc = e
            if attempt < max_retries:
                sleep_s = min(2 ** attempt + random.uniform(0, 1), 30)
                logger.warning(
                    "Ollama request failed (%s). Retrying in %.1fs... (attempt %d/%d)",
                    e, sleep_s, attempt + 1, max_retries,
                )
                time.sleep(sleep_s)
    raise RuntimeError(
        f"Cannot reach Ollama at {OLLAMA_BASE_URL} after {max_retries + 1} attempts. "
        f"Make sure Ollama is running (run 'ollama serve' in terminal) "
        f"and model '{model or OLLAMA_MODEL}' is pulled "
        f"(run 'ollama pull {model or OLLAMA_MODEL}')"
    ) from last_exc


def _call_groq(prompt: str, model: str = None, api_key: str = None, max_retries: int = 1) -> str:
    key = api_key or GROQ_API_KEY
    if not key:
        raise ValueError("Groq API key not found. Set GROQ_API_KEY in .env")
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": model or GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.1,
        "max_tokens": 1024,
    }
    for attempt in range(max_retries + 1):
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers, json=payload, timeout=60,
        )
        if resp.status_code != 429:
            resp.raise_for_status()
            data = resp.json()
            if not data.get("choices"):
                raise ValueError(f"Unexpected Groq response format: {data}")
            return data["choices"][0]["message"]["content"].strip()
        if attempt < max_retries:
            retry_after = int(resp.headers.get("Retry-After", 10))
            logger.warning(
                "Groq rate limited (429). Retrying after %ds... (attempt %d/%d)",
                retry_after, attempt + 1, max_retries,
            )
            time.sleep(min(retry_after, 30))
    raise RuntimeError(
        f"Groq API rate limited after {max_retries + 1} attempts. "
        "Try again later or switch to a different provider."
    )


def _call_with_fallback(prompt: str, provider: str, groq_key: str | None, model: str | None) -> str:
    provider = (provider or LLM_PROVIDER).lower()
    if provider == "groq":
        try:
            return _call_groq(prompt, model, groq_key)
        except (requests.RequestException, RuntimeError) as e:
            logger.warning("Groq failed (%s) — falling back to Ollama", e)
            return _call_ollama(prompt, model)
    try:
        return _call_ollama(prompt, model)
    except (requests.RequestException, RuntimeError) as e:
        if groq_key or GROQ_API_KEY:
            logger.warning("Ollama failed (%s) — falling back to Groq", e)
            return _call_groq(prompt, model, groq_key)
        raise


def call_llm(prompt: str, provider: str = None, groq_key: str = None, model: str = None) -> str:
    return _call_with_fallback(prompt, provider, groq_key, model)


def generate_answer(
    user_query: str,
    sql: str,
    columns: list[str],
    rows: list[list],
    row_count: int,
    provider: str = None,
    groq_key: str = None,
    model: str = None,
) -> str:
    from sql_chatbot.generation.prompt import build_answer_prompt
    prompt = build_answer_prompt(user_query, sql, columns, rows, row_count)
    return _call_with_fallback(prompt, provider, groq_key, model)
