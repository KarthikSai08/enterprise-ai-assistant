# SQL Metadata Retrieval

Semantic table/column search engine for business databases with two-stage LLM SQL generation.

**Stage 1:** BGE-M3 embeddings + BM25 + RRF + BGE Reranker → finds relevant tables/columns from natural language.

**Stage 2:** LLM (Ollama or Groq) generates SQL → executes it → a second LLM call produces a natural-language answer.

## Setup

```bash
pip install -e .
```

Install Ollama and pull a model (e.g., `llama3.2`):

```bash
ollama pull llama3.2
```

## Configuration

Create a `.env` file in the project root:

```env
# Database (SQL Server)
DB_SERVER=(localdb)\karthik
DB_NAME=SQLChatBot_DB
DB_TRUSTED=true
DB_SCHEMA=dbo

# LLM Provider — "ollama" (default) or "groq"
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Groq (optional — used when LLM_PROVIDER=groq or Ollama fails)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama3-70b-8192
```

### Optional: Tuning Configuration

Edit `tuning_config.yaml` at the project root to adjust retrieval thresholds (candidate pool size, domain boosts, score weights, etc.) without touching code.

## Generate Knowledge Base from Database

```bash
python scripts/generate_kb_from_db.py
```

Connects to your SQL Server and generates YAML files from the actual schema (tables, columns, foreign keys, row counts, indexes).

## Enrich with Business Metadata

```bash
python scripts/merge_metadata.py
```

Merges hand-curated business keywords, intents, and descriptions into the generated schema files.

## Run the CLI

```bash
python -m sql_retrieval
```

| Command | Description |
|---------|-------------|
| `<query>` | Search → generate SQL → execute → natural answer |
| `tables` | List all indexed tables |
| `help` | Show available commands |
| `exit` | Quit |

```
> show me all employees

Domains: people

  #    Table                          Score    Domain       Columns
  ────────────────────────────────────────────────────────────────────────────────
  1    Employees                      0.8502  people       EmployeeID, FullName, Email, DepartmentID, ManagerID, HireDate

  Joins:
    Employees.DepartmentID = Departments.DepartmentID  (maps each employee to their department)

  Tables: 1 | Columns: EmployeeID, FullName, Email, DepartmentID, ManagerID, HireDate | Latency: 245ms
  Confidence: 0.9234

  Generating SQL...
  ────────────────────────────────────────────────────────────────────────────
  SELECT EmployeeID, FullName, Email, DepartmentID, ManagerID, HireDate
  FROM Employees
  ────────────────────────────────────────────────────────────────────────────

  Result: 150 row(s)
    [1, 'Alice Smith', 'alice@example.com', 3, 10, '2021-06-15']
    [2, 'Bob Jones', 'bob@example.com', 3, 10, '2022-01-10']
    ...

  There are 150 employees in the database, with details including names, emails, departments, managers, and hire dates available.
```

## Run the API Server

```bash
uvicorn sql_retrieval.server:app --host 0.0.0.0 --port 8000
```

### Endpoints

**`GET /health`** — Health check with KB stats and DB connectivity.

**`POST /search`** — Natural-language search that returns tables, generated SQL, and a natural answer.

```bash
curl -s http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "total sales by region last year"}' | python -m json.tool
```

## Project Structure

```
src/sql_retrieval/
├── __main__.py                   Interactive CLI
├── config.py                     Constants, path resolution, tuning config loader
├── config_schema.py              Pydantic schema for tuning_config.yaml validation
├── server.py                     FastAPI server (/health, /search)
├── metadata/
│   └── loader.py                 YAML knowledge base loader
├── generation/
│   ├── llm_client.py             LLM calls (Ollama + Groq with fallback)
│   ├── prompt.py                 Prompt templates for SQL gen + answer gen
│   └── pipeline.py               Two-stage pipeline: SQL → execute → answer
├── db/
│   └── executor.py               SQL Server query execution with safety validation
└── retrieval/
    ├── bm25.py                   BM25 sparse retrieval
    ├── vector.py                 BGE-M3 dense retrieval via ChromaDB
    ├── reranker.py               BGE Reranker cross-encoder
    └── engine.py                 Main retrieval pipeline

scripts/
├── generate_kb_from_db.py        Generate KB from SQL Server
├── generate_metadata.py          Business metadata definitions
└── merge_metadata.py             Merge business metadata into KB

knowledge_base/
├── tables/                       68 YAML files — one per table
├── columns/                      68 YAML files — one per table
├── joins/                        joins.yaml — 149 FK relationships
├── glossary/                     glossary.yaml — 17 business terms
├── domains/                      domains.yaml — 14 business domains
├── business_rules/               business_rules.yaml — 12 business rules
├── sql_patterns/                 sql_patterns.yaml — 10 SQL pattern templates
├── examples/                     examples.yaml — 10 example query pairs
└── stats/                        stats.yaml — database statistics
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
- fastapi, uvicorn, pydantic (for the API server)
