# SQL Metadata Retrieval

Semantic table/column search engine for business databases. No LLM required.

Uses **BGE-M3 embeddings + BM25 + RRF + BGE Reranker** to find relevant tables, columns, and join paths from natural language queries.

## Setup

```bash
pip install -e .
```

## Database Configuration

Create a `.env` file in the project root:

```env
DB_SERVER=(localdb)\karthik
DB_NAME=SQLChatBot_DB
DB_TRUSTED=true
DB_SCHEMA=dbo
```

## Generate Knowledge Base from Database

```bash
python scripts/generate_kb_from_db.py
```

Connects to your SQL Server and generates YAML files from the actual schema (tables, columns, foreign keys, row counts, indexes).

## Enrich with Business Metadata

After generating the raw schema, enrich with hand-curated business keywords, intents, and descriptions:

```bash
python scripts/merge_metadata.py
```

## Run the Retrieval CLI

```bash
python -m sql_retrieval
```

| Command | Description |
|---------|-------------|
| `<query>` | Search for relevant tables, columns, and joins |
| `tables` | List all indexed tables |
| `help` | Show available commands |
| `exit` | Quit |

```
> show me all employees
> total sales by region
> products with low stock
```

## Project Structure

```
src/sql_retrieval/
├── __main__.py           Interactive CLI
├── config.py             Constants and path resolution
├── metadata/
│   └── loader.py         YAML knowledge base loader
└── retrieval/
    ├── bm25.py           BM25 sparse retrieval
    ├── vector.py         BGE-M3 dense retrieval via ChromaDB
    ├── reranker.py       BGE Reranker cross-encoder
    └── engine.py         Main retrieval pipeline

scripts/
├── generate_kb_from_db.py    Generate KB from SQL Server
├── generate_metadata.py      Business metadata definitions (TABLE_META/COL_META)
└── merge_metadata.py         Merge business metadata into knowledge base

knowledge_base/
├── tables/              68 YAML files — one per table
├── columns/             68 YAML files — one per table
├── joins/               joins.yaml — 149 FK relationships
├── glossary/            glossary.yaml — 17 business terms
├── domains/             domains.yaml — 14 business domains
├── business_rules/      business_rules.yaml — 12 business rules
├── sql_patterns/        sql_patterns.yaml — 10 SQL pattern templates
├── examples/            examples.yaml — 10 example query pairs
└── stats/               stats.yaml — database statistics
```

## Knowledge Base

| Directory | Files | Content |
|-----------|-------|---------|
| `tables/` | 68 | Table names, PKs, FKs, row counts, search keywords, intents |
| `columns/` | 68 | Column names, types, nullable, filterable/groupable, aggregations |
| `joins/` | 1 | 149 foreign key relationships with ON clauses |
| `glossary/` | 1 | 17 business terms with synonyms and descriptions |
| `domains/` | 1 | 14 domains with trigger/anti keywords and table mappings |
| `business_rules/` | 1 | 12 validation rules with conditions and messages |
| `sql_patterns/` | 1 | 10 SQL templates for common query patterns |
| `examples/` | 1 | 10 natural language to SQL example pairs |
| `stats/` | 1 | Database statistics |

## Regenerating

After schema changes in the database, re-run:

```bash
python scripts/generate_kb_from_db.py
python scripts/merge_metadata.py
```

## Dependencies

- Python >= 3.10
- pyodbc (requires ODBC Driver 17 for SQL Server)
- pyyaml, numpy, FlagEmbedding, chromadb, sentence-transformers
- rapidfuzz, rank_bm25, python-dotenv
