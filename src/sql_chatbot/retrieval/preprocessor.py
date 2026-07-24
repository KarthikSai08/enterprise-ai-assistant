import re
from rapidfuzz import process, fuzz
from sql_chatbot.config import AGG_KEYWORDS, JOIN_KEYWORDS
from sql_chatbot.retrieval.tokenizer import SQLTokenizer

_SKIP_TYPOS = frozenset({
    "the", "and", "for", "are", "but", "not", "you", "all", "can",
    "has", "had", "was", "were", "been", "get", "got", "did", "use",
    "show", "list", "give", "find", "tell", "me",
    "how", "why", "what", "when", "where", "which",
})

class QueryPreprocessor:
    def __init__(self, all_terms: set[str], glossary: dict):
        self._all_terms = all_terms
        self._glossary_expansion: dict[str, list[str]] = {}
        for term, info in glossary.items():
            synonyms = info.get("synonyms", []) if isinstance(info, dict) else []
            for syn in synonyms:
                self._glossary_expansion.setdefault(syn.lower(), []).append(term.lower())
        self._typo_cache: dict[str, str] = {}
        self._tokenizer = SQLTokenizer(remove_stopwords=False, keep_full_identifiers=True)

    def correct_typos(self, query: str) -> str:
        cached = self._typo_cache.get(query)
        if cached is not None:
            return cached
        raw_tokens = query.lower().split()
        corrected = []
        for token in raw_tokens:
            if len(token) <= 2 or token in _SKIP_TYPOS:
                corrected.append(token)
                continue
            sub_tokens = self._tokenizer.tokenize(token)
            if sub_tokens:
                for sub in sub_tokens:
                    if len(sub) <= 2 or sub in _SKIP_TYPOS:
                        corrected.append(sub)
                        continue
                    best = process.extractOne(
                        sub, self._all_terms,
                        scorer=fuzz.WRatio,
                        score_cutoff=75,
                    )
                    corrected.append(best[0] if best else sub)
            else:
                best = process.extractOne(
                    token, self._all_terms,
                    scorer=fuzz.WRatio,
                    score_cutoff=75,
                )
                corrected.append(best[0] if best else token)
        result = " ".join(corrected)
        self._typo_cache[query] = result
        return result

    def expand_query(self, query: str) -> str:
        ql = query.lower()
        expansions = []
        for syn, terms in self._glossary_expansion.items():
            if syn in ql:
                expansions.extend(terms)
        if expansions:
            return query + " " + " ".join(expansions)
        return query

    @staticmethod
    def classify_query(ql: str, domains: list[str]) -> str:
        has_agg = any(kw in ql for kw in AGG_KEYWORDS)
        has_join_kw = any(kw in ql for kw in JOIN_KEYWORDS)
        single_domain = len(domains) == 1
        if has_agg and not has_join_kw and single_domain:
            return "simple_agg"
        if has_join_kw or len(domains) > 1:
            return "multi_table"
        return "ambiguous"

    @staticmethod
    def is_simple_count_query(query: str) -> bool:
        ql = query.lower().strip()
        count_signals = {"count", "how many", "how much", "total number of"}
        agg_signals = {"sum", "avg", "average", "maximum", "minimum"}
        is_count = any(s in ql for s in count_signals)
        has_total_as_agg = "total" in ql and any(kw in ql for kw in ["spend", "amount", "revenue", "sum"])
        has_specific = any(s in ql for s in agg_signals) or has_total_as_agg
        return is_count and not has_specific

    @staticmethod
    def _word_matches_query(word: str, q_words: set[str]) -> bool:
        return word in q_words or (word + "s") in q_words or (len(word) > 3 and word.endswith("s") and word[:-1] in q_words)

    @staticmethod
    def normalize_query(text: str) -> str:
        qn = re.sub(r"[^\w\s]", " ", text).strip()
        return re.sub(r"\s+", " ", qn)
