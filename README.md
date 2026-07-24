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
| **Keyword Scoring** | Multi-match scoring against table/column keywords + sample values with weight factors | Rewards tables with high keyword or known-value affinity |
| **Cross-Encoder Reranking** | `BAAI/bge-reranker-v2-m3` for fine-grained relevance scoring | Re-ranks top candidates using a pairwise query-document model |
| **Column Retrieval** | Separate BM25 + dense index per column, fused and reranked | Identifies specific columns relevant to the query |
| **Join Matching** | BFS on the foreign-key graph to find join paths between candidate tables | Enables multi-table query construction |

All tunable parameters (candidate pool sizes, score thresholds, boost factors, weights) live in `src/sql_chatbot/config.py` — no code changes required for retrieval tuning.

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

2. **SQL Generation** — Calls Groq (cloud API, default) or Ollama (local). Auto-fallbacks between providers if one fails. Configure via `LLM_PROVIDER` in `.env`.

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

Copy `.env.example` from the project root to `.env` and fill in your settings:

```bash
cp .env.example .env
# Then edit .env with your DB_SERVER, DB_NAME, and GROQ_API_KEY
```

Supported environment variables:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DB_SERVER` | Yes | — | SQL Server host/instance |
| `DB_NAME` | Yes | — | Database name |
| `DB_USE_WINDOWS_AUTH` | No | `true` | Use Windows Authentication (falls back to `DB_TRUSTED` for backward compat) |
| `DB_USER` | No | — | SQL Auth username (if DB_TRUSTED=false) |
| `DB_PASS` | No | — | SQL Auth password |
| `DB_SCHEMA` | No | `dbo` | Database schema to extract |
| `LLM_PROVIDER` | No | `groq` | `groq` or `ollama` |
| `GROQ_API_KEY` | Yes* | — | Groq API key (required if LLM_PROVIDER=groq) |
| `GROQ_MODEL` | No | `llama-3.1-8b-instant` | Groq model name |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `qwen2.5-coder:7b` | Ollama model name |

### Generate the Knowledge Base

The knowledge base is a set of YAML files that describe every table, column, foreign key relationship, and business domain. It is generated from two sources:

1. **Live database schema** — extracted automatically from SQL Server
2. **Hand-curated business metadata** — defined in `src/sql_chatbot/scripts/metadata_data.py` (table descriptions, search keywords, column aliases, domain mappings)
3. **Bootstrap data** — domains, glossary, examples, business rules, and SQL patterns defined in `src/sql_chatbot/scripts/kb_bootstrap_data.py`

```bash
# Full rebuild: extract from DB → merge metadata → write bootstrap files
python -m sql_chatbot.scripts.generate full-rebuild

# Or run individual steps:
# Step 1: Extract schema from SQL Server (run when DB schema changes)
python -m sql_chatbot.scripts.generate

# Step 2: Merge business metadata with extracted schema (run after editing metadata_data.py)
python -m sql_chatbot.scripts.generate merge

# Step 3: Write bootstrap files (domains, glossary, examples, etc.)
python -m sql_chatbot.scripts.generate bootstrap
```

> **Note:** The `merge` command reads `TABLE_META` and `COLUMN_META` from `metadata_data.py` and overwrites all YAML files in `knowledge_base/`. Hand-edits to YAML files will be lost on next merge — always edit `metadata_data.py` instead.

#### Auto-fill Behavior

The `merge` command automatically fills empty metadata fields for any column not explicitly listed in `COLUMN_META`:

| Field | Auto-fill logic |
|-------|----------------|
| `aliases` | Derived from camelCase/PascalCase split of column name |
| `aggregations_allowed` | Set to `SUM, AVG, MIN, MAX` for numeric columns; empty for FK/identifier/status columns |
| `sample_values` | Inferred from column name patterns (e.g., `gender` → `["Male", "Female"]`, `maritalStatus` → `["Married", "Unmarried", "Divorced"]`) |
| `search_keywords` | Generated from column name words and aliases |
| `common_user_intents` | Generated based on inferred role (dimension → filter/group queries, metric → aggregation queries) |
| `role` | Inferred from column name patterns when no explicit role is set (e.g., columns containing "name"/"date"/"address" → dimension, "amount"/"total"/"qty" → metric) |

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
| `exit`    | Quit 

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

### Example Queries

#### 3-Table Joins

```
[User] >>> show sale orders with product names and customer details

Domains: Sales

  #    Table                    Score    Domain       Columns
  ────────────────────────────────────────────────────────────────────────────────
  1    tbl_SaleOrder            0.9124  Sales        orderNo, orderDate,
                                                     totalAmount, organizationId
  2    tbl_SaleOrderDetail      0.8731  Sales        orderId, productId,
                                                     quantity, unitPrice
  3    tbl_ProductMaster        0.6512  Sales        productCode, productName,
                                                     categoryId
  4    tbl_Organization         0.5823  Sales        firmName, cityId, creditLimit

  Joins:
    tbl_SaleOrderDetail.orderId = tbl_SaleOrder.idSaleOrder
    tbl_SaleOrderDetail.productId = tbl_ProductMaster.idProduct
    tbl_SaleOrder.organizationId = tbl_Organization.idOrganization

  Tables: 4 | Columns: orderNo, orderDate, totalAmount, productName, quantity,
  unitPrice, firmName
```

```
[User] >>> invoices with product categories and tax breakdown

Domains: Sales

  #    Table                    Score    Domain       Columns
  ────────────────────────────────────────────────────────────────────────────────
  1    tbl_SaleInvoiceHeader    0.9341  Sales        invoiceNo, invoiceDate,
                                                     grandTotal, taxableAmount
  2    tbl_SaleInvoiceDetail    0.8012  Sales        invoiceId, productId,
                                                     quantity, unitPrice
  3    tbl_ProductMaster        0.6123  Sales        productCode, productName,
                                                     categoryId
  4    tbl_ProductCategory      0.4512  Sales        categoryName, categoryCode

  Joins:
    tbl_SaleInvoiceDetail.invoiceId = tbl_SaleInvoiceHeader.idInvoice
    tbl_SaleInvoiceDetail.productId = tbl_ProductMaster.idProduct
    tbl_ProductMaster.categoryId = tbl_ProductCategory.idProductCategory

  Tables: 4 | Columns: invoiceNo, grandTotal, categoryName, productName,
  quantity, unitPrice
```

```
[User] >>> purchase orders with supplier info and delivery status

Domains: Purchase

  #    Table                    Score    Domain       Columns
  ────────────────────────────────────────────────────────────────────────────────
  1    tbl_PurchaseOrder        0.8912  Purchase     poNo, poDate, totalAmount,
                                                     vendorId, deliveryDate
  2    tbl_Organization         0.7431  Purchase     firmName, cityId, contactPerson
  3    tbl_PurchaseSchedule     0.6124  Purchase     poId, productId, quantity,
                                                     unitRate, deliveryDate
  4    tbl_ProductMaster        0.4823  Purchase     productCode, productName

  Joins:
    tbl_PurchaseOrder.vendorId = tbl_Organization.idOrganization
    tbl_PurchaseSchedule.poId = tbl_PurchaseOrder.idPurchaseOrder
    tbl_PurchaseSchedule.productId = tbl_ProductMaster.idProduct

  Tables: 4 | Columns: poNo, poDate, totalAmount, firmName, productName,
  quantity, unitRate, deliveryDate
```

#### 2-Table Joins

```
[User] >>> total sales by product

Domains: Sales

  #    Table                    Score    Domain       Columns
  ────────────────────────────────────────────────────────────────────────────────
  1    tbl_SaleInvoiceHeader    0.9102  Sales        invoiceNo, invoiceDate,
                                                     grandTotal
  2    tbl_SaleInvoiceDetail    0.8543  Sales        invoiceId, productId,
                                                     quantity, unitPrice

  Joins:
    tbl_SaleInvoiceDetail.invoiceId = tbl_SaleInvoiceHeader.idInvoice

  Tables: 2 | Columns: invoiceNo, grandTotal, quantity, unitPrice
```

```
[User] >>> employee attendance with department name

Domains: HR

  #    Table                    Score    Domain       Columns
  ────────────────────────────────────────────────────────────────────────────────
  1    tbl_Employee             0.9231  HR           employeeCode, employeeName,
                                                     departmentId, designationId
  2    tbl_Attendance           0.7842  HR           employeeId, attendanceDate,
                                                     status
  3    tbl_Department           0.5612  HR           departmentName, departmentCode

  Joins:
    tbl_Attendance.employeeId = tbl_Employee.idEmployee
    tbl_Employee.departmentId = tbl_Department.idDepartment

  Tables: 3 | Columns: employeeName, departmentName, attendanceDate, status
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
│   ├── scripts/
│   │   ├── generate.py            Schema extraction + business metadata merge
│   │   └── metadata_data.py       Hand-curated TABLE_META & COLUMN_META
│   │                              (descriptions, keywords, aliases, domains)
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
├── pyproject.toml                 Python package definition
└── .env                           Environment variables (not committed)
```

---

## Knowledge Base

The knowledge base is the system's brain — a structured representation of your database schema enriched with business context. Each YAML file is curated to bridge the gap between technical column names and business user language.

### Metadata Source: `metadata_data.py`

The hand-curated business metadata lives in **`src/sql_chatbot/scripts/metadata_data.py`**, not in the YAML files directly. This file defines:

- **`TABLE_META`** — dict with per-table: display name, description, domain, search keywords, common user intents, important columns, business metrics, common filters, common group-by columns, search weight, and priority.
- **`COLUMN_META`** — dict keyed by `(table, column)` with: description, role (`identifier`, `foreign_key`, `dimension`, `metric`, `status`, `attribute`), importance, aliases, and sample values.
- **`ACTIVE_ALIASES`** — shared alias map for all `isActive` columns.

**Workflow:** Edit `metadata_data.py` → run `python -m sql_chatbot.scripts.generate merge` → restart the server. Never edit YAML files directly — they are overwritten by the merge command.

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
- **Sample values** — valid filter values to guide the LLM; also used in domain boosting and keyword scoring to match user queries against known values (e.g., "ahmedabad" matches `dmn_City.cityName` sample values)
- **Search keywords** and **common user intents**

> **Note on Filterable:** Columns with `role: metric` are automatically set as both aggregatable and filterable. This allows queries like "totalAmount greater than 10000" to use comparison operators on financial columns.

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

All retrieval parameters are configurable in `src/sql_chatbot/config.py`:

| Constant | Default | Description |
|----------|---------|-------------|
| `TOP_K` | 10 | Top-N results from dense + sparse fusion |
| `RRF_K` | 60 | RRF fusion constant (higher = less BM25 influence) |
| `COLUMN_RRF_K` | 60 | RRF constant for column-level retrieval |
| `COLUMN_TOP_K` | 15 | Top-N columns per candidate table |
| `SCORE_THRESHOLD` | 0.001 | Minimum table score to appear in results |
| `KEYWORD_SCORE_THRESHOLD` | 0.0001 | Minimum score for keyword-only matches |
| `SCORE_GAP_FACTOR` | 0.3 | Relative gap below top score to exclude candidates |
| `CANDIDATE_POOL_MULTIPLIER` | 5 | Pool multiplier for dense retrieval (× TOP_K) |
| `CANDIDATE_POOL_MIN` | 30 | Minimum candidate pool size |
| `RRF_K_MULTIPLIER` | 2 | Column RRF-K multiplier (× pool size) |
| `RRF_K_MIN` | 3 | Minimum column RRF-K |
| `RERANKER_K_MULTIPLIER` | 1 | Reranker pool multiplier |
| `RERANKER_K_MIN` | 2 | Minimum reranker pool size |
| `DOMAIN_SIM_MIN_ABS` | 0.20 | Minimum cosine similarity for domain match |
| `DOMAIN_SIM_GAP` | 0.08 | Gap threshold for domain rank tie-breaking |
| `DOMAIN_FILE_FALLBACK_FLOOR` | 0.15 | Minimum score when no domain file match |
| `CE_WEIGHT` | 0.40 | Cross-encoder (reranker) contribution weight |
| `RRF_WEIGHT` | 0.60 | RRF (dense + sparse) contribution weight |
| `DOMAIN_BOOST_TOP_PRIMARY` | 0.75 | Score floor for top-domain primary tables |
| `DOMAIN_BOOST_TOP_NON_PRIMARY` | 0.55 | Score floor for top-domain non-primary tables |
| `DOMAIN_BOOST_OTHER_PRIMARY` | 0.50 | Score floor for other-domain primary tables |
| `DOMAIN_BOOST_OTHER_NON_PRIMARY` | 0.40 | Score floor for other-domain non-primary tables |
| `DOMAIN_BOOST_EXISTING_FLOOR` | 0.85 | Min score boost if domain already in results |
| `DOMAIN_BOOST_NEW_FLOOR` | 0.65 | Min score boost for newly added domain tables |
| `KEYWORD_SCORE_PER_MATCH` | 1.00 | Score added per keyword/value match |
| `KEYWORD_NULL_TABLE_BASE` | 0.01 | Base score when a keyword match has no table context |

Changes take effect on the next server restart.

---

## Safety & Security

The system incorporates multiple layers of protection:

1. **Prompt-Level Guardrails** — 20 strict rules in the generation prompt (`generation/prompt.py`) enforce: SELECT-only, no hallucinated tables/columns, no sensitive data exposure, only use join relationships defined in the context, only filter on `filterable` columns, only aggregate on `aggregatable` columns, and anti-prompt-injection. If any rule cannot be satisfied, the LLM returns `NOT_SUPPORTED`.

2. **SQL Execution Validation** — Server-side regex in `db/executor.py` blocks `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `EXEC`, `GRANT`, and 15+ other harmful patterns. Transaction and batch separators are prohibited.

3. **Sensitive Data** — Column patterns for mobile numbers, bank accounts, IFSC, GST, PAN, Aadhaar, salary, passwords, tokens, and credit cards are independently checked in both the prompt builder and the executor, even if the retrieval layer returns them incorrectly.

4. **Output Capping** — `TOP (100)` is automatically injected if the generated SQL lacks a limit, preventing accidental full-table scans.

---

## Regeneration

When either the database schema or business metadata changes:

```bash
# Full rebuild (schema + metadata + bootstrap files):
python -m sql_chatbot.scripts.generate full-rebuild

# Or individual steps:
python -m sql_chatbot.scripts.generate              # Step 1: Extract from DB
python -m sql_chatbot.scripts.generate merge          # Step 2: Merge business metadata
python -m sql_chatbot.scripts.generate bootstrap      # Step 3: Write bootstrap files
```

> **Note:** If the database is unavailable, run `merge` and `bootstrap` separately — they only depend on existing YAML files and the Python metadata sources.

> **Important:** After regenerating the knowledge base, **restart the server** for the changes to take effect:
> ```bash
> # Kill the running server, then start again
> uvicorn sql_chatbot.server:app --host 0.0.0.0 --port 8000
> ```
> The YAML files on disk are updated immediately, but the running server holds an in-memory cache built at startup.

---

## Testing & Benchmark

The project includes a golden-set benchmark that evaluates retrieval accuracy across 40 test cases covering all query types.

### Quick Start

```bash
# Full benchmark (all 40 queries) — takes ~3-5 minutes
python tests/run_golden_set.py

# Quick smoke test (1 query per type) — takes ~1 minute
python tests/run_golden_set.py --quick

# Verbose mode (show per-query details)
python tests/run_golden_set.py --verbose
```

### Test Categories

| Type | Count | Description |
|------|-------|-------------|
| `single` | 10 | Single-table queries (list, count, show) — expects recall ≥ 0.5 |
| `two_table` | 8 | 2-join table pairs — verifies join graph bridges related tables |
| `three_plus` | 8 | 3+ table join chains — validates multi-hop bridge table expansion |
| `cross_domain` | 5 | Cross-domain queries (e.g. Sales + Geography) — tests domain detector fusion |
| `not_supported` | 5 | Out-of-scope queries (weather, jokes, DDL) — expects `has_context: false` |
| `edge_case` | 4 | Edge cases (inactive products, cities in state, etc.) — boundary behavior |

### Benchmark Output

```
================================================================================
  SQL ChatBot — Golden Set Benchmark Report
================================================================================
  Date:       2026-07-24 14:57:51
  Total:      40
  Passed:     34
  Failed:     6
  Pass Rate:  85.0%

  Type            Total    Passed   Rate     Avg Latency  Avg Recall
  ------------------------------------------------------------------
  cross_domain    5        3        60.0%   22150.0ms    0.712
  edge_case       4        4        100.0%  18750.0ms    0.875
  not_supported   5        4        80.0%   10150.0ms    1.000
  single          10       10       100.0%  19500.0ms    1.000
  three_plus      8        7        87.5%   22300.0ms    0.812
  two_table       8        6        75.0%   16450.0ms    0.688

  Overall Avg Latency:   18500.0 ms
  Overall Avg Recall:    0.847
  Overall Avg Precision: 0.415
================================================================================
```

*Note: Latency includes embedding inference on CPU. Actual per-query latency after warmup is ~5-15s.*

### Adding Test Cases

Edit `tests/golden_set.yaml` and add a new entry:

```yaml
- query: "your natural language query here"
  type: single            # or two_table | three_plus | cross_domain | not_supported | edge_case
  domain: [Sales]         # expected business domain(s)
  expect:
    has_context: true
    expected_tables: [tbl_ExpectedTable1, tbl_ExpectedTable2]
```

Then re-run the benchmark to validate.

### How Scoring Works

Each query is run through the full retrieval pipeline. The test computes:

- **Recall** — fraction of expected tables found in retrieved results
- **Precision** — fraction of retrieved tables that are among expected tables
- **Pass condition** — `has_context == True` AND recall ≥ 0.5 (for context-expected queries)
- **Not-supported pass** — `has_context == False` (for out-of-scope queries)

Exit code is non-zero if any test fails, making it suitable for CI pipelines.

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
