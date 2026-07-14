"""Application-wide constants and path resolution."""

from pathlib import Path

# ── Score thresholds ─────────────────────────────────────────────────

# Minimum relevance score [-1, 1] a table needs to appear in results
SCORE_THRESHOLD = 0.10

# For simple aggregation queries: if the second-best table's score is less
# than this fraction of the best table's score, drop it (keep only top-1)
SCORE_GAP_FACTOR = 0.3

# ── Query classification keywords ───────────────────────────────────

AGG_KEYWORDS = frozenset({   # trigger "simple_agg" classification
    "count", "total", "sum", "avg", "average", "how many",
})

JOIN_KEYWORDS = frozenset({  # trigger "multi_table" classification
    "and", "vs", "versus", "by", "per", "with", "breakdown",
    "compare", "comparison",
})

# ── Stopwords (filtered out during keyword matching) ────────────────

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

# Maps natural-language aggregation words to their SQL equivalents
AGGREGATION_TYPES = {
    "total": "SUM", "sum": "SUM", "count": "COUNT",
    "avg": "AVG", "average": "AVG",
}

# ── Directory resolution ────────────────────────────────────────────

def _find_project_root():
    """
    Walk up from this file's directory until we find pyproject.toml or .git.
    This lets us locate the project root regardless of where the code is installed.
    """
    p = Path(__file__).resolve()
    for parent in p.parents:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return p.parent.parent.parent

PROJECT_ROOT = _find_project_root()

# data/ holds all YAML files (context knowledge base + evaluation queries)
DATA_DIR = PROJECT_ROOT / "data"

# data/contexts/ holds the four YAML knowledge-base files
CONTEXTS_DIR = DATA_DIR / "contexts"

# .cache/ stores pre-computed vector embeddings so we skip the 4-minute
# re-encode on every startup
CACHE_DIR = PROJECT_ROOT / ".cache"
