from sentence_transformers import CrossEncoder

from sql_chatbot.config import RERANKER_MODEL


class Reranker:
    def __init__(self):
        print("  Loading BGE Reranker...")
        self.model = CrossEncoder(RERANKER_MODEL, device="cpu")

    def rerank(
        self,
        query: str,
        candidates: list[tuple],
        original_scores: dict,
        tables: dict,
        top_k=5,
    ):
        pairs = []
        for name, _ in candidates[:10]:
            tbl = tables.get(name, {})
            desc = tbl.get("description", "")
            col_parts = [
                f"{c['name']}: {c.get('description', '')}"
                for c in tbl.get("columns", [])[:8]
                if c.get("description")
            ]
            text = desc + " " + "; ".join(col_parts) if col_parts else desc
            pairs.append((query, text))

        if not pairs:
            return [
                (name, original_scores.get(name, 0))
                for name, _ in candidates[:top_k]
            ]

        scores = self.model.predict(pairs).tolist()
        if isinstance(scores, float):
            scores = [scores]

        indexed = list(zip(candidates[:10], scores))
        indexed.sort(key=lambda x: (-x[1], -original_scores.get(x[0][0], 0)))

        return [
            (name, score)
            for (name, _), score in indexed[:top_k]
        ]

    def rerank_columns(
        self,
        query: str,
        candidates: list[tuple[str, float]],
        column_texts: dict[str, str],
        top_k=5,
    ):
        pairs = []
        col_names = []
        for name, _ in candidates:
            doc = column_texts.get(name, name)
            pairs.append((query, doc))
            col_names.append(name)

        if not pairs:
            return candidates[:top_k]

        scores = self.model.predict(pairs).tolist()
        if isinstance(scores, float):
            scores = [scores]

        indexed = list(zip(col_names, scores))
        indexed.sort(key=lambda x: -x[1])

        return [(name, score) for name, score in indexed[:top_k]]
