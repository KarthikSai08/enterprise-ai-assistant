from rank_bm25 import BM25Okapi


class BM25:
    def __init__(self):
        self.model = None
        self.names: list[str] = []

    def index(self, texts: dict[str, str]):
        self.names = list(texts.keys())
        docs = [texts[n] for n in self.names]
        tokenized = [d.lower().split() for d in docs]
        self.model = BM25Okapi(tokenized)

    def search(self, query: str, top_k=6):
        if self.model is None:
            return []
        tokenized = query.lower().split()
        scores = self.model.get_scores(tokenized)
        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: -x[1])
        return [(self.names[i], scores[i]) for i, s in indexed[:top_k] if scores[i] > 0]
