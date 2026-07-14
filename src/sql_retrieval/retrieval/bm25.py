"""
BM25 Okapi sparse retrieval.

BM25 is a bag-of-words ranking function that scores documents based on
term frequency (TF) and inverse document frequency (IDF), with length
normalization. It's the modern standard for keyword search.
"""

import math
from collections import Counter


class BM25:
    def __init__(self):
        # Standard BM25 parameters tuned for short-to-medium text
        self.k1 = 1.5   # term-frequency saturation (higher = more TF impact)
        self.b = 0.75   # length normalization (0 = no normalization, 1 = full)

        self.names = []   # document identifiers (table names)
        self.docs = []    # document texts
        self.avgdl = 0    # average document length (in words)
        self.df = []      # term-frequency dict per document [{word: count}, ...]
        self.idf = {}     # inverse document frequency per term

    def index(self, texts: dict[str, str]):
        """
        Build the BM25 index from a dict of {table_name: searchable_text}.
        The text includes the table's purpose, keywords, columns, etc.
        """
        self.names = list(texts.keys())
        self.docs = [texts[n] for n in self.names]

        # Average document length (in words) for length normalization
        self.avgdl = sum(len(d.split()) for d in self.docs) / max(len(self.docs), 1)

        # Term-frequency counter per document
        self.df = [Counter(d.split()) for d in self.docs]

        # Compute IDF for every unique term across all documents
        N = len(self.docs)
        all_terms = set().union(*[set(c.keys()) for c in self.df])
        self.idf = {
            t: math.log(
                (N - sum(1 for c in self.df if t in c) + 0.5)
                / (sum(1 for c in self.df if t in c) + 0.5)
                + 1
            )
            for t in all_terms
        }

    def search(self, query: str, top_k=10):
        """
        Score every document against the query using BM25.
        Returns up to `top_k` (name, score) tuples with positive scores.
        """
        query_terms = query.lower().split()
        scores = []

        for i in range(len(self.docs)):
            s = 0.0
            dl = sum(self.df[i].values())  # document length (total words)
            for t in query_terms:
                if t in self.idf:
                    tf = self.df[i].get(t, 0)  # term frequency in this doc
                    # BM25 formula:
                    # score = IDF * (TF * (k1+1)) / (TF + k1 * (1 - b + b * dl/avgdl))
                    s += (
                        self.idf[t]
                        * tf
                        * (self.k1 + 1)
                        / (tf + self.k1 * (1 - self.b + self.b * dl / max(self.avgdl, 1)))
                    )
            scores.append(s)

        # Sort by score descending, keep only positive-score hits
        idx = sorted(range(len(scores)), key=lambda i: -scores[i])
        return [(self.names[i], scores[i]) for i in idx[:top_k] if scores[i] > 0]
