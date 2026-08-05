import logging
import re
import sys
from pathlib import Path
from rapidfuzz.distance import JaroWinkler
from sql_chatbot.config import KNOWLEDGE_BASE_DIR, BASE_DIR

logger = logging.getLogger(__name__)

_TERMS_PATH = KNOWLEDGE_BASE_DIR / "terms" / "terms.yaml"

_VALUE_CORRECTIONS: dict[str, str] = {}
_ENUM_VALUES: dict[str, list[str]] = {}

try:
    import yaml
    if _TERMS_PATH.exists():
        with open(_TERMS_PATH, encoding="utf-8") as _f:
            _data = yaml.safe_load(_f) or {}
        _VALUE_CORRECTIONS = _data.get("value_corrections", {})
        _ENUM_VALUES = _data.get("enum_values", {})
    else:
        _scripts_dir = str(BASE_DIR / "scripts")
        if _scripts_dir not in sys.path:
            sys.path.insert(0, _scripts_dir)
        from terms_data import VALUE_CORRECTIONS as _VC, ENUM_VALUES as _EV  # type: ignore[import-untyped]
        _VALUE_CORRECTIONS = _VC
        _ENUM_VALUES = _EV
except Exception as e:
    logger.error("Failed to load value corrections and enum values: %s", e)

_VALUE_CORRECTIONS_LOWER = {k.lower(): v for k, v in _VALUE_CORRECTIONS.items()}
_WORD_RE = re.compile(r"[a-zA-Z0-9]+[%+\-]?")
_PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


class EntityValueExtractor:
    def __init__(self, tables: dict):
        self.tables = tables
        self.value_index: dict[str, list[tuple[str, str]]] = {}
        self._max_ngram = 1

        def _register(table_name, col_name, value):
            sv = str(value).strip().lower()
            if not sv:
                return
            self.value_index.setdefault(sv, []).append((table_name, col_name))
            ngram_len = len(sv.split())
            if ngram_len > self._max_ngram:
                self._max_ngram = ngram_len

        for table_name, t in tables.items():
            for c in t.get("columns", []):
                for v in c.get("sample_values", []):
                    _register(table_name, c["name"], v)

        for table_col, values in _ENUM_VALUES.items():
            if "." not in table_col:
                continue

            for k in _VALUE_CORRECTIONS_LOWER:
                ngram_len = len(k.split())
                if ngram_len > self._max_ngram:
                    self._max_ngram = ngram_len

        self._all_values = list(self.value_index.keys())

    def _ngrams(self, words: list[str]) -> list[tuple[str, int, int]]:
        out = []
        n = len(words)
        for size in range(min(self._max_ngram, n), 0, -1):
            for i in range(n - size + 1):
                out.append((" ".join(words[i:i + size]), i, i + size))
        return out

    def _resolve_value(self, phrase: str, jw_cutoff: float = 0.90) -> str | None:
        phrase_l = phrase.lower()

        corrected = _VALUE_CORRECTIONS_LOWER.get(phrase_l)
        if corrected and corrected.lower() in self.value_index:
            return corrected.lower()

        if phrase_l in self.value_index:
            return phrase_l

        if len(phrase_l) < 4:
            return None
        best_value, best_score = None, 0.0
        for candidate in self._all_values:
            score = JaroWinkler.normalized_similarity(phrase_l, candidate)
            if score > best_score:
                best_score, best_value = score, candidate
        return best_value if best_value and best_score >= jw_cutoff else None

    _ENTITY_ROLE_PRIORITY = {
        "dimension": 0, "identifier": 0, "foreign_key": 1, "status": 2, "attribute": 3, "metric": 4,
    }

    def detect_entities(self, query: str) -> list[dict]:
        words = _WORD_RE.findall(query.lower())
        matched_spans: set[tuple[int, int]] = set()
        entities: list[dict] = []

        for phrase, start, end in self._ngrams(words):
            if any(start < e and s < end for s, e in matched_spans):
                continue
            resolved = self._resolve_value(phrase)
            if resolved:
                matched_spans.add((start, end))
                matches = []
                for table_name, col_name in self.value_index[resolved]:
                    col_info = next(
                        (c for c in self.tables.get(table_name, {}).get("columns", []) if c["name"] == col_name),
                        None,
                    )
                    role = (col_info or {}).get("role", "attribute")
                    importance = (col_info or {}).get("importance", "medium")
                    priority = self._ENTITY_ROLE_PRIORITY.get(role, 5)
                    matches.append({
                        "table": table_name,
                        "column": col_name,
                        "value": resolved,
                        "matched_from": phrase,
                        "domain": self.tables.get(table_name, {}).get("domain", ""),
                        "_priority": priority,
                        "_importance_rank": {"high": 0, "medium": 1, "low": 2}.get(importance, 3),
                    })
                matches.sort(key=lambda x: (x["_priority"], x["_importance_rank"]))
                seen_values_col_pairs : set[tuple[str, str, str]] = set()
                for m in matches:
                    pair_key = (m["table"], m["column"], m["value"])
                    if pair_key in seen_values_col_pairs:
                        continue
                    seen_values_col_pairs.add(pair_key)
                    d = dict(m)
                    d.pop("_priority", None)
                    d.pop("_importance_rank", None)
                    entities.append(d)
        return entities

    def resolve_locked_tables(self, entities: list[dict]) -> dict:
        by_domain: dict[str, list[dict]] = {}
        for e in entities:
            by_domain.setdefault(e["domain"], []).append(e)
        locked: dict[str, dict] = {}
        suppress: set[str] = set()
        for domain, ents in by_domain.items():
            if not domain:
                continue
            table_names = {e["table"] for e in ents}
            if len(table_names) == 1:
                master = next(iter(table_names))
            else:
                master = max(
                    table_names,
                    key=lambda tn: (
                        _PRIORITY_RANK.get(self.tables.get(tn, {}).get("priority", "medium").lower(), 2),
                        self.tables.get(tn, {}).get("search_weight", 5),
                    ),
                )
            locked[master] = {"matched": [e for e in ents if e["table"] == master], "domain": domain}
            for tn in table_names:
                if tn != master:
                    suppress.add(tn)
        return {"locked": locked, "suppress": suppress}
