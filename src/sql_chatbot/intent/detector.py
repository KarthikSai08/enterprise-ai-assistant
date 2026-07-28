import json
import logging
import re

from sql_chatbot.config import LLM_PROVIDER, GROQ_API_KEY
from sql_chatbot.generation.llm_client import call_llm

logger = logging.getLogger(__name__)

_JSON_EXTRACT = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.I)


INTENT_RULES = [
    ("COUNT", re.compile(r"\b(count|how many|total number of|number of)\b", re.I)),
    ("SUM", re.compile(r"\b(total|sum|overall)\b", re.I)),
    ("AVG", re.compile(r"\b(average|avg|mean)\b", re.I)),
    ("LIST", re.compile(r"\b(list|show|display|get me|fetch|all)\b", re.I)),
    ("FILTER_ACTIVE", re.compile(r"\b(active|enabled|current)\b", re.I)),
    ("FILTER_INACTIVE", re.compile(r"\b(inactive|disabled|deactivated)\b", re.I)),
    ("COMPARE", re.compile(r"\b(compare|vs|versus|breakdown|difference|diff|v/s)\b", re.I)),
    ("RANK", re.compile(r"\b(top|bottom|highest|lowest|largest|smallest|best|worst)\b", re.I)),
    ("TREND", re.compile(r"\b(trend|growth|increase|decrease|change|over time|month over month|m-o-m)\b", re.I)),
    ("RATIO", re.compile(r"\b(percentage|percent|ratio|proportion|share|%)\b", re.I)),
]

ACTION_WORDS = re.compile(
    r"\b(count|how many|total|sum|overall|average|avg|mean|list|show|display|"
    r"get me|fetch|all|active|enabled|current|inactive|disabled|deactivated|"
    r"number of|compare|vs|versus|breakdown|difference|diff|v/s|"
    r"top|bottom|highest|lowest|largest|smallest|best|worst|"
    r"trend|growth|increase|decrease|change|over time|month over month|m\-o\-m|"
    r"percentage|percent|ratio|proportion|share)\b", re.I
)

INTENT_PROMPT = """Extract the intent and core entity from this database question.

Question: "{query}"

Respond ONLY with JSON in this exact format, no markdown, no explanation:
{{"intents": ["COUNT" or "SUM" or "AVG" or "LIST" or "FILTER_ACTIVE" or "FILTER_INACTIVE"], "entity": "core subject words only, no action words"}}

Example: "total active employees" -> {{"intents": ["SUM", "FILTER_ACTIVE"], "entity": "employees"}}
Example: "how many products" -> {{"intents": ["COUNT"], "entity": "products"}}"""


def _llm_available() -> bool:
    if LLM_PROVIDER == "groq":
        return bool(GROQ_API_KEY)
    return True


def detect_intent_rule_based(query: str) -> dict | None:
    matched = [label for label, pattern in INTENT_RULES if pattern.search(query)]
    if not matched:
        return None
    entity = ACTION_WORDS.sub(" ", query).strip()
    entity = re.sub(r"\s+", " ", entity)
    if not entity:
        return None
    return {"intents": matched, "entity": entity, "source": "rules"}


def detect_intent_llm(query: str) -> dict | None:
    if not _llm_available():
        return None
    try:
        raw = call_llm(INTENT_PROMPT.format(query=query))
        m = _JSON_EXTRACT.search(raw)
        raw = m.group(1) if m else raw.strip()
        data = json.loads(raw)
        if "entity" in data and data["entity"]:
            data["source"] = "llm"
            return data
    except Exception as e:
        logger.warning("Intent detection LLM fallback failed: %s", e)
    return None


def detect_intent(query: str) -> dict:
    result = detect_intent_rule_based(query)
    if result:
        return result
    result = detect_intent_llm(query)
    if result:
        return result
    return {"intents": [], "entity": query, "source": "fallback"}
