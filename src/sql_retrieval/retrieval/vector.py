"""
Dense vector retrieval using BGE-M3 embeddings stored in an in-memory
Qdrant collection with Cosine distance.

BGE-M3 produces a 1024-dimensional embedding per text. Qdrant stores these
vectors and supports efficient HNSW-based nearest-neighbor search.

Embeddings are cached to disk so the 4-minute CPU encoding only happens
on the very first run.
"""

from pathlib import Path
                         
import numpy as np                         
from FlagEmbedding import BGEM3FlagModel                         
from qdrant_client import QdrantClient                         
from qdrant_client.models import Distance, PointStruct, VectorParams

from sql_retrieval.config import CACHE_DIR


class VectorRetriever:
    def __init__(self):
        # Disk cache for pre-computed embeddings (avoids 4-min re-encode)
        self.cache_dir = CACHE_DIR / "vectors"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load the BGE-M3 embedding model (downloads on first use)
        print("  Loading BGE-M3...")
        self.encoder = BGEM3FlagModel("BAAI/bge-m3", device="cpu")

        # In-memory Qdrant (fast, no file locks). Re-index from cached
        # embeddings takes <1s, so persistence doesn't save time here.
        self.store = QdrantClient(":memory:")
        self.store.create_collection(
            "tables",
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
        )

        self.index_map = {}  # maps Qdrant point ID → table name

    def index(self, texts: dict[str, str]):
        """
        Encode all table texts and upsert them into Qdrant.
        On the first run this takes ~4 minutes on CPU.
        Subsequent runs load cached embeddings in <1s.
        """
        names = list(texts.keys())
        cache_file = self.cache_dir / "embeddings.npy"
        names_file = self.cache_dir / "names.txt"

        # ── Cache hit: load pre-computed embeddings from disk ──────────
        if cache_file.exists() and names_file.exists():
            cached_names = names_file.read_text(encoding="utf-8").splitlines()
            if cached_names == names:
                print("  Loading cached embeddings...")
                all_vecs = np.load(cache_file)
                points = []
                for i, (name, vec) in enumerate(zip(names, all_vecs)):
                    points.append(
                        PointStruct(id=i, vector=vec.tolist(), payload={"name": name})
                    )
                    self.index_map[i] = name
                self.store.upsert("tables", points=points)
                print(f"  Loaded {len(points)} cached vectors")
                return

        # ── Cache miss: encode all table texts ─────────────────────────
        print(f"  Encoding {len(names)} texts (first run, ~6 min on CPU)...")

        # Encode all table descriptions in one batch call
        encoded = self.encoder.encode(
            [texts[n] for n in names], batch_size=8
        )["dense_vecs"]

        # Save to disk for next time
        np.save(cache_file, encoded)
        names_file.write_text("\n".join(names), encoding="utf-8")

        # Upload points to Qdrant
        points = []
        for i, (name, vec) in enumerate(zip(names, encoded)):
            points.append(
                PointStruct(id=i, vector=vec.tolist(), payload={"name": name})
            )
            self.index_map[i] = name
        self.store.upsert("tables", points=points)
        print(f"  Indexed {len(points)} vectors into Qdrant")

    def search(self, query: str, top_k=10):
        """
        Encode the query with the same BGE-M3 model,
        then find the top_k nearest tables by cosine similarity in Qdrant.
        """
        vec = self.encoder.encode([query], batch_size=8)["dense_vecs"][0]
        hits = self.store.query_points(
            "tables", query=vec.tolist(), limit=top_k
        ).points

        # Deduplicate by name (keep highest score if duplicates exist)
        seen = {}
        for h in hits:
            name = h.payload.get("name", "")
            if name not in seen or h.score > seen[name]:
                seen[name] = h.score

        return sorted(seen.items(), key=lambda x: -x[1])[:top_k]
