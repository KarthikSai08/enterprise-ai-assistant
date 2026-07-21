from pathlib import Path
import yaml

from sql_chatbot.config import (
    TABLES_DIR, COLUMNS_DIR, JOINS_DIR, GLOSSARY_DIR,
    DOMAINS_DIR, BUSINESS_RULES_DIR, SQL_PATTERNS_DIR,
    EXAMPLES_DIR, STATS_DIR,
)


def _load_yaml(filepath: Path) -> dict:
    if not filepath.exists():
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _build_column_list(col_data: dict) -> list[dict]:
    cols = []
    for c in col_data.get("columns", []):
        cols.append({
            "name": c.get("name", ""),
            "display_name": c.get("display_name", ""),
            "datatype": c.get("datatype", ""),
            "description": c.get("description", ""),
            "aliases": c.get("aliases", []),
            "role": c.get("role", ""),
            "importance": c.get("importance", "medium"),
            "nullable": c.get("nullable", True),
            "is_primary_key": c.get("is_primary_key", False),
            "is_join_key": c.get("is_join_key", False),
            "filterable": c.get("filterable", False),
            "groupable": c.get("groupable", False),
            "aggregatable": c.get("aggregatable", False),
            "aggregations_allowed": c.get("aggregations_allowed", []),
            "sample_values": c.get("sample_values", []),
            "search_keywords": c.get("search_keywords", []),
            "common_user_intents": c.get("common_user_intents", []),
        })
    return cols


def _merge_table_and_columns(table_data: dict, col_data: dict) -> dict:
    cols = _build_column_list(col_data) if col_data else []

    table_name = table_data.get("table_name", "")
    display_name = table_data.get("display_name", "")
    description = table_data.get("description", "")
    search_keywords = table_data.get("search_keywords", [])
    common_intents = table_data.get("common_user_intents", [])
    module = table_data.get("module", "")
    business_metrics = table_data.get("business_metrics", [])
    common_filters = table_data.get("common_filters", [])
    common_groupby = table_data.get("common_groupby", [])

    parts = [
        f"Table: {table_name}",
        f"Display: {display_name}" if display_name else "",
        f"Description: {description}" if description else "",
        f"Domain: {table_data.get('domain', '')}" if table_data.get("domain") else "",
        f"Module: {module}" if module else "",
        f"Keywords: {', '.join(search_keywords)}" if search_keywords else "",
        f"Intents: {' | '.join(common_intents)}" if common_intents else "",
        f"Metrics: {', '.join(business_metrics)}" if business_metrics else "",
        f"Filters: {', '.join(common_filters)}" if common_filters else "",
        f"GroupBy: {', '.join(common_groupby)}" if common_groupby else "",
    ]

    for c in cols:
        col_line = f"Column: {c['name']}"
        if c["display_name"]:
            col_line += f" ({c['display_name']})"
        col_line += f" - {c['datatype']}"
        if c["description"]:
            col_line += f" - {c['description']}"
        if c["aliases"]:
            col_line += f" [aliases: {', '.join(c['aliases'])}]"
        if c["role"]:
            col_line += f" [role: {c['role']}]"
        col_line += f" [importance: {c['importance']}]"
        if c.get("search_keywords"):
            col_line += f" [col_keywords: {', '.join(c['search_keywords'])}]"
        if c.get("sample_values"):
            col_line += f" [values: {', '.join(str(v) for v in c['sample_values'][:4])}]"
        parts.append(col_line)

    all_keywords = list(set(k.lower() for k in search_keywords if k))
    for c in cols:
        all_keywords.append(c["display_name"].lower())
        for alias in c["aliases"]:
            all_keywords.append(alias.lower())

    text = "\n".join(p for p in parts if p)

    return {
        "name": table_name,
        "display_name": display_name,
        "description": description,
        "domain": table_data.get("domain", ""),
        "module": table_data.get("module", ""),
        "priority": table_data.get("priority", "Medium"),
        "search_weight": table_data.get("search_weight", 5),
        "estimated_rows": table_data.get("estimated_rows", 0),
        "primary_key": table_data.get("primary_key", ""),
        "foreign_keys": table_data.get("foreign_keys", []),
        "related_tables": table_data.get("related_tables", []),
        "common_user_intents": common_intents,
        "search_keywords": search_keywords,
        "important_columns": table_data.get("important_columns", []),
        "business_metrics": table_data.get("business_metrics", []),
        "common_filters": table_data.get("common_filters", []),
        "common_groupby": table_data.get("common_groupby", []),
        "columns": cols,
        "keywords": all_keywords,
        "text": text,
    }


def load_all_tables() -> dict[str, dict]:
    tables = {}
    for f in TABLES_DIR.glob("*.yaml"):
        table_data = _load_yaml(f)
        if not table_data:
            continue
        table_name = table_data.get("table_name", f.stem)
        col_path = COLUMNS_DIR / f.name
        col_data = _load_yaml(col_path)
        tables[table_name] = _merge_table_and_columns(table_data, col_data)
    return tables


def load_joins() -> list[dict]:
    data = _load_yaml(JOINS_DIR / "joins.yaml")
    return [
        {
            "from": j.get("from_table", j.get("from", "")),
            "to": j.get("to_table", j.get("to", "")),
            "on": j.get("on_clause", j.get("on", "")),
            "meaning": j.get("business_meaning", j.get("meaning", "")).lower(),
            "join_type": j.get("default_join_type", j.get("join_type", "INNER")),
        }
        for j in data.get("joins", [])
    ]


def load_glossary() -> dict[str, dict]:
    data = _load_yaml(GLOSSARY_DIR / "glossary.yaml")
    terms = data.get("terms", {})
    if not terms and isinstance(data, dict):
        terms = data
    return terms


def load_all_domains() -> dict[str, dict]:
    domains = {}
    for f in DOMAINS_DIR.glob("*.yaml"):
        data = _load_yaml(f)
        if not data:
            continue
        items = data.get("domains", [data])
        for item in items:
            domain_name = item.get("domain", f.stem)
            raw_trigger = item.get("trigger_keywords", [])
            flattened = []
            for kw in raw_trigger:
                if isinstance(kw, str):
                    for part in kw.split(","):
                        part = part.strip()
                        if part:
                            flattened.append(part)
                else:
                    flattened.append(str(kw))
            raw_anti = item.get("anti_keywords", [])
            anti_flat = []
            for kw in raw_anti:
                if isinstance(kw, str):
                    for part in kw.split(","):
                        part = part.strip()
                        if part:
                            anti_flat.append(part)
                else:
                    anti_flat.append(str(kw))
            domains[domain_name] = {
                "primary": item.get("primary_tables", []),
                "support": item.get("support_tables", []),
                "trigger": [k.lower() for k in flattened],
                "anti": [k.lower() for k in anti_flat],
                "description": item.get("description", ""),
            }
    return domains


def load_all_business_rules() -> list[dict]:
    rules = []
    for f in BUSINESS_RULES_DIR.glob("*.yaml"):
        data = _load_yaml(f)
        rules.extend(data.get("rules", []))
    return rules


def load_all_sql_patterns() -> dict[str, list]:
    patterns = {}
    for f in SQL_PATTERNS_DIR.glob("*.yaml"):
        data = _load_yaml(f)
        patterns[f.stem] = data.get("patterns", [])
    return patterns


def load_examples() -> list[dict]:
    data = _load_yaml(EXAMPLES_DIR / "examples.yaml")
    return data.get("examples", [])


def load_stats() -> dict:
    return _load_yaml(STATS_DIR / "stats.yaml")


def build():
    tables = load_all_tables()
    joins = load_joins()
    glossary = load_glossary()
    domains = load_all_domains()
    rules = load_all_business_rules()
    patterns = load_all_sql_patterns()
    examples = load_examples()
    stats = load_stats()

    col_syns = {}
    column_texts: dict[str, str] = {}
    for table_name, t in tables.items():
        for c in t.get("columns", []):
            if c["aliases"]:
                col_syns[f"{table_name}.{c['name']}"] = c["aliases"]

            parts = [
                f"Table: {table_name}",
                f"Column: {c['name']}",
            ]
            if c["display_name"]:
                parts.append(f"Display: {c['display_name']}")
            parts.append(f"Type: {c['datatype']}")
            if c["description"]:
                parts.append(f"Description: {c['description']}")
            if c["aliases"]:
                parts.append(f"Aliases: {', '.join(c['aliases'])}")
            if c["sample_values"]:
                parts.append(f"Values: {', '.join(str(v) for v in c['sample_values'][:5])}")
            if c["role"]:
                parts.append(f"Role: {c['role']}")
            parts.append(f"Importance: {c['importance']}")
            if c.get("search_keywords"):
                parts.append(f"Keywords: {', '.join(c['search_keywords'])}")
            if c.get("common_user_intents"):
                parts.append(f"Intents: {' | '.join(c['common_user_intents'])}")
            key = f"{table_name}.{c['name']}"
            column_texts[key] = " - ".join(parts)

    return {
        "tables": tables,
        "domains": domains,
        "joins": joins,
        "col_syns": col_syns,
        "glossary": glossary,
        "rules": rules,
        "patterns": patterns,
        "examples": examples,
        "stats": stats,
        "column_texts": column_texts,
    }
