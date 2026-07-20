import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
import yaml

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

DOMAIN_BOOST_TOP_PRIMARY = 0.75
DOMAIN_BOOST_TOP_NON_PRIMARY = 0.55
DOMAIN_BOOST_OTHER_PRIMARY = 0.50
DOMAIN_BOOST_OTHER_NON_PRIMARY = 0.40
DOMAIN_BOOST_EXISTING_FLOOR = 0.85
DOMAIN_BOOST_NEW_FLOOR = 0.65

KEYWORD_SCORE_PER_MATCH = 1.00
KEYWORD_NULL_TABLE_BASE = 0.01

GENERIC_ALIAS_STOPWORDS = frozenset({
    "total", "amount", "value", "date", "status", "code", "name", "details", "record"
})

AGG_KEYWORDS = frozenset({
    "count", "total", "sum", "avg", "average", "how many",
})

JOIN_KEYWORDS = frozenset({
    "vs", "versus", "breakdown",
    "compare", "comparison",
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
DB_TRUSTED = os.getenv("DB_TRUSTED", "true").lower() in ("true", "1", "yes")
DB_SCHEMA = os.getenv("DB_SCHEMA", "dbo")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")
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


class RetrievalConfig(BaseModel):
    top_k: int = Field(default=10, ge=1)
    rrf_k: int = Field(default=60, ge=1)
    column_rrf_k: int = Field(default=60, ge=1)
    column_top_k: int = Field(default=15, ge=1)
    score_threshold: float = Field(default=0.001, ge=0)
    keyword_score_threshold: float = Field(default=0.0001, ge=0)
    score_gap_factor: float = Field(default=0.3, ge=0, le=1)


class CandidatePoolConfig(BaseModel):
    multiplier: int = Field(default=5, ge=1)
    min: int = Field(default=30, ge=1, alias="min")
    rrf_k_multiplier: int = Field(default=2, ge=1)
    rrf_k_min: int = Field(default=3, ge=1)
    reranker_k_multiplier: int = Field(default=1, ge=1)
    reranker_k_min: int = Field(default=2, ge=1)


class DomainDetectionConfig(BaseModel):
    sim_min_abs: float = Field(default=0.20, ge=0, le=1)
    sim_gap: float = Field(default=0.08, ge=0, le=1)
    file_fallback_floor: float = Field(default=0.15, ge=0, le=1)


class ScoreBlendingConfig(BaseModel):
    ce_weight: float = Field(default=0.40, ge=0, le=1)
    rrf_weight: float = Field(default=0.60, ge=0, le=1)


class DomainBoostConfig(BaseModel):
    top_primary: float = Field(default=0.75, ge=0, le=1)
    top_non_primary: float = Field(default=0.55, ge=0, le=1)
    other_primary: float = Field(default=0.50, ge=0, le=1)
    other_non_primary: float = Field(default=0.40, ge=0, le=1)
    existing_floor: float = Field(default=0.85, ge=0, le=1)
    new_floor: float = Field(default=0.65, ge=0, le=1)


class KeywordScoringConfig(BaseModel):
    score_per_match: float = Field(default=1.00, ge=0)
    null_table_base: float = Field(default=0.01, ge=0)


class TuningConfig(BaseModel):
    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    candidate_pool: CandidatePoolConfig = Field(default_factory=CandidatePoolConfig)
    domain_detection: DomainDetectionConfig = Field(default_factory=DomainDetectionConfig)
    score_blending: ScoreBlendingConfig = Field(default_factory=ScoreBlendingConfig)
    domain_boost: DomainBoostConfig = Field(default_factory=DomainBoostConfig)
    keyword_scoring: KeywordScoringConfig = Field(default_factory=KeywordScoringConfig)


_CONFIG_PATH = BASE_DIR / "tuning_config.yaml"
_cached_config: TuningConfig | None = None


def load_tuning_config(path: Path | None = None) -> TuningConfig:
    global _cached_config
    if _cached_config is not None:
        return _cached_config

    p = path or _CONFIG_PATH
    if not p.exists():
        _cached_config = TuningConfig()
        return _cached_config

    with open(p, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    try:
        _cached_config = TuningConfig.model_validate(raw)
    except ValidationError as e:
        print(f"  WARNING: tuning_config.yaml validation failed: {e}")
        print(f"  Falling back to default values")
        _cached_config = TuningConfig()

    return _cached_config


try:
    _tc = load_tuning_config()
    r = _tc.retrieval
    TOP_K = r.top_k
    RRF_K = r.rrf_k
    COLUMN_RRF_K = r.column_rrf_k
    COLUMN_TOP_K = r.column_top_k
    SCORE_THRESHOLD = r.score_threshold
    KEYWORD_SCORE_THRESHOLD = r.keyword_score_threshold
    SCORE_GAP_FACTOR = r.score_gap_factor

    cp = _tc.candidate_pool
    CANDIDATE_POOL_MULTIPLIER = cp.multiplier
    CANDIDATE_POOL_MIN = cp.min
    RRF_K_MULTIPLIER = cp.rrf_k_multiplier
    RRF_K_MIN = cp.rrf_k_min
    RERANKER_K_MULTIPLIER = cp.reranker_k_multiplier
    RERANKER_K_MIN = cp.reranker_k_min

    dd = _tc.domain_detection
    DOMAIN_SIM_MIN_ABS = dd.sim_min_abs
    DOMAIN_SIM_GAP = dd.sim_gap
    DOMAIN_FILE_FALLBACK_FLOOR = dd.file_fallback_floor

    sb = _tc.score_blending
    CE_WEIGHT = sb.ce_weight
    RRF_WEIGHT = sb.rrf_weight

    db_ = _tc.domain_boost
    DOMAIN_BOOST_TOP_PRIMARY = db_.top_primary
    DOMAIN_BOOST_TOP_NON_PRIMARY = db_.top_non_primary
    DOMAIN_BOOST_OTHER_PRIMARY = db_.other_primary
    DOMAIN_BOOST_OTHER_NON_PRIMARY = db_.other_non_primary
    DOMAIN_BOOST_EXISTING_FLOOR = db_.existing_floor
    DOMAIN_BOOST_NEW_FLOOR = db_.new_floor

    ks = _tc.keyword_scoring
    KEYWORD_SCORE_PER_MATCH = ks.score_per_match
    KEYWORD_NULL_TABLE_BASE = ks.null_table_base

    print(f"  Loaded tuning config from tuning_config.yaml")
except Exception as e:
    print(f"  WARNING: Could not load tuning_config.yaml: {e}")
