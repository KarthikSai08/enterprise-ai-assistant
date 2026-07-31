import re
import logging

import requests
from sql_chatbot.db.executor import execute_query, SQLValidationError, SQLQueryExecutionError, DBConnectionError
from sql_chatbot.generation.llm_client import call_llm, generate_answer
from sql_chatbot.generation.prompt import build_context_str, build_prompt

logger = logging.getLogger(__name__)


def _build_valid_columns(retrieval_result: dict) -> set[str]:
    cols: set[str] = set()
    for r in retrieval_result.get("results", []):
        table = r.get("table", "")
        for c in (r.get("all_columns") or []):
            cols.add(f"{table}.{c}")
            cols.add(c)
        for fk in r.get("foreign_keys", []):
            fk_name = fk.get("name", "")
            if fk_name:
                cols.add(f"{table}.{fk_name}")
                cols.add(fk_name)
        pk = r.get("primary_key", "")
        if pk:
            cols.add(f"{table}.{pk}")
            cols.add(pk)
    for j in retrieval_result.get("joins", []):
        on_clause = j.get("on", "")
        for part in re.split(r"\s*=\s*", on_clause):
            part = part.strip()
            if "." in part:
                cols.add(part)
    return cols


def _extract_column_hint(bad_columns: list[str], valid_columns: set[str], retrieval_result: dict | None = None) -> str:
    assert isinstance(bad_columns, list), f"bad_columns must be a list, got {type(bad_columns)}: {bad_columns!r}"
    if not bad_columns:
        return ""
    hints = []
    all_missing_tables: set[str] = set()

    for raw_entry in bad_columns:
        bad_col = raw_entry.split(".")[-1]
        candidates = {
            parts[0] for vc in valid_columns
            if len(parts := vc.split(".")) == 2 and bad_col.lower() == parts[1].lower()
        }
        if not candidates:
            candidates = {
                parts[0] for vc in valid_columns
                if len(parts := vc.split(".")) == 2 and bad_col.lower() in parts[1].lower()
            }
        if candidates:
            tbl_names = ", ".join(sorted(candidates))
            tbl_cols = {
                parts[1] for vc in valid_columns
                if len(parts := vc.split(".")) == 2 and parts[0] in candidates
            }
            hints.append(
                f"'{raw_entry}' is wrong — '{bad_col}' belongs to table(s) '{tbl_names}' "
                f"(columns there: {', '.join(sorted(tbl_cols))}), not the table you attached it to."
            )
            if retrieval_result:
                all_missing_tables.update(
                    t for t in candidates
                    if not any(r["table"] == t for r in retrieval_result.get("results", []))
                )
        else:
            hints.append(f"'{raw_entry}' — column '{bad_col}' does not exist in any table in DATABASE CONTEXT.")

    hint = " ".join(hints) + " Correct the query using ONLY columns from DATABASE CONTEXT, attached to the correct table alias."
    if all_missing_tables:
        hint += f" NOTE: {', '.join(sorted(all_missing_tables))} are valid tables but may not currently be listed above."
    return hint

_EXEC_ERROR_COLUMN_RE = re.compile(r"Invalid column(?: name)? '([^']+)'", re.I)

def _extract_column_hint_from_exec_error(error_msg: str, valid_columns: set[str], retrieval_result: dict | None = None) -> str:
    """For SQLQueryExecutionError (raw DB error text) — different shape than
    the AST validator's structured bad_columns list, so parse separately."""
    matches = _EXEC_ERROR_COLUMN_RE.findall(error_msg)
    if not matches:
        return ""
    return _extract_column_hint(matches, valid_columns, retrieval_result)

def run_sql_with_retry(user_query: str, retrieval_result: dict) -> dict:
    if not retrieval_result.get("results"):
        return {
            "not_supported": True,
            "sql": None,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": "No matching tables or columns found for this query. Try rephrasing with different words.",
        }

    valid_columns = _build_valid_columns(retrieval_result)
    context_str = build_context_str(retrieval_result)
    result_table_names = [r["table"] for r in retrieval_result.get("results", [])]
    prompt = build_prompt(
        user_query,
        context_str,
        intent=retrieval_result.get("intent"),
        detected_entities=retrieval_result.get("detected_entities"),
        detected_filters=retrieval_result.get("detected_filters"),
        context_joins=retrieval_result.get("joins", []),
        main_tables=result_table_names,
    )

    try:
        sql = call_llm(prompt)
    except (RuntimeError, ValueError, requests.RequestException) as e:
        return {
            "not_supported": True,
            "sql": None,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": f"SQL generation failed — LLM unavailable: {e}",
        }

    if sql.strip().upper().startswith("NOT_SUPPORTED"):
        return {
            "not_supported": True,
            "sql": None,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": None,
        }

    try:
        result = execute_query(sql, valid_columns)
        result["not_supported"] = False
        return result
    except SQLValidationError as e:
        hint = _extract_column_hint(e.bad_columns, valid_columns, retrieval_result)
        if hint:
            logger.warning("Column hallucination detected: %s", hint)
            retry_prompt = (
                prompt
                + f"\n\nThe previous SQL was rejected for using invalid columns.\n{hint}\n"
                + "Please rewrite the SQL using ONLY columns from the DATABASE CONTEXT above."
            )
            try:
                retry_sql = call_llm(retry_prompt)
            except (RuntimeError, ValueError, requests.RequestException):
                return {
                    "not_supported": True,
                    "sql": sql,
                    "columns": [],
                    "rows": [],
                    "row_count": 0,
                    "error": str(e),
                }
            if not retry_sql.strip().upper().startswith("NOT_SUPPORTED"):
                try:
                    result = execute_query(retry_sql, valid_columns)
                    result["not_supported"] = False
                    return result
                except SQLQueryExecutionError as e:
                    logger.warning("SQL execution error (retrying): %s", e)
                    hint = _extract_column_hint_from_exec_error(str(e), valid_columns, retrieval_result)
                    retry_extra = f"\n{hint}\n" if hint else "\n"
        return {
            "not_supported": True,
            "sql": sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e),
        }
    except DBConnectionError as e:
        return {
            "not_supported": True,
            "sql": sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e),
        }
    except SQLQueryExecutionError as e:
        logger.warning("SQL execution error (retrying): %s", e)
        hint = _extract_column_hint(str(e), valid_columns, retrieval_result)
        retry_extra = f"\n{hint}\n" if hint else "\n"
        retry_prompt = (
            prompt
            + f"\n\nThe previous SQL attempt failed with error: {e}{retry_extra}"
            + "Please fix the SQL syntax and generate a corrected query using ONLY columns from DATABASE CONTEXT."
        )
        try:
            retry_sql = call_llm(retry_prompt)
        except (RuntimeError, ValueError, requests.RequestException):
            return {
                "not_supported": True,
                "sql": sql,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": str(e),
            }
        if not retry_sql.strip().upper().startswith("NOT_SUPPORTED"):
            try:
                result = execute_query(retry_sql, valid_columns)
                result["not_supported"] = False
                return result
            except (SQLValidationError, SQLQueryExecutionError) as retry_e:
                logger.warning("Execution retry also failed: %s", retry_e)
                pass
        return {
            "not_supported": True,
            "sql": sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e),
        }


def run_sql_with_answer(user_query: str, retrieval_result: dict) -> dict:
    sql_result = run_sql_with_retry(user_query, retrieval_result)
    if sql_result.get("not_supported"):
        sql_result["answer"] = None
        return sql_result

    try:
        answer = generate_answer(
            user_query=user_query,
            sql=sql_result["sql"],
            columns=sql_result["columns"],
            rows=sql_result["rows"],
            row_count=sql_result["row_count"],
        )
        sql_result["answer"] = answer
    except Exception as e:
        logger.warning("Answer generation failed: %s", e)
        sql_result["answer"] = None

    return sql_result