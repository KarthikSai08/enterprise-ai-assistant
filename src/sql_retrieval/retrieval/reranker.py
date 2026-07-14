"""
Cross-encoder re-ranker using BGE Reranker v2-m3.

Unlike the bi-encoder (BGE-M3) which computes independent embeddings,
the cross-encoder processes the query and each candidate together through
a transformer, giving a more accurate relevance score – but it's slower,
so we only run it on the top-K candidates from BM25 + vector search.
"""

from sentence_transformers import CrossEncoder


class Reranker:
    def __init__(self):
        print("  Loading BGE Reranker...")
        # CrossEncoder takes (query, candidate_text) pairs and outputs relevance scores
        self.model = CrossEncoder("BAAI/bge-reranker-v2-m3", device="cpu")

    def rerank(
        self,
        query: str,
        candidates: list[tuple],
        original_scores: dict,
        tables: dict,
        top_k=5,
    ):
        """
        Re-rank the top 10 candidates using the cross-encoder.
        Final ordering is: original score (descending) → reranker score (descending).

        Parameters
        ----------
        candidates : list of (table_name, combined_score)
            The top-N candidates from BM25 + vector + RRF
        original_scores : dict
            {table_name: combined_score} used as primary sort key
        tables : dict
            Full table metadata, used to get each table's "purpose" text
        top_k : int
            Number of results to return after re-ranking
        """
        # Build (query, purpose) pairs for the cross-encoder
        pairs = [
            (query, tables.get(name, {}).get("purpose", ""))
            for name, _ in candidates[:10]
        ]

        if not pairs:
            return [
                (name, original_scores.get(name, 0))
                for name, _ in candidates[:top_k]
            ]

        # Get relevance scores from the cross-encoder
        scores = self.model.predict(pairs).tolist()
        if isinstance(scores, float):
            scores = [scores]

        # Sort: first by original score (desc), then by reranker score (desc)
        indexed = list(zip(candidates[:10], scores))
        indexed.sort(key=lambda x: (-original_scores.get(x[0][0], 0), -x[1]))

        return [
            (name, original_scores.get(name, 0))
            for (name, _), _ in indexed[:top_k]
        ]
