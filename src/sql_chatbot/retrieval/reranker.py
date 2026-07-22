import logging
import time

from sentence_transformers import CrossEncoder

from sql_chatbot.config import RERANKER_MODEL

logger = logging.getLogger(__name__)

_CACHE_TTL = 300
_cache: dict[str, tuple[float, list[float]]] = {}


class Reranker:
    def __init__(self):
        logger.info("Loading BGE Reranker...")
        self.model = CrossEncoder(RERANKER_MODEL, device="cpu")

    def _cached_predict(self, pairs: list[tuple[str, str]]) -> list[float]:
        key = str(sorted(pairs))
        now = time.monotonic()
        if key in _cache:
            ts, scores = _cache[key]
            if now - ts < _CACHE_TTL:
                return scores
        raw = self.model.predict(pairs)
        if isinstance(raw, (int, float)):
            scores = [float(raw)]
        else:
            scores = [float(s) for s in raw]
        _cache[key] = (now, scores)
        return scores

    def rerank(self, query: str, candidates: list[tuple],
                original_scores: dict, tables: dict, top_k=5):
        top_n = max(top_k * 2, 5)
        pairs = []
        pair_names = []
        for name, _ in candidates[:top_n]:
            tbl = tables.get(name, {})
            desc = tbl.get("description", "")
            col_parts = [
                f"{c['name']}: {c.get('description', '')}"
                for c in tbl.get("columns", [])[:6]
                if c.get("description")
            ]
            text = desc + " " + "; ".join(col_parts) if col_parts else desc
            pairs.append((query, text))
            pair_names.append(name)

        if not pairs:
            return [
                (name, original_scores.get(name, 0))
                for name, _ in candidates[:top_k]
            ]

        scores = self._cached_predict(pairs)
        indexed = list(zip(pair_names, scores))
        indexed.sort(key=lambda x: (-x[1], -original_scores.get(x[0], 0)))

        return [
            (name, score)
            for name, score in indexed[:top_k]
        ]

    def rerank_columns(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        column_texts: dict[str, str],
        top_k=5,
        original_scores: dict | None = None,
    ):
        top_n = max(top_k * 2, 10)
        pairs = []
        col_names = []
        for name, _ in candidates[:top_n]:
            doc = column_texts.get(name, name)
            pairs.append((query, doc))
            col_names.append(name)

        if not pairs:
            return candidates[:top_k]

        scores = self._cached_predict(pairs)
        indexed = list(zip(col_names, scores))
        indexed.sort(key=lambda x: (-x[1], -(original_scores or {}).get(x[0], 0)))

        return [(name, score) for name, score in indexed[:top_k]]
