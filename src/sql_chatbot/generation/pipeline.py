import logging

from sql_chatbot.db.executor import execute_query, SQLValidationError
from sql_chatbot.generation.llm_client import generate_sql, generate_answer
from sql_chatbot.generation.prompt import build_context_str, build_prompt

logger = logging.getLogger(__name__)


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

    prompt = build_prompt(
        user_query,
        build_context_str(retrieval_result),
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
        result = execute_query(sql)
        result["not_supported"] = False
        return result
    except SQLValidationError as e:
        return {
            "not_supported": True,
            "sql": sql,
            "columns": [],
            "rows": [],
            "row_count": 0,
            "error": str(e),
        }
    except Exception as e:
        logger.warning("SQL execution error (retrying): %s", e)
        retry_prompt = prompt + f"\n\nThe previous SQL attempt failed with error: {e}\nPlease fix the SQL syntax and generate a corrected query."
        retry_sql = generate_sql(retry_prompt)
        if not retry_sql.strip().upper().startswith("NOT_SUPPORTED"):
            try:
                result = execute_query(retry_sql)
                result["not_supported"] = False
                return result
            except Exception:
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
