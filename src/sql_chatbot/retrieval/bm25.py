import bm25s
import logging
from sql_chatbot.retrieval.tokenizer import SQLTokenizer

logger = logging.getLogger(__name__)

class BM25:
    def __init__(self, tokenizer=None):
        self.model = None
        self.names: list[str] = []
        self.tokenizer = tokenizer or SQLTokenizer(
            remove_stopwords=True, keep_full_identifiers=True
        )

    def index(self, texts: dict[str, str]):
        self.names = list(texts.keys())
        docs = [texts[n] for n in self.names]
        tokenized = [self.tokenizer.tokenize(d) for d in docs]

        self.model = bm25s.BM25()
        # bm25s accepts raw list[list[str]] tokens directly — it builds
        # its own vocab internally, no need to route through bm25s.tokenize()
        self.model.index(tokenized, show_progress=False)

    def search(self, query: str, top_k=6):
        if self.model is None or not self.names:
            return []
        tokenized = self.tokenizer.tokenize(query)
        if not tokenized:
            return []

        k = min(top_k, len(self.names))
        if k == 0:
            return []

        # retrieve() expects a batch of queries -> wrap single query in a list
        doc_ids, scores = self.model.retrieve(
            [tokenized], k=k, show_progress=False
        )

        # doc_ids/scores have shape (1, k) since we passed a batch of 1
        results = zip(doc_ids[0].tolist(), scores[0].tolist())
        return [(self.names[i], s) for i, s in results if s > 0]