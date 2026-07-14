"""
Load the four YAML files from data/contexts/ and build an enriched,
search-ready dictionary of every table, domain, join path, column synonym,
and evaluation query.
"""

from pathlib import Path

import yaml

from sql_retrieval.config import CONTEXTS_DIR, DATA_DIR

# The four YAML files that make up the knowledge base
YAML_FILES = [
    "metadata.yaml",       # 69 tables with columns, data types, descriptions
    "context.yaml",        # Business synonyms, glossary, sample questions
    "domain_catalog.yaml", # Domain definitions (trigger/anti keywords, table membership)
    "joins.yaml",          # ~80 join paths between tables
]


def _load_yaml(name):
    """Load a single YAML file from the contexts directory."""
    path = CONTEXTS_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Context file not found: {path}")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def build():
    """
    Main entry point. Returns five objects:
      tables  – dict of {table_name: {name, purpose, domain, columns, keywords, text, ...}}
      domains – dict of {domain_name: {primary/support tables, trigger/anti keywords}}
      joins   – list of {from, to, on, meaning}
      col_syns_flat – dict of {"table.column": [synonyms]}
      eval_q  – list of 120 evaluation queries with ground truth
    """

    # ── Load all four YAML files ─────────────────────────────────────

    meta = _load_yaml("metadata.yaml")
    ctx_raw = _load_yaml("context.yaml")
    dcat = _load_yaml("domain_catalog.yaml")

    # ── Extract sub-sections from context.yaml ───────────────────────

    ctx = ctx_raw.get("context", {}) if isinstance(ctx_raw, dict) else {}
    table_synonyms = ctx.get("table_synonyms", {})  # user-facing table aliases
    col_syns_data = ctx.get("column_synonyms", {})   # user-facing column aliases
    gloss_data = ctx.get("glossary", {})              # business term definitions
    queries_data = ctx.get("sample_queries", [])      # example questions per table

    # ── Build enriched table metadata ────────────────────────────────

    tables = {}

    for tn, td in meta.get("tables", {}).items():
        # Each column gets a dict with name, type, description, label, etc.
        cols = [
            {
                "name": c,
                "type": cinfo.get("data_type", ""),
                "desc": cinfo.get("description", ""),
                "label": cinfo.get("business_label", ""),
                "filter": cinfo.get("is_filter", False),
                "agg": cinfo.get("is_aggregation", False),
                "ref": cinfo.get("references"),
            }
            for c, cinfo in td.get("columns", {}).items()
        ]

        # Collect keywords for this table from multiple sources
        kw = []

        # 1. Table-level synonyms from context.yaml
        if tn in table_synonyms:
            kw.extend(table_synonyms[tn].get("synonyms", []))

        # 2. Column synonyms like "Invoice No" for tbl_SaleInvoiceHeader.invoiceNo
        for c in cols:
            ck = f"{tn}.{c['name']}"
            if ck in col_syns_data:
                col_syns = col_syns_data[ck]
                kw.extend(col_syns if isinstance(col_syns, list) else [])
            if c["label"]:
                kw.append(c["label"])

        # 3. Sample questions that mention this table
        sample_questions = [
            q.get("question", "")
            for q in queries_data
            if tn in q.get("tables_required", [])
        ]

        # 4. Glossary definitions tied to this table
        glossary_terms = []
        for _, gd in gloss_data.items():
            mt = gd.get("table", "")
            if (isinstance(mt, list) and tn in mt) or mt == tn:
                glossary_terms.append(gd.get("definition", ""))

        # 5. Domain-level trigger keywords (e.g., "sale" for the sales domain)
        domain_keywords = []
        for _, dd in dcat.get("domains", {}).items():
            if tn in dd.get("primary_tables", []) + dd.get("support_tables", []):
                domain_keywords.extend(dd.get("trigger_keywords", []))

        all_keywords = list(set(k.lower() for k in kw if k))

        # Build a rich text representation that both BM25 and the vector
        # model will search against
        text = (
            f"Table: {tn}\n"
            f"Purpose: {td.get('purpose', '')}\n"
            f"Domain: {td.get('domain', '')}\n"
            + (f"Keywords: {', '.join(all_keywords)}\n" if all_keywords else "")
            + (f"DomainKW: {', '.join(domain_keywords)}\n" if domain_keywords else "")
            + (f"Questions: {' | '.join(sample_questions)}\n" if sample_questions else "")
            + (f"Glossary: {' | '.join(glossary_terms)}\n" if glossary_terms else "")
            + "\n".join(
                f"Col: {c['name']} - {c['desc']} - {c['label']}" for c in cols
            )
        )

        tables[tn] = {
            "name": tn,
            "purpose": td.get("purpose", ""),
            "domain": td.get("domain", ""),
            "priority": td.get("priority", 3),
            "columns": cols,
            "filters": td.get("filters", []),
            "agg_cols": td.get("aggregation_columns", []),
            "keywords": all_keywords,
            "text": text,  # ← the searchable text for BM25 + vector model
        }

    # ── Build domain index ───────────────────────────────────────────

    domains = {}
    for dn, dd in dcat.get("domains", {}).items():
        domains[dn] = {
            "primary": dd.get("primary_tables", []),  # core tables for this domain
            "support": dd.get("support_tables", []),   # auxiliary tables
            "trigger": [k.lower() for k in dd.get("trigger_keywords", [])],
            "anti": [k.lower() for k in dd.get("anti_keywords", [])],
        }

    # ── Build join index ─────────────────────────────────────────────

    joins = [
        {
            "from": j["from_table"],
            "to": j["to_table"],
            "on": j["on_clause"],
            "meaning": j.get("business_meaning", "").lower(),
        }
        for j in _load_yaml("joins.yaml").get("joins", [])
    ]

    # ── Flatten column synonyms ──────────────────────────────────────

    col_syns_flat = {}
    for k, v in col_syns_data.items():
        if isinstance(v, list):
            col_syns_flat[k] = v
        elif isinstance(v, dict):
            col_syns_flat[k] = v.get("synonyms", [])

    # ── Load evaluation queries ──────────────────────────────────────

    eval_path = DATA_DIR / "evaluation_queries.yaml"
    eval_q = []
    if eval_path.exists():
        with open(eval_path, encoding="utf-8") as f:
            eval_q = yaml.safe_load(f).get("queries", [])

    return tables, domains, joins, col_syns_flat, eval_q
