import chromadb
import numpy as np
from FlagEmbedding import BGEM3FlagModel

from sql_retrieval.config import CACHE_DIR, EMBEDDING_MODEL


class VectorRetriever:
    def __init__(self):
        self.encoder = BGEM3FlagModel(EMBEDDING_MODEL, device="cpu")
        persist = str(CACHE_DIR / "chroma")
        self.client = chromadb.PersistentClient(path=persist)
        self.table_collection = self.client.get_or_create_collection(
            name="tables", metadata={"hnsw:space": "cosine"}
        )
        self.column_collection = self.client.get_or_create_collection(
            name="columns", metadata={"hnsw:space": "cosine"}
        )
        self._table_count = 0
        self._column_count = 0

    def index_tables(self, texts: dict[str, str]):
        names = list(texts.keys())
        docs = [texts[n] for n in names]
        ids = [f"tbl_{i}" for i in range(len(names))]
        vecs = self.encoder.encode(docs, batch_size=8)["dense_vecs"]
        self.table_collection.add(
            ids=ids, embeddings=vecs.tolist(),
            metadatas=[{"name": n} for n in names],
            documents=docs
        )
        self._table_count = len(names)
        print(f"  Indexed {len(names)} tables into ChromaDB")

    def index_columns(self, texts: dict[str, str]):
        names = list(texts.keys())
        docs = [texts[n] for n in names]
        ids = [f"col_{i}" for i in range(len(names))]
        vecs = self.encoder.encode(docs, batch_size=8)["dense_vecs"]
        self.column_collection.add(
            ids=ids, embeddings=vecs.tolist(),
            metadatas=[{"name": n} for n in names],
            documents=docs
        )
        self._column_count = len(names)
        print(f"  Indexed {len(names)} columns into ChromaDB")

    def search_tables(self, query: str, top_k=10):
        vec = self.encoder.encode([query], batch_size=8)["dense_vecs"][0]
        results = self.table_collection.query(
            query_embeddings=[vec.tolist()], n_results=top_k
        )
        out = []
        for name, score in zip(results["metadatas"][0], results["distances"][0]):
            out.append((name["name"], 1 - score))
        return out

    def search_columns(self, query: str, top_k=10):
        vec = self.encoder.encode([query], batch_size=8)["dense_vecs"][0]
        results = self.column_collection.query(
            query_embeddings=[vec.tolist()], n_results=top_k
        )
        out = []
        for name, score in zip(results["metadatas"][0], results["distances"][0]):
            out.append((name["name"], 1 - score))
        return out
