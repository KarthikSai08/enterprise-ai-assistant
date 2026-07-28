import os
import re
from collections import defaultdict
from pathlib import Path

import yaml
from dotenv import load_dotenv

from metadata_data import TABLE_META, COLUMN_META as _RAW_COLUMN_META, ACTIVE_ALIASES
from kb_bootstrap_data import (
    DOMAINS_DATA, GLOSSARY_DATA, EXAMPLES_DATA,
    BUSINESS_RULES_DATA, SQL_PATTERNS_DATA, STATS_DATA,
)
from terms_data import TERMS_DATA

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

SERVER = os.getenv("DB_SERVER", "")
DATABASE = os.getenv("DB_NAME", "")
USER = os.getenv("DB_USER", "")
PASSWORD = os.getenv("DB_PASS", "")
TRUSTED = os.getenv("DB_TRUSTED", "true").lower() in ("true", "1", "yes")
SCHEMA = os.getenv("DB_SCHEMA", "dbo")

BASE = Path(__file__).resolve().parent.parent / "knowledge_base"

COLUMN_META = dict(_RAW_COLUMN_META)

for tbl in TABLE_META:
    COLUMN_META.setdefault((tbl, "isActive"), ACTIVE_ALIASES)

for tbl in ["tbl_Booking", "tbl_CreditDebitNote", "tbl_OrgAddress", "tbl_OrgBankDetail",
            "tbl_OrgContact", "tbl_OrgRegistration", "tbl_PaymentMade", "tbl_PaymentReceived",
            "tbl_PurchaseEnquiry", "tbl_PurchaseInvoice", "tbl_PurchaseOrder",
            "tbl_SaleOrder", "tbl_SaleReturn", "tbl_TDSDeduction", "tbl_VendorEvaluation"]:
    COLUMN_META.setdefault((tbl, "organizationId"), {
        "description": "Reference to the organization/party", "role": "foreign_key", "importance": "high",
        "aliases": ["org", "party", "customer", "vendor", "dealer"],
    })

for tbl in ["tbl_Attendance", "tbl_LeaveApplication", "tbl_PayrollDetail", "tbl_PayrollHeader"]:
    COLUMN_META.setdefault((tbl, "employeeId"), {
        "description": "Reference to the employee", "role": "foreign_key", "importance": "high",
        "aliases": ["employee", "emp"],
    })

for tbl in ["tbl_GlobalPurchaseRate", "tbl_InventoryAdjustment", "tbl_LoadingDetail",
            "tbl_PhysicalInventory", "tbl_ProductPricing", "tbl_PurchaseSchedule",
            "tbl_QualityChecklist", "tbl_QualityTestResult", "tbl_RateApproval",
            "tbl_RateBand", "tbl_SaleInvoiceDetail", "tbl_SaleOrderDetail",
            "tbl_StockLedger", "tbl_StockTransfer"]:
    COLUMN_META.setdefault((tbl, "productId"), {
        "description": "Reference to the product", "role": "foreign_key", "importance": "high",
        "aliases": ["product", "item", "material"],
    })

for tbl in ["tbl_Employee"]:
    COLUMN_META.setdefault((tbl, "departmentId"), {
        "description": "Reference to the department", "role": "foreign_key", "importance": "high",
        "aliases": ["department", "dept"],
    })
    COLUMN_META.setdefault((tbl, "designationId"), {
        "description": "Reference to the job designation/title", "role": "foreign_key", "importance": "high",
        "aliases": ["designation", "job title", "role"],
    })

for tbl in TABLE_META:
    imp = TABLE_META[tbl].get("important_columns", [])
    if "statusId" in imp:
        COLUMN_META.setdefault((tbl, "statusId"), {
            "description": "Reference to the status", "role": "foreign_key", "importance": "medium",
            "aliases": ["status"],
        })
    if "status" in imp:
        COLUMN_META.setdefault((tbl, "status"), {
            "description": "Record status or state", "role": "dimension", "importance": "high",
            "aliases": ["status", "record status", "state"],
        })

for col in ["invoiceDate", "orderDate", "bookingDate", "receiptDate", "paymentDate",
            "voucherDate", "returnDate", "enquiryDate", "attendanceDate", "testDate",
            "evaluationDate", "adjustmentDate", "countDate", "transferDate", "tripDate",
            "deliveryDate", "startDate", "endDate", "occurredOn"]:
    COLUMN_META.setdefault(("", col), {
        "description": "Date of the transaction", "role": "dimension", "importance": "high",
        "aliases": [col.replace("Date", " date"), "transaction date"],
    })


QUERY_TABLES = """
SELECT
    t.TABLE_SCHEMA,
    t.TABLE_NAME,
    t.TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES t
WHERE t.TABLE_TYPE = 'BASE TABLE'
    AND t.TABLE_SCHEMA NOT IN ('sys', 'guest', 'INFORMATION_SCHEMA', 'db_owner',
        'db_accessadmin', 'db_securityadmin', 'db_ddladmin', 'db_backupoperator',
        'db_datareader', 'db_datawriter', 'db_denydatareader', 'db_denydatawriter')
ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
"""

QUERY_COLUMNS = """
SELECT
    c.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.CHARACTER_MAXIMUM_LENGTH,
    c.NUMERIC_PRECISION,
    c.NUMERIC_SCALE,
    c.IS_NULLABLE,
    c.ORDINAL_POSITION,
    c.COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS c
WHERE c.TABLE_SCHEMA = ?
    AND c.TABLE_NAME = ?
ORDER BY c.ORDINAL_POSITION
"""

QUERY_PRIMARY_KEYS = """
SELECT
    ccu.COLUMN_NAME
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
JOIN INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE ccu
    ON tc.CONSTRAINT_NAME = ccu.CONSTRAINT_NAME
    AND tc.TABLE_SCHEMA = ccu.TABLE_SCHEMA
WHERE tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
    AND tc.TABLE_SCHEMA = ?
    AND tc.TABLE_NAME = ?
"""

QUERY_ALL_FK = """
SELECT
    fk.name AS fk_name,
    tp.name AS parent_table,
    cp.name AS parent_column,
    tr.name AS ref_table,
    cr.name AS ref_column
FROM sys.foreign_keys fk
JOIN sys.foreign_key_columns fkc
    ON fk.object_id = fkc.constraint_object_id
JOIN sys.tables tp ON fkc.parent_object_id = tp.object_id
JOIN sys.columns cp ON fkc.parent_object_id = cp.object_id AND fkc.parent_column_id = cp.column_id
JOIN sys.tables tr ON fkc.referenced_object_id = tr.object_id
JOIN sys.columns cr ON fkc.referenced_object_id = cr.object_id AND fkc.referenced_column_id = cr.column_id
WHERE tp.schema_id NOT IN (SCHEMA_ID('sys'), SCHEMA_ID('guest'), SCHEMA_ID('INFORMATION_SCHEMA'))
ORDER BY tp.name, cp.name
"""

QUERY_INDEX_COLUMNS = """
SELECT
    OBJECT_NAME(i.object_id) AS table_name,
    i.name AS index_name,
    i.is_primary_key,
    i.is_unique,
    c.name AS column_name
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
JOIN sys.tables t ON i.object_id = t.object_id
WHERE t.schema_id = SCHEMA_ID(?)
    AND t.name = ?
    AND i.name IS NOT NULL
ORDER BY i.name, ic.key_ordinal
"""

QUERY_ROW_COUNTS = """
SELECT
    t.TABLE_SCHEMA,
    t.TABLE_NAME,
    p.rows AS row_count
FROM INFORMATION_SCHEMA.TABLES t
JOIN sys.partitions p
    ON OBJECT_ID(t.TABLE_SCHEMA + '.' + t.TABLE_NAME) = p.object_id
WHERE t.TABLE_TYPE = 'BASE TABLE'
    AND p.index_id IN (0, 1)
    AND t.TABLE_SCHEMA NOT IN ('sys', 'guest', 'INFORMATION_SCHEMA')
ORDER BY t.TABLE_SCHEMA, t.TABLE_NAME
"""


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _read_yaml(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}


def _write_yaml(filepath, data):
    _ensure_dir(os.path.dirname(filepath))
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _derive_display_name(col_name: str) -> str:
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", col_name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    return s.strip()


def _sql_type_to_simple(type_name: str) -> str:
    t = type_name.lower().strip()
    if t.startswith("varchar"):
        return "varchar"
    if t.startswith("nvarchar"):
        return "nvarchar"
    if t.startswith("char") or t.startswith("nchar"):
        return "varchar"
    if t.startswith("decimal") or t.startswith("numeric"):
        return "decimal"
    if t in ("int",):
        return "int"
    if t in ("bigint",):
        return "bigint"
    if t in ("smallint",):
        return "smallint"
    if t in ("tinyint",):
        return "tinyint"
    if t in ("bit",):
        return "bit"
    if t in ("date",):
        return "date"
    if t in ("datetime", "datetime2", "smalldatetime"):
        return "datetime"
    if t in ("time",):
        return "time"
    if t in ("float",):
        return "float"
    if t in ("real",):
        return "real"
    if t in ("money", "smallmoney"):
        return "decimal"
    if t in ("uniqueidentifier",):
        return "uniqueidentifier"
    if t in ("varbinary", "binary", "image"):
        return "binary"
    return t


def connect():
    import pyodbc
    if TRUSTED:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
    else:
        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER};"
            f"DATABASE={DATABASE};"
            f"UID={USER};"
            f"PWD={PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
    return pyodbc.connect(conn_str, timeout=30)


def extract_tables(conn, schema: str) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute(QUERY_TABLES)
    tables = []
    for row in cursor.fetchall():
        if row.TABLE_SCHEMA == schema:
            tables.append({"schema": row.TABLE_SCHEMA, "name": row.TABLE_NAME, "type": row.TABLE_TYPE})
    return tables


def extract_row_counts(conn) -> dict[str, int]:
    cursor = conn.cursor()
    cursor.execute(QUERY_ROW_COUNTS)
    return {row.TABLE_NAME: row.row_count for row in cursor.fetchall()}


def extract_columns(conn, schema: str, table_name: str) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute(QUERY_COLUMNS, (schema, table_name))
    cols = []
    for row in cursor.fetchall():
        type_str = row.DATA_TYPE
        if row.CHARACTER_MAXIMUM_LENGTH and row.DATA_TYPE not in ("text", "ntext", "image"):
            type_str = f"{row.DATA_TYPE}({row.CHARACTER_MAXIMUM_LENGTH})"
        elif row.DATA_TYPE in ("decimal", "numeric") and row.NUMERIC_PRECISION:
            type_str = f"{row.DATA_TYPE}({row.NUMERIC_PRECISION},{row.NUMERIC_SCALE or 0})"
        cols.append({
            "name": row.COLUMN_NAME,
            "datatype": _sql_type_to_simple(type_str),
            "raw_type": type_str,
            "nullable": row.IS_NULLABLE == "YES",
            "ordinal": row.ORDINAL_POSITION,
            "has_default": row.COLUMN_DEFAULT is not None,
        })
    return cols


def extract_pk_columns(conn, schema: str, table_name: str) -> set[str]:
    cursor = conn.cursor()
    cursor.execute(QUERY_PRIMARY_KEYS, (schema, table_name))
    return {row.COLUMN_NAME for row in cursor.fetchall()}


def extract_all_foreign_keys(conn) -> list[dict]:
    cursor = conn.cursor()
    cursor.execute(QUERY_ALL_FK)
    fks = []
    for row in cursor.fetchall():
        fks.append({
            "parent_table": row.parent_table,
            "parent_column": row.parent_column,
            "ref_table": row.ref_table,
            "ref_column": row.ref_column,
        })
    return fks


def extract_index_info(conn, schema: str, table_name: str) -> dict:
    cursor = conn.cursor()
    cursor.execute(QUERY_INDEX_COLUMNS, (schema, table_name))
    filterable, groupable = set(), set()
    for row in cursor.fetchall():
        col = row.column_name
        if row.is_primary_key or row.is_unique:
            groupable.add(col)
        else:
            filterable.add(col)
    return {"filterable": filterable, "groupable": groupable}


# ---------------------------------------------------------------------------
# Auto-fill helpers — fill empty metadata fields for columns not in COLUMN_META
# ---------------------------------------------------------------------------

_NAME_WORD_BLACKLIST = {"id", "tbl", "dim", "dmn"}


def _split_camel(name: str) -> list[str]:
    """Split camelCase/PascalCase into words."""
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    return [w for w in re.split(r"[_\s]+", s) if w]


def _name_to_words(name: str) -> list[str]:
    """Convert column name to lowercase word list."""
    return [w.lower() for w in _split_camel(name) if w.lower() not in _NAME_WORD_BLACKLIST]


_SAMPLE_VALUE_PATTERNS: dict[str, list[str]] = {
    "gender": ["Male", "Female"],
    "maritalstatus": ["Married", "Unmarried", "Divorced"],
    "bloodgroup": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
    "employmenttype": ["Permanent", "Contract", "Temporary", "Intern", "Probation"],
    "yesno": ["Yes", "No"],
    "truefalse": ["true", "false"],
    "activeinactive": ["Active", "Inactive"],
    "paymentterm": ["Net 30", "Net 45", "Net 60", "Advance", "COD"],
    "uom": ["KG", "MT", "Pieces", "Liters", "Nos", "Box"],
    "gradename": ["Grade A", "Grade B", "Grade C", "Premium"],
    "categoryname": ["Raw Material", "Finished Goods", "Consumables", "Edible Oils", "Packaging", "Chemicals", "Spares"],
    "classname": ["Premium", "Standard", "Economy", "Grade A", "Grade B", "Grade C"],
    "orgtype": ["Dealer", "Distributor", "Vendor", "Transporter", "CNF", "Customer"],
    "statustype": ["Pending", "Approved", "Rejected", "Cancelled", "Completed", "Active", "Inactive"],
}


def _auto_fill_aliases(col_name: str) -> list[str]:
    words = _name_to_words(col_name)
    if not words:
        return []
    seen: set[str] = set()
    result: list[str] = []
    for w in words:
        wl = w.lower()
        if wl not in seen and wl not in _NAME_WORD_BLACKLIST:
            seen.add(wl)
            result.append(wl)
    name_lower = " ".join(result)
    if name_lower and name_lower not in seen:
        result.append(name_lower)
    return result


def _auto_fill_aggregations_allowed(datatype: str, role: str = "") -> list[str]:
    if role in ("foreign_key", "identifier", "status"):
        return []
    if role == "metric":
        return ["SUM", "AVG", "MIN", "MAX"]
    if datatype in ("int", "decimal", "float", "bigint", "smallint", "tinyint", "money", "real"):
        return ["SUM", "AVG", "MIN", "MAX"]
    return []


def _auto_fill_sample_values(col_name: str) -> list[str]:
    key = col_name.lower().replace("_", "").replace(" ", "")
    for pattern, values in _SAMPLE_VALUE_PATTERNS.items():
        if pattern in key:
            return values
    if col_name.lower().startswith("is") and col_name != "isActive":
        return ["true", "false"]
    return []


def _auto_fill_search_keywords(col_name: str, aliases: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for w in _name_to_words(col_name):
        wl = w.lower()
        if wl not in seen:
            seen.add(wl)
            result.append(wl)
    for alias in aliases:
        for w in alias.lower().split():
            if w not in seen:
                seen.add(w)
                result.append(w)
    return result


def _auto_fill_intents(col_name: str, role: str) -> list[str]:
    display = _derive_display_name(col_name).lower()
    if role == "metric":
        return [f"Total {display}", f"Average {display}", f"Sum of {display}", f"Maximum {display}", f"Minimum {display}"]
    if role == "dimension":
        return [f"Filter by {display}", f"Group by {display}", f"Show {display}"]
    if role == "identifier":
        return [f"Find by {display}", f"Search {display}", f"Show {display}"]
    if role == "foreign_key":
        return [f"Filter by {display}", f"Join by {display}"]
    if role == "status":
        return [f"Filter by {display}"]
    return []


_ROLE_NAME_PATTERNS: dict[str, list[str]] = {
    "dimension": ["name", "type", "date", "address", "gender", "description", "remark", "note", "comment", "status"],
    "metric": ["amount", "total", "qty", "quantity", "price", "rate", "score", "value", "count", "charge", "pay", "deduction", "earning"],
    "identifier": ["code", "number", "no", "ref", "email", "phone", "mobile"],
    "status": ["isactive", "isenabled", "isdeleted", "isarchived", "islocked"],
}


def _infer_role(col_name: str) -> str | None:
    name_lower = col_name.lower()
    words = _name_to_words(col_name)
    for role, patterns in _ROLE_NAME_PATTERNS.items():
        for pat in patterns:
            if pat in name_lower or pat in words:
                return role
    return None


def _auto_fill_column(col_name: str, datatype: str, role: str, existing: dict) -> dict:
    """Fill any empty metadata fields for a column with auto-derived values."""
    out = dict(existing)
    if role == "attribute" or role == "":
        inferred = _infer_role(col_name)
        if not inferred and out.get("is_join_key"):
            inferred = "foreign_key"
        if inferred:
            out["role"] = inferred
            role = inferred
            if out.get("filterable") is not None:
                out["filterable"] = inferred in ("foreign_key", "dimension", "identifier", "status", "metric")
            if out.get("groupable") is not None:
                out["groupable"] = inferred in ("dimension", "identifier", "foreign_key", "status")
            if out.get("aggregatable") is not None:
                out["aggregatable"] = inferred == "metric"
    if not out.get("aliases"):
        out["aliases"] = _auto_fill_aliases(col_name)
    if not out.get("aggregations_allowed"):
        out["aggregations_allowed"] = _auto_fill_aggregations_allowed(datatype, role)
    if out.get("aggregatable") and not out.get("aggregations_allowed"):
        out["aggregations_allowed"] = _auto_fill_aggregations_allowed(datatype, role)
    if out.get("aggregations_allowed") and not out.get("aggregatable"):
        out["aggregatable"] = True
    if not out.get("sample_values"):
        out["sample_values"] = _auto_fill_sample_values(col_name)
    if not out.get("search_keywords"):
        out["search_keywords"] = _auto_fill_search_keywords(col_name, out.get("aliases", []))
    if not out.get("common_user_intents"):
        out["common_user_intents"] = _auto_fill_intents(col_name, role)
    return out


def build_table_yaml(table_name: str, columns: list[dict], pk_cols: set[str],
                     foreign_keys: list[dict], row_count: int) -> dict:
    table_fks = [fk for fk in foreign_keys if fk["parent_table"] == table_name]
    related = list({fk["ref_table"] for fk in table_fks})

    return {
        "table_name": table_name,
        "display_name": _derive_display_name(table_name),
        "domain": "",
        "module": "",
        "description": f"Table {table_name} from database.",
        "primary_key": list(pk_cols)[0] if pk_cols else (columns[0]["name"] if columns else ""),
        "estimated_rows": row_count,
        "search_weight": 5,
        "priority": "Medium",
        "search_keywords": [],
        "common_user_intents": [],
        "foreign_keys": [{"name": fk["parent_column"], "references": f"{fk['ref_table']}.{fk['ref_column']}"} for fk in table_fks],
        "related_tables": related,
        "important_columns": [],
        "business_metrics": [],
        "common_filters": [],
        "common_groupby": [],
        "columns": [{"name": c["name"], "type": c["datatype"], "nullable": c["nullable"]} for c in columns],
    }


def build_column_yaml(table_name: str, columns: list[dict], pk_cols: set[str],
                      fk_cols: set[str], idx_info: dict) -> dict:
    filterable_set = idx_info.get("filterable", set())
    groupable_set = idx_info.get("groupable", set())

    col_entries = []
    for c in columns:
        col_name = c["name"]
        is_pk = col_name in pk_cols
        is_fk = col_name in fk_cols
        agg_allowed = ["SUM", "AVG", "MIN", "MAX"] if c["datatype"] in ("int", "decimal", "float", "bigint", "smallint") else []

        col_entries.append({
            "name": col_name,
            "display_name": _derive_display_name(col_name),
            "datatype": c["datatype"],
            "description": _derive_display_name(col_name),
            "nullable": c["nullable"],
            "role": "identifier" if is_pk else "foreign_key" if is_fk else "dimension",
            "importance": "high" if is_pk or is_fk else "medium",
            "is_primary_key": is_pk,
            "is_join_key": is_fk,
            "filterable": col_name in filterable_set or is_fk,
            "groupable": col_name in groupable_set or is_pk,
            "aggregatable": len(agg_allowed) > 0,
            "aggregations_allowed": agg_allowed,
            "search_keywords": [],
            "common_user_intents": [],
            "sample_values": [],
        })
    return {"columns": col_entries}


def generate_from_db():
    import pyodbc
    print(f"Connecting to {SERVER}/{DATABASE} ({'Windows Auth' if TRUSTED else 'SQL Auth'})...")
    conn = connect()
    print("Connected.")

    print("Extracting foreign keys...")
    all_fks = extract_all_foreign_keys(conn)
    print(f"  Found {len(all_fks)} foreign key relationships")

    fk_col_set: dict[str, set[str]] = {}
    for fk in all_fks:
        fk_col_set.setdefault(fk["parent_table"], set()).add(fk["parent_column"])

    print("Extracting row counts...")
    row_counts = extract_row_counts(conn)

    print(f"Extracting tables from schema '{SCHEMA}'...")
    tables = extract_tables(conn, SCHEMA)
    print(f"  Found {len(tables)} tables")

    tables_dir = BASE / "tables"
    columns_dir = BASE / "columns"
    _ensure_dir(tables_dir)
    _ensure_dir(columns_dir)

    for i, tbl in enumerate(tables, 1):
        tname = tbl["name"]
        print(f"  [{i}/{len(tables)}] {tname}...", end=" ", flush=True)

        columns = extract_columns(conn, SCHEMA, tname)
        if not columns:
            print("SKIP (no columns)")
            continue

        pk_cols = extract_pk_columns(conn, SCHEMA, tname)
        idx_info = extract_index_info(conn, SCHEMA, tname)
        row_count = row_counts.get(tname, 0)

        table_doc = build_table_yaml(tname, columns, pk_cols, all_fks, row_count)
        _write_yaml(tables_dir / f"{tname}.yaml", table_doc)

        table_fk_cols = fk_col_set.get(tname, set())
        col_doc = build_column_yaml(tname, columns, pk_cols, table_fk_cols, idx_info)
        _write_yaml(columns_dir / f"{tname}.yaml", col_doc)

        print(f"OK ({len(columns)} cols)")

    print("Generating joins...")
    joins_dir = BASE / "joins"
    _ensure_dir(joins_dir)
    joins = [{
        "from_table": fk["parent_table"], "from_column": fk["parent_column"],
        "to_table": fk["ref_table"], "to_column": fk["ref_column"],
        "on": f"{fk['parent_table']}.{fk['parent_column']} = {fk['ref_table']}.{fk['ref_column']}",
        "join_type": "LEFT JOIN",
        "business_meaning": f"Links {fk['parent_table']}.{fk['parent_column']} to {fk['ref_table']}.{fk['ref_column']}",
    } for fk in all_fks]
    _write_yaml(joins_dir / "joins.yaml", {"joins": joins})
    print(f"  Generated {len(joins)} join definitions")

    conn.close()
    print(f"\nDone! Extracted {len(tables)} tables into {BASE}")
    print("Next step: run merge_metadata to add descriptions, keywords, and business context.")


def merge():
    tables_dir = BASE / "tables"
    cols_dir = BASE / "columns"
    joins_path = BASE / "joins" / "joins.yaml"
    tables_dir.mkdir(parents=True, exist_ok=True)
    cols_dir.mkdir(parents=True, exist_ok=True)

    joins_data = _read_yaml(joins_path)
    fk_map = defaultdict(list)
    for j in joins_data.get("joins", []):
        fk_map[j.get("from_table", j.get("from", ""))].append(
            {"col": j.get("from_column"), "ref": j.get("to_table", "") + "." + j.get("to_column", "")}
        )

    for table_name, meta in sorted(TABLE_META.items()):
        existing = _read_yaml(tables_dir / f"{table_name}.yaml")
        columns = existing.get("columns", [])
        foreign_keys = [{"name": fk["col"], "references": fk["ref"]} for fk in fk_map.get(table_name, [])]
        related = sorted({fk["ref"].split(".")[0] for fk in fk_map.get(table_name, [])})

        table_yaml = {
            "table_name": table_name,
            "display_name": meta.get("display_name", table_name),
            "domain": meta.get("domain", ""),
            "module": meta.get("module", ""),
            "description": meta.get("description", ""),
            "primary_key": existing.get("primary_key", ""),
            "estimated_rows": existing.get("estimated_rows", 0),
            "search_weight": meta.get("search_weight", 5),
            "priority": meta.get("priority", "Medium"),
            "search_keywords": meta.get("search_keywords", []),
            "common_user_intents": meta.get("common_user_intents", []),
            "foreign_keys": foreign_keys,
            "related_tables": related,
            "important_columns": meta.get("important_columns", []),
            "business_metrics": meta.get("business_metrics", []),
            "common_filters": meta.get("common_filters", []),
            "common_groupby": meta.get("common_groupby", []),
            "columns": [],
        }

        col_entries = []
        for col in columns:
            cname = col["name"]
            col_datatype = col.get("type", col.get("datatype", "varchar"))
            cm = COLUMN_META.get((table_name, cname), COLUMN_META.get(("", cname), {}))
            if cname == "isActive":
                cm = dict(ACTIVE_ALIASES)
                if col_datatype == "bit":
                    cm["sample_values"] = [1, 0]
            is_pk = cname == table_yaml["primary_key"] or col.get("is_primary_key", False)

            col_role = cm.get("role", "attribute")

            entry = {
                "name": cname,
                "display_name": cname,
                "datatype": col_datatype,
                "description": cm.get("description", f"{cname} column in {table_name}"),
                "nullable": col.get("nullable", True),
                "role": col_role,
                "importance": cm.get("importance", "medium"),
                "is_primary_key": is_pk,
                "is_join_key": cname in [fk["col"] for fk in fk_map.get(table_name, [])],
                "filterable": col_role in ("foreign_key", "dimension", "identifier", "status", "metric") or cname in ("isActive", "statusId", "status"),
                "groupable": col_role in ("dimension", "identifier", "foreign_key", "status"),
                "aggregatable": col_role == "metric",
                "aggregations_allowed": ["SUM", "AVG", "MIN", "MAX"] if col_role == "metric" else [],
                "aliases": cm.get("aliases", []),
                "sample_values": cm.get("sample_values", []),
                "search_keywords": cm.get("search_keywords", []),
                "common_user_intents": cm.get("common_user_intents", []),
            }

            entry = _auto_fill_column(cname, col_datatype, col_role, entry)
            col_entries.append(entry)

        table_yaml["columns"] = col_entries
        _write_yaml(tables_dir / f"{table_name}.yaml", table_yaml)
        _write_yaml(cols_dir / f"{table_name}.yaml", {"columns": col_entries})

        print(f"  [{table_name}] keywords={len(meta.get('search_keywords', []))}, "
              f"intents={len(meta.get('common_user_intents', []))}, cols={len(col_entries)}")

    kw_total = sum(len(m.get("search_keywords", [])) for m in TABLE_META.values())
    in_total = sum(len(m.get("common_user_intents", [])) for m in TABLE_META.values())
    print(f"\nDone: {len(TABLE_META)} tables, {kw_total} keywords, {in_total} intents")


def write_bootstrap_data():
    """Write all bootstrapped knowledge base data (domains, glossary, examples, rules, patterns, stats)."""
    domains_dir = BASE / "domains"
    glossary_dir = BASE / "glossary"
    examples_dir = BASE / "examples"
    rules_dir = BASE / "business_rules"
    patterns_dir = BASE / "sql_patterns"
    stats_dir = BASE / "stats"

    for d in [domains_dir, glossary_dir, examples_dir, rules_dir, patterns_dir, stats_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # Domains
    _write_yaml(domains_dir / "domains.yaml", {"domains": DOMAINS_DATA})
    print(f"  domains.yaml ({len(DOMAINS_DATA)} domains)")

    # Glossary
    _write_yaml(glossary_dir / "glossary.yaml", {"terms": GLOSSARY_DATA})
    print(f"  glossary.yaml ({len(GLOSSARY_DATA)} terms)")

    # Examples
    _write_yaml(examples_dir / "examples.yaml", {"examples": EXAMPLES_DATA})
    print(f"  examples.yaml ({len(EXAMPLES_DATA)} examples)")

    # Business Rules
    _write_yaml(rules_dir / "business_rules.yaml", {"rules": BUSINESS_RULES_DATA})
    print(f"  business_rules.yaml ({len(BUSINESS_RULES_DATA)} rules)")

    # SQL Patterns
    _write_yaml(patterns_dir / "sql_patterns.yaml", {"patterns": SQL_PATTERNS_DATA})
    print(f"  sql_patterns.yaml ({len(SQL_PATTERNS_DATA)} patterns)")

    # Terms
    terms_dir = BASE / "terms"
    terms_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(terms_dir / "terms.yaml", TERMS_DATA)
    print(f"  terms.yaml ({sum(len(v) for v in TERMS_DATA.values())} entries)")

    # Stats — compute from actual data
    table_count = len(list((BASE / "tables").glob("*.yaml")))
    total_cols = 0
    for tname in TABLE_META:
        tbl_yaml = _read_yaml(BASE / "tables" / f"{tname}.yaml")
        total_cols += len(tbl_yaml.get("columns", []))
    stats = {
        "tables_count": len(TABLE_META),
        "total_columns": total_cols,
        "total_foreign_keys": len([j for j in _read_yaml(BASE / "joins" / "joins.yaml").get("joins", [])]),
        "total_keywords": sum(len(m.get("search_keywords", [])) for m in TABLE_META.values()),
        "total_intents": sum(len(m.get("common_user_intents", [])) for m in TABLE_META.values()),
        "total_domains": len(DOMAINS_DATA),
        "total_rules": len(BUSINESS_RULES_DATA),
        "total_glossary_terms": len(GLOSSARY_DATA),
        "total_sql_patterns": len(SQL_PATTERNS_DATA),
        "total_examples": len(EXAMPLES_DATA),
    }
    _write_yaml(stats_dir / "stats.yaml", stats)
    print(f"  stats.yaml ({len(stats)} stats)")


def full_rebuild():
    """Full rebuild: extract from DB → merge metadata → bootstrap hand-written data."""
    print("=" * 60)
    print("STEP 1/3: Extracting schema from database")
    print("=" * 60)
    try:
        generate_from_db()
    except Exception as e:
        print(f"\nERROR: Could not extract schema from database: {e}")
        print()
        print("If your database is not available, you can still run:")
        print("  python scripts/generate.py merge     # enrich metadata")
        print("  python scripts/generate.py bootstrap # write bootstrap files")
        print()
        print("Make sure knowledge_base/ already has table/column YAMLs from a prior extract.")
        return

    print("\n" + "=" * 60)
    print("STEP 2/3: Merging business metadata")
    print("=" * 60)
    merge()

    print("\n" + "=" * 60)
    print("STEP 3/3: Writing bootstrap data (domains, glossary, examples, rules, patterns)")
    print("=" * 60)
    write_bootstrap_data()

    print("\n" + "=" * 60)
    print("FULL REBUILD COMPLETE")
    print("=" * 60)
    print(f"Restart the server for changes to take effect.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "merge":
        merge()
    elif len(sys.argv) > 1 and sys.argv[1] == "bootstrap":
        write_bootstrap_data()
    elif len(sys.argv) > 1 and sys.argv[1] == "full-rebuild":
        full_rebuild()
    else:
        generate_from_db()
