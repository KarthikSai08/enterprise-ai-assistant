from pathlib import Path

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

SCORE_THRESHOLD = 0.10
SCORE_GAP_FACTOR = 0.3

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

AGGREGATION_TYPES = {
    "total": "SUM", "sum": "SUM", "count": "COUNT",
    "avg": "AVG", "average": "AVG",
}
