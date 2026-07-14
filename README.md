# SQL Metadata Retrieval

Semantic table/column search engine for business databases. No LLM required.

Uses **BGE-M3 embeddings + BM25 + RRF + BGE Reranker** to find relevant tables, columns, and join paths from natural language queries.

## Setup

```bash
pip install -e .
```

## Usage

```bash
python -m sql_retrieval
```

### Commands

| Command | Description |
|---------|-------------|
| `<query>` | Search for relevant tables, columns, and joins |
| `tables` | List all indexed tables |
| `help` | Show available commands |
| `exit` | Quit |

## Project Structure

```
src/sql_retrieval/
├── __main__.py       Interactive CLI
├── config.py         Constants and path resolution
├── metadata/
│   └── loader.py     YAML knowledge base loader
└── retrieval/
    ├── bm25.py       BM25 sparse retrieval
    ├── vector.py     BGE-M3 dense retrieval via Qdrant
    ├── reranker.py   BGE Reranker cross-encoder
    └── engine.py     Main retrieval pipeline

data/contexts/
├── metadata.yaml       Table definitions (69 tables)
├── context.yaml        Synonyms, glossary, sample questions
├── domain_catalog.yaml Domain routing rules
└── joins.yaml          Join paths between tables
```

## Dependencies

Python >= 3.10, pyyaml, numpy, FlagEmbedding, qdrant-client, sentence-transformers
