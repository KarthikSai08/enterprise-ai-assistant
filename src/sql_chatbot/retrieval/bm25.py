from rank_bm25 import BM25Okapi
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
        self.model = BM25Okapi(tokenized)

    def search(self, query: str, top_k=6):
        if self.model is None:
            return []
        tokenized = self.tokenizer.tokenize(query)
        if not tokenized:
            return []
        scores = self.model.get_scores(tokenized)
        indexed = list(enumerate(scores))
        indexed.sort(key=lambda x: -x[1])
        return [(self.names[i], s) for i, s in indexed[:top_k] if s > 0]
