import requests
from sql_chatbot.config import OLLAMA_BASE_URL, OLLAMA_MODEL, GROQ_API_KEY, GROQ_MODEL, LLM_PROVIDER


def _call_ollama(prompt: str, model: str = None) -> str:
    payload = {
        "model": model or OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.1, "num_predict": 1024},
    }
    url = OLLAMA_BASE_URL.rstrip("/") + "/api/generate"
    try:
        resp = requests.post(url, json=payload, timeout=1200)
        resp.raise_for_status()
        return resp.json()["response"].strip()
    except requests.ConnectionError:
        raise RuntimeError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            f"Make sure Ollama is running (run 'ollama serve' in terminal) "
            f"and model '{model or OLLAMA_MODEL}' is pulled "
            f"(run 'ollama pull {model or OLLAMA_MODEL}')"
        ) from None


def _call_groq(prompt: str, model: str = None, api_key: str = None) -> str:
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
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers, json=payload, timeout=1200,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def generate_sql(prompt: str, provider: str = None, groq_key: str = None, model: str = None) -> str:
    provider = (provider or LLM_PROVIDER).lower()
    if provider == "groq":
        try:
            return _call_groq(prompt, model, groq_key)
        except requests.RequestException as e:
            print(f"  Groq failed ({e}) — falling back to Ollama")
            return _call_ollama(prompt, model)
    try:
        return _call_ollama(prompt, model)
    except (requests.RequestException, RuntimeError) as e:
        print(f"  Ollama failed ({e}) — falling back to Groq")
        return _call_groq(prompt, model, groq_key)


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
    provider = (provider or LLM_PROVIDER).lower()
    if provider == "groq":
        try:
            return _call_groq(prompt, model, groq_key)
        except requests.RequestException as e:
            print(f"  Answer LLM Groq failed ({e}) — falling back to Ollama")
            return _call_ollama(prompt, model)
    try:
        return _call_ollama(prompt, model)
    except (requests.RequestException, RuntimeError) as e:
        print(f"  Answer LLM Ollama failed ({e}) — falling back to Groq")
        return _call_groq(prompt, model, groq_key)
