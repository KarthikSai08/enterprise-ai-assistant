import os
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

BASE_DIR = Path(__file__).parent.parent.parent
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
TABLES_DIR = KNOWLEDGE_BASE_DIR / "tables"
COLUMNS_DIR = KNOWLEDGE_BASE_DIR / "columns"
JOINS_DIR = KNOWLEDGE_BASE_DIR / "joins"
GLOSSARY_DIR = KNOWLEDGE_BASE_DIR / "glossary"
DOMAINS_DIR = KNOWLEDGE_BASE_DIR / "domains"
BUSINESS_RULES_DIR = KNOWLEDGE_BASE_DIR / "business_rules"
SQL_PATTERNS_DIR = KNOWLEDGE_BASE_DIR / "sql_patterns"
EXAMPLES_DIR = KNOWLEDGE_BASE_DIR / "examples"
STATS_DIR = KNOWLEDGE_BASE_DIR / "stats"

CACHE_DIR = BASE_DIR / ".cache"

EMBEDDING_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

TOP_K = 10
RRF_K = 60
COLUMN_RRF_K = 60
COLUMN_TOP_K = 15
SCORE_THRESHOLD = 0.001
KEYWORD_SCORE_THRESHOLD = 0.0001
SCORE_GAP_FACTOR = 0.3

CANDIDATE_POOL_MULTIPLIER = 5
CANDIDATE_POOL_MIN = 30
RRF_K_MULTIPLIER = 2
RRF_K_MIN = 3
RERANKER_K_MULTIPLIER = 1
RERANKER_K_MIN = 2

DOMAIN_SIM_MIN_ABS = 0.20
DOMAIN_SIM_GAP = 0.08
DOMAIN_FILE_FALLBACK_FLOOR = 0.15

CE_WEIGHT = 0.40
RRF_WEIGHT = 0.60

DOMAIN_BOOST_FACTOR = 0.60
DOMAIN_BOOST_FLOOR = 0.40

KEYWORD_SCORE_PER_MATCH = 1.00
KEYWORD_NULL_TABLE_BASE = 0.01

GENERIC_COLUMN_NAMES = frozenset({
    "total", "amount", "value", "date", "status", "code", "name", "details", "record",
})

AGG_KEYWORDS = frozenset({
    "count", "total", "sum", "avg", "average", "how many",
})

JOIN_KEYWORDS = frozenset({
    "vs", "versus", "breakdown", "compare", "comparison",
})

STOPWORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "can", "shall", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off", "over",
    "under", "again", "further", "then", "once", "here", "there", "when",
    "where", "why", "how", "all", "each", "every", "both", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "just", "because", "get", "got",
    "me", "my", "our", "your", "his", "her", "its", "their", "this",
    "that", "these", "those", "what", "which", "who", "whom", "any",
    "about", "up", "down", "also", "now", "then", "but", "or", "if",
})

DB_SERVER = os.getenv("DB_SERVER", "")
DB_NAME = os.getenv("DB_NAME", "")
DB_USER = os.getenv("DB_USER", "")
DB_PASS = os.getenv("DB_PASS", "")
DB_USE_WINDOWS_AUTH = os.getenv("DB_USE_WINDOWS_AUTH", os.getenv("DB_TRUSTED", "true")).lower() in ("true", "1", "yes")
DB_SCHEMA = os.getenv("DB_SCHEMA", "dbo")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")

AGGREGATION_TYPES = {
    "total": "SUM", "sum": "SUM", "count": "COUNT",
    "avg": "AVG", "average": "AVG",
}

SENSITIVE_COLUMN_PATTERNS = frozenset({
    "mobileno", "mobile", "phone", "phonenumber", "whatsapp",
    "accountnumber", "bankaccount", "ifsc", "ifsccode",
    "password", "pwd", "secret", "apikey", "encryptionkey", "token",
    "gstno", "gst", "panno", "pan", "aadhar", "aadhaar",
    "salary", "basicsalary", "ctc", "netpay", "hra",
    "creditcardno", "cvv", "otp", "pin",
})


def is_sensitive_column(col_name: str) -> bool:
    c = col_name.lower().replace("_", "")
    return any(pat in c for pat in SENSITIVE_COLUMN_PATTERNS)
