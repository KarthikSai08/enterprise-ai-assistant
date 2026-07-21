# SQL ChatBot — Semantic Metadata Retrieval & NL2SQL

A **two-stage, retrieval-augmented natural-language to SQL system** for relational business databases. Given a plain-English question, the system retrieves relevant schema (tables, columns, relationships) using hybrid semantic search, generates safe T-SQL via an LLM, executes it, and produces a concise natural-language answer.

---

## Architecture

```
User Query
    │
    ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STAGE 1: SEMANTIC RETRIEVAL                                          │
│                                                                      │
│  Query ──► Typo Correction ──► Glossary Expansion                    │
│                                      │                               │
│                    ┌─────────────────┼─────────────────┐              │
│                    ▼                 ▼                  ▼             │
│              BGE-M3 Dense       BM25 Sparse      Domain Centroids    │
│              (ChromaDB)         (rank_bm25)      (cosine sim)        │
│                    │                 │                  │             │
│                    └─────────┬───────┘                  │             │
│                              ▼                          │             │
│                    Reciprocal Rank Fusion                │             │
│                    (RRF)                                │             │
│                              │                          │             │
│                              ▼                          │             │
│                    Domain-Aware Score Boosting ◄─────────┘             │
│                    + Keyword Scoring                                  │
│                              │                                        │
│                              ▼                                        │
│                    BGE Reranker (Cross-Encoder)                       │
│                              │                                        │
│                              ▼                                        │
│                    Top-K Tables + Columns + Joins                     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│ STAGE 2: LLM SQL GENERATION & EXECUTION                              │
│                                                                      │
│  Retrieved Schema ──► Prompt Builder ──► LLM (Ollama / Groq)         │
│                              │                                       │
│                              ▼                                       │
│                    Generated T-SQL                                   │
│                              │                                       │
│                              ▼                                       │
│                    SQL Validator (SELECT-only, TOP cap)              │
│                              │                                       │
│                              ▼                                       │
│                    pyodbc Execution (SQL Server)                     │
│                              │                                       │
│                              ▼                                       │
│                    Results ──► Answer LLM ──► Natural Text           │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Stage 1: Semantic Retrieval

The retrieval pipeline transforms a raw natural-language query into a ranked list of relevant database tables, columns, and joins using a cascade of complementary techniques:

| Step | Technique | Purpose |
|------|-----------|---------|
| **Typo Correction** | `rapidfuzz.WRatio` against an indexed vocabulary of all table/column/keyword/domain terms | Handles misspellings and partial matches |
| **Glossary Expansion** | Synonym-based term expansion from a curated business glossary | Bridges terminology gaps (e.g., "staff" → "employee") |
| **Dense Retrieval** | `BAAI/bge-m3` embeddings stored in ChromaDB with cosine similarity | Captures semantic meaning beyond keyword overlap |
| **Sparse Retrieval** | BM25Okapi on table description text | Ensures exact keyword matches are never missed |
| **Reciprocal Rank Fusion** | Weighted combination of dense + sparse ranking | Balances precision (sparse) with recall (dense) |
| **Domain Detection** | Cosine similarity against domain centroids + keyword rule matching | Identifies business context (Sales, HR, Finance, etc.) |
| **Domain-Boosted Scoring** | Score floors applied per domain based on table role (primary/support) and domain rank | Ensures domain-relevant tables surface prominently |
| **Keyword Scoring** | Multi-match scoring against table/column keywords with weight factors | Rewards tables with high keyword affinity |
| **Cross-Encoder Reranking** | `BAAI/bge-reranker-v2-m3` for fine-grained relevance scoring | Re-ranks top candidates using a pairwise query-document model |
| **Column Retrieval** | Separate BM25 + dense index per column, fused and reranked | Identifies specific columns relevant to the query |
| **Join Matching** | BFS on the foreign-key graph to find join paths between candidate tables | Enables multi-table query construction |

All tunable parameters (candidate pool sizes, score thresholds, boost factors, weights) live in `tuning_config.yaml` — no code changes required.

### Stage 2: SQL Generation & Execution

The retrieved schema context is assembled into a highly constrained prompt that instructs the LLM to produce safe, correct T-SQL:

1. **Prompt Assembly** — The prompt (`generation/prompt.py:45-177`) enforces 20 strict rules:
   - Only `SELECT` statements — no DDL, DML, admin commands
   - No hallucinated tables, columns, or relationships
   - No sensitive data exposure (GST, PAN, Aadhaar, bank details, passwords, salary)
   - No metadata queries (`INFORMATION_SCHEMA`, `sys.*`)
   - Only use join relationships explicitly present in the retrieved schema
   - Aggregations only on columns marked `aggregatable`
   - Filters only on columns marked `filterable`
   - Proper `TOP (N)` / `DISTINCT TOP (N)` ordering
   - Anti-prompt-injection safeguards
   - If any rule cannot be satisfied → returns `NOT_SUPPORTED`

2. **SQL Generation** — Calls Ollama (local, default) or Groq (cloud). Auto-fallbacks between providers if one fails.

3. **SQL Validation** — Server-side regex checks reject non-SELECT statements. Automatic `TOP (100)` capping if no limit is specified. Fixes `SELECT TOP (N) DISTINCT` → `SELECT DISTINCT TOP (N)`.

4. **Query Execution** — Runs against SQL Server via pyodbc with a 30-second timeout.

5. **Answer Generation** — A second LLM call converts the raw result rows into a fluent natural-language response (3-4 sentences with key facts).

---

## Quick Start

### Prerequisites

- Python ≥ 3.10
- ODBC Driver 17 for SQL Server
- A SQL Server database
- (Optional) [Ollama](https://ollama.com) with a pulled model for local LLM inference

### Installation

```bash
pip install -e .
```

### Configuration

Create a `.env` file in the project root:

```env
# ── Database ──────────────────────────────────────────
DB_SERVER=(localdb)\karthik
DB_NAME=SQLChatBot_DB
DB_TRUSTED=true
DB_SCHEMA=dbo

# ── LLM Provider ──────────────────────────────────────
# Options: "ollama" (default, free/local) or "groq" (cloud API)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Groq (used when LLM_PROVIDER=groq or as fallback if Ollama fails)
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama3-70b-8192
```

### Generate the Knowledge Base

The knowledge base is a set of YAML files that describe every table, column, foreign key relationship, and business domain. It is generated from your live database schema and then enriched with hand-curated business metadata.

```bash
# Step 1: Extract schema from SQL Server
python src/sql_chatbot/scripts/generate.py

# Step 2: Merge business metadata (descriptions, keywords, domains, aliases)
python src/sql_chatbot/scripts/generate.py merge
```

### Run

```bash
# Interactive CLI
python -m sql_chatbot

# API Server
uvicorn sql_chatbot.server:app --host 0.0.0.0 --port 8000
```

---

## Usage

### CLI Commands

| Command | Description |
|---------|-------------|
| `<query>` | Search tables → generate SQL → execute → natural answer |
| `tables`  | List all indexed tables with domains and column counts |
| `help`    | Show available commands |
| `exit`    | Quit |

### Interactive Example

```
[User] >>> show total sales last month

Domains: Sales

  #    Table                    Score    Domain       Columns
  ────────────────────────────────────────────────────────────────────────────────
  1    tbl_SaleInvoiceHeader    0.8921  Sales        invoiceNo, invoiceDate,
                                                     grandTotal, dealerOrgId
  2    tbl_SaleInvoiceDetail    0.7814  Sales        invoiceId, productId,
                                                     quantity, unitPrice

  Joins:
    tbl_SaleInvoiceDetail.invoiceId = tbl_SaleInvoiceHeader.idInvoice
    (line-item details for each invoice)

  Tables: 2 | Columns: invoiceNo, invoiceDate, grandTotal, quantity, unitPrice
  | Latency: 312ms
  Confidence: 0.9428

[Bot] >>> Generating SQL...
  ────────────────────────────────────────────────────────────
  SELECT TOP (100)
      i.invoiceNo,
      i.invoiceDate,
      i.grandTotal,
      d.quantity,
      d.unitPrice
  FROM tbl_SaleInvoiceHeader i
  JOIN tbl_SaleInvoiceDetail d ON d.invoiceId = i.idInvoice
  WHERE i.invoiceDate >= DATEADD(MONTH, -1, GETDATE())
  ────────────────────────────────────────────────────────────

[Bot] >>> Result: 47 row(s)
        [1, 'INV-001', '2026-06-15', 10, 150.00]
        [2, 'INV-002', '2026-06-18', 5, 200.00]
        ...

[Bot] >>> Last month recorded 47 sale invoices totaling ₹2,34,500 across
        18 unique products. The average invoice value was ₹4,989.
```

### API Endpoints

#### `GET /health`

Returns system health, knowledge base statistics, and database connectivity status.

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

```json
{
  "status": "ok",
  "tables": 68,
  "columns": 892,
  "domains": 14,
  "joins": 149,
  "db_connected": true,
  "version": "1.0.0"
}
```

#### `POST /search`

Accepts a natural-language query and returns the full retrieval result plus generated SQL and answer.

```bash
curl -s http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "total sales by region last year"}' | python -m json.tool
```

---

## Project Structure

```
├── src/sql_chatbot/
│   ├── __main__.py                Interactive CLI entry point
│   ├── config.py                  Constants, environment, tuning config loader
│   ├── server.py                  FastAPI application (health + search endpoints)
│   │
│   ├── metadata/
│   │   └── loader.py              YAML knowledge base loader — builds in-memory
│   │                               index of tables, columns, domains, joins, rules
│   │
│   ├── retrieval/
│   │   ├── engine.py              Main retrieval orchestrator — typo correction,
│   │   │                           domain detection, fusion, boosting, ranking
│   │   ├── vector.py              BGE-M3 dense embedding index via ChromaDB
│   │   ├── bm25.py                BM25 sparse retrieval (rank_bm25)
│   │   └── reranker.py            BGE Cross-Encoder reranker
│   │
│   ├── generation/
│   │   ├── prompt.py              Prompt templates — SQL generation (20 rules)
│   │   │                           and answer generation
│   │   ├── llm_client.py          LLM abstraction — Ollama + Groq with fallback
│   │   └── pipeline.py            Two-stage pipeline: generate SQL → execute →
│   │                               generate answer, with auto-retry on failure
│   │
│   ├── db/
│   │   └── executor.py            SQL Server query execution — validation,
│   │                               SELECT-only enforcement, TOP capping
│   │
│   └── intent/
│       └── detector.py            Query intent classification — regex rules
│                                  (COUNT/SUM/AVG/LIST/FILTER) with LLM fallback
│
├── scripts/
│   └── generate.py                Schema extraction from SQL Server +
│                                  business metadata merge utility
│
├── knowledge_base/
│   ├── tables/                    68 YAML files — table-level metadata
│   ├── columns/                   68 YAML files — column-level metadata
│   ├── joins/                     joins.yaml — 149 foreign key relationships
│   ├── domains/                   domains.yaml — 14 business domains
│   ├── glossary/                  glossary.yaml — 17 curated business terms
│   ├── business_rules/            business_rules.yaml — 12 validation rules
│   ├── sql_patterns/              sql_patterns.yaml — 10 reusable SQL templates
│   ├── examples/                  examples.yaml — 10 NL-to-SQL example pairs
│   └── stats/                     stats.yaml — database statistics metadata
│
├── tuning_config.yaml             Retrieval tuning parameters (optional)
├── pyproject.toml                 Python package definition
└── .env                           Environment variables (not committed)
```

---

## Knowledge Base

The knowledge base is the system's brain — a structured representation of your database schema enriched with business context. Each YAML file is curated to bridge the gap between technical column names and business user language.

### Table Metadata (`knowledge_base/tables/`)

Each table YAML includes:
- **Display name** and **description** — user-friendly identifiers
- **Domain** — business area (Sales, Finance, HR, Inventory, etc.)
- **Search keywords** — alternate names and synonyms users might say
- **Common user intents** — examples of questions this table can answer
- **Important columns**, **business metrics**, **common filters**, **group-by columns**
- **Search weight** — relative importance for ranking (1–10)
- **Foreign keys** and **related tables**

### Column Metadata (`knowledge_base/columns/`)

Each column is annotated with:
- **Role** — `identifier`, `foreign_key`, `dimension`, `metric`, `status`, `attribute`
- **Importance** — `high`, `medium`, `low`
- **Aliases** — alternate names users might use (e.g., "firm" → `firmName`)
- **Filterable / Groupable / Aggregatable** flags — control which SQL operations are allowed
- **Aggregations allowed** — `SUM`, `AVG`, `MIN`, `MAX`
- **Sample values** — valid filter values to guide the LLM
- **Search keywords** and **common user intents**

### Domain Model (`knowledge_base/domains/`)

14 business domains, each with:
- **Trigger keywords** — words/phrases that indicate this domain
- **Anti keywords** — terms that should exclude this domain
- **Primary tables** — core tables of this domain
- **Support tables** — auxiliary tables referenced by the domain

### Business Rules (`knowledge_base/business_rules/`)

12 validation rules that the LLM is made aware of during SQL generation (e.g., credit limit checks, stock non-negative, GST compliance).

---

## Tuning

All retrieval parameters are configurable via `tuning_config.yaml`:

```yaml
retrieval:
  top_k: 10                    # Top-N from dense vector search
  rrf_k: 60                    # RRF fusion constant (higher = less BM25 influence)
  score_threshold: 0.001       # Minimum table score to appear in results

domain_boost:
  top_primary: 0.75            # Score floor for top-domain primary tables
  top_non_primary: 0.55        # Score floor for top-domain non-primary tables

score_blending:
  ce_weight: 0.40              # Cross-encoder contribution
  rrf_weight: 0.60             # RRF contribution
```

Changes take effect on the next restart — no code modifications needed.

---

## Safety & Security

The system incorporates multiple layers of protection:

1. **SQL Validation** — Server-side regex blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `EXEC`, `GRANT`, and 15+ other harmful patterns. Transaction and batch separators are prohibited.

2. **Sensitive Data** — Column patterns for mobile numbers, bank accounts, IFSC, GST, PAN, Aadhaar, salary, passwords, tokens, and credit cards are independently checked in both the prompt builder and the SQL validator, even if the retrieval layer returns them incorrectly.

3. **Prompt Hardening** — 20 rules in the generation prompt guard against hallucination, prompt injection, metadata leaks, and unsafe SQL constructs. The LLM cannot generate anything beyond a single `SELECT` statement.

4. **Output Capping** — `TOP (100)` is automatically injected if the generated SQL lacks a limit, preventing accidental full-table scans.

---

## Regeneration

When the database schema changes:

```bash
# Extract updated schema
python src/sql_chatbot/scripts/generate.py

# Re-merge business metadata (preserves curated descriptions)
python src/sql_chatbot/scripts/generate.py merge
```

---

## Testing

Run the golden set of 20 retrieval test cases (single-table, cross-domain, not_supported, and known_failure queries):

```bash
python tests/run_golden_set.py
```

The golden set exercises the full retrieval pipeline — BM25, ChromaDB (BGE-M3), domain boosting, keyword scoring, and BGE reranker — then compares each result against expected table names:

| Type | Description |
|------|-------------|
| `single` | Expects all expected tables in Top-1 |
| `cross-domain` | Expects all expected tables in Top-3 |
| `not_supported` | Expects the query to be rejected (no relevant results) |
| `known_failure` | Queries known to be difficult — tracked for regression but treated as acceptable failures |

Test definitions live in `tests/golden_set.yaml`.

---

## Dependencies

| Category | Packages |
|----------|----------|
| Core | `pyyaml`, `numpy`, `python-dotenv` |
| Embeddings & Search | `FlagEmbedding` (BGE-M3), `chromadb`, `sentence-transformers` (BGE Reranker), `rank_bm25` |
| Fuzzy Matching | `rapidfuzz` |
| Database | `pyodbc` (ODBC Driver 17 for SQL Server) |
| API Server | `fastapi`, `uvicorn`, `pydantic` |
| LLM | `requests` (Ollama API), `groq` (Groq SDK) |
| Python | ≥ 3.10 |

---

## License & Author

Internal project. For questions or contributions, refer to the project maintainers.
