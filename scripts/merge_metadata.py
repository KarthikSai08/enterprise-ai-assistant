#!/usr/bin/env python
"""
Merge hand-curated business metadata (from generate_metadata.py) into the
raw YAML files already sitting in knowledge_base/. Run this AFTER
generate_kb_from_db.py, or any time you edit TABLE_META/COLUMN_META.

Usage:
    python merge_metadata.py
"""
import sys
from collections import defaultdict
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generate_metadata import TABLE_META, COLUMN_META as _RICH_COLUMN_META, ACTIVE_ALIASES

BASE = Path(__file__).resolve().parent.parent / "knowledge_base"

# ---------------------------------------------------------------------------
# Start with your hand-curated (rich) entries, then auto-fill generic
# columns that you haven't written by hand. .setdefault() = "only fill
# this in if it's not already there" — hand-written entries always win.
# ---------------------------------------------------------------------------
COLUMN_META = dict(_RICH_COLUMN_META)

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
            "deliveryDate", "startDate", "endDate"]:
    COLUMN_META.setdefault(("", col), {
        "description": "Date of the transaction", "role": "dimension", "importance": "high",
        "aliases": [col.replace("Date", " date"), "transaction date"],
    })


def _read_yaml(path):
    try:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except (FileNotFoundError, yaml.YAMLError):
        return {}


def _write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


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
            cm = COLUMN_META.get((table_name, cname), COLUMN_META.get(("", cname), {}))
            if cname == "isActive":
                cm = ACTIVE_ALIASES
            is_pk = cname == table_yaml["primary_key"] or col.get("is_primary_key", False)

            col_entries.append({
                "name": cname,
                "display_name": cname,
                "datatype": col.get("type", col.get("datatype", "varchar")),
                "description": cm.get("description", f"{cname} column in {table_name}"),
                "nullable": col.get("nullable", True),
                "role": cm.get("role", "attribute"),
                "importance": cm.get("importance", "medium"),
                "is_primary_key": is_pk,
                "is_join_key": cname in [fk["col"] for fk in fk_map.get(table_name, [])],
                "filterable": cm.get("role") in ("foreign_key", "dimension", "identifier", "status") or cname in ("isActive", "statusId", "status"),
                "groupable": cm.get("role") in ("dimension", "identifier", "foreign_key", "status"),
                "aggregatable": cm.get("role") == "metric",
                "aggregations_allowed": ["SUM", "AVG", "MIN", "MAX"] if cm.get("role") == "metric" else [],
                "aliases": cm.get("aliases", []),
                "search_keywords": cm.get("search_keywords", []),
                "common_user_intents": cm.get("common_user_intents", []),
            })

        table_yaml["columns"] = col_entries
        _write_yaml(tables_dir / f"{table_name}.yaml", table_yaml)
        _write_yaml(cols_dir / f"{table_name}.yaml", {"columns": col_entries})

        print(f"  [{table_name}] keywords={len(meta.get('search_keywords', []))}, "
              f"intents={len(meta.get('common_user_intents', []))}, cols={len(col_entries)}")

    kw_total = sum(len(m.get("search_keywords", [])) for m in TABLE_META.values())
    in_total = sum(len(m.get("common_user_intents", [])) for m in TABLE_META.values())
    print(f"\nDone: {len(TABLE_META)} tables, {kw_total} keywords, {in_total} intents")


if __name__ == "__main__":
    merge()

    