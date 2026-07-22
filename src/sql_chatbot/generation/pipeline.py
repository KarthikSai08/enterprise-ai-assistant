import re
import logging

from sql_chatbot.db.executor import execute_query, SQLValidationError, SQLQueryExecutionError, DBConnectionError
from sql_chatbot.generation.llm_client import generate_sql, generate_answer
from sql_chatbot.generation.prompt import build_context_str, build_prompt

logger = logging.getLogger(__name__)


def _build_valid_columns(retrieval_result: dict) -> set[str]:
    cols: set[str] = set()
    for r in retrieval_result.get("results", []):
        table = r.get("table", "")
        for c in r.get("all_columns", []):
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


def _extract_column_hint(error: str, valid_columns: set[str]) -> str:
    match = re.search(r"Invalid column(?: name)? '([^']+)'", error) or re.search(r"Invalid column names found in SQL: (\w+)", error)
    if match:
        bad_col = match.group(1)
        candidates = set()
        for vc in valid_columns:
            parts = vc.split(".")
            if len(parts) == 2:
                col_name = parts[1]
                if bad_col.lower() in col_name.lower() or col_name.lower() in bad_col.lower():
                    candidates.add(parts[0])
        if candidates:
            tbl_names = ", ".join(sorted(candidates))
            tbl_cols = set()
            for vc in valid_columns:
                parts = vc.split(".")
                if len(parts) == 2 and parts[0] in candidates:
                    tbl_cols.add(parts[1])
            cols_list = ", ".join(sorted(tbl_cols))
            return (
                f"The previous SQL used '{bad_col}' but that column does not exist. "
                f"Did you mean one of these columns on table '{tbl_names}': {cols_list}? "
                f"Please correct the query using ONLY columns from DATABASE CONTEXT."
            )
        return f"The column '{bad_col}' does not exist in any table. Only use columns from DATABASE CONTEXT."
    return ""


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
    prompt = build_prompt(
        user_query,
        context_str,
        intent=retrieval_result.get("intent"),
    )
    sql = generate_sql(prompt)

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
        hint = _extract_column_hint(str(e), valid_columns)
        if hint:
            logger.warning("Column hallucination detected: %s", hint)
            retry_prompt = (
                prompt
                + f"\n\nThe previous SQL was rejected for using invalid columns.\n{hint}\n"
                + "Please rewrite the SQL using ONLY columns from the DATABASE CONTEXT above."
            )
            retry_sql = generate_sql(retry_prompt)
            if not retry_sql.strip().upper().startswith("NOT_SUPPORTED"):
                try:
                    result = execute_query(retry_sql, valid_columns)
                    result["not_supported"] = False
                    return result
                except (SQLValidationError, SQLQueryExecutionError):
                    pass
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
        hint = _extract_column_hint(str(e), valid_columns)
        retry_extra = f"\n{hint}\n" if hint else "\n"
        retry_prompt = (
            prompt
            + f"\n\nThe previous SQL attempt failed with error: {e}{retry_extra}"
            + "Please fix the SQL syntax and generate a corrected query using ONLY columns from DATABASE CONTEXT."
        )
        retry_sql = generate_sql(retry_prompt)
        if not retry_sql.strip().upper().startswith("NOT_SUPPORTED"):
            try:
                result = execute_query(retry_sql, valid_columns)
                result["not_supported"] = False
                return result
            except (SQLValidationError, SQLQueryExecutionError):
                pass
        return {
            "not_supported": False,
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
