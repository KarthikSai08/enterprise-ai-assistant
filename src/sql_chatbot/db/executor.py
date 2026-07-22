import re
import pyodbc
from sql_chatbot.config import DB_SERVER, DB_NAME, DB_USER, DB_PASS, DB_TRUSTED

class SQLValidationError(Exception):
    pass

class SQLQueryExecutionError(Exception):
    pass

class DBConnectionError(Exception):
    pass

_SQL_KEYWORDS = frozenset(w.upper() for w in """
    SELECT FROM WHERE AND OR NOT IN AS ON JOIN LEFT RIGHT INNER OUTER FULL CROSS
    TOP DISTINCT ORDER BY GROUP HAVING ASC DESC BETWEEN LIKE IS NULL TRUE FALSE
    CASE WHEN THEN ELSE END EXISTS UNION ALL INTERSECT EXCEPT WITH
    COUNT SUM AVG MIN MAX OVER PARTITION ROW_NUMBER RANK DENSE_RANK
    GETDATE DATEADD DATEDIFF YEAR MONTH DAY DATEPART CAST CONVERT
    SUBSTRING CHARINDEX LEN REPLACE UPPER LOWER TRIM
    ABS ROUND CEILING FLOOR POWER IIF COALESCE NULLIF
    SET DECLARE BEGIN END IF ELSE WHILE RETURN PRINT RAISERROR THROW
    INSERT UPDATE DELETE MERGE DROP ALTER TRUNCATE CREATE EXEC EXECUTE
    GRANT REVOKE DENY BACKUP RESTORE DBCC OPENROWSET OPENQUERY
    BULK INSERT xp_cmdshell GO
""".split())

_HARMFUL_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|MERGE|EXEC|EXECUTE|"
    r"GRANT|REVOKE|REPLACE|RENAME|CREATE|EXPORT|CALL|DECLARE|RAISE|PRAGMA|"
    r"COPY|VACUUM|LOAD|IMPORT)\b",
    re.IGNORECASE,
)

_SQL_IDENTIFIER = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')


def check_not_supported(sql: str) -> None:
    if sql.strip().upper().startswith("NOT_SUPPORTED"):
        raise SQLValidationError("This question isn't something I can answer from the database.")


def validate_columns(sql: str, valid_columns: set[str]) -> None:
    no_strings = re.sub(r"'[^']*'", "", sql)
    no_comments = re.sub(r"--.*$", "", no_strings, flags=re.MULTILINE)
    no_numbers = re.sub(r"\b\d+\b", "", no_comments)

    qualified = re.findall(r'(\w+)\.(\w+)', no_comments)
    for tbl, col in qualified:
        col_key = f"{tbl}.{col}"
        if col_key not in valid_columns:
            raise SQLValidationError(
                f"Invalid column '{col_key}': column does not exist in DATABASE CONTEXT."
            )

    all_qualified_cols = {c for _, c in qualified}
    all_tables = {t for t, _ in qualified}

    tokens = _SQL_IDENTIFIER.findall(no_numbers)
    hallucinated = []
    for token in tokens:
        if token.upper() in _SQL_KEYWORDS:
            continue
        if token in all_tables:
            continue
        if token in all_qualified_cols:
            continue
        if any(token in v or v.endswith("." + token) for v in valid_columns):
            continue
        if any(token.lower() == v.split(".")[-1].lower() for v in valid_columns):
            continue
        hallucinated.append(token)
    if hallucinated:
        raise SQLValidationError(
            f"Invalid column names found in SQL: {', '.join(hallucinated[:5])}. "
            "These do not exist in DATABASE CONTEXT."
        )


def validate_and_cap(sql: str, max_rows: int = 100) -> str:
    stripped = sql.strip()
    if not stripped:
        raise SQLValidationError("Empty SQL statement.")

    if _HARMFUL_PATTERNS.search(stripped):
        raise SQLValidationError("Only SELECT statements are allowed.")

    stripped = re.sub(
        r"(?i)\bSELECT\s+TOP\s*\(?\s*(\d+)\s*\)?\s+DISTINCT\b",
        r"SELECT DISTINCT TOP \1",
        stripped,
    )

    stripped = re.sub(
        r"(?i)(\bSELECT\b.*?)\bTOP\b\s*\(?\s*(\d+)\s*\)?\s+DISTINCT\b",
        r"\1DISTINCT TOP \2",
        stripped,
    )

    upper = stripped.upper()
    if not upper.startswith("SELECT"):
        raise SQLValidationError("Only SELECT statements are allowed.")

    has_top = "TOP " in upper or "TOP(" in upper

    if not has_top:
        insert_at = _find_select_list_end(stripped)
        if insert_at:
            kw = stripped[insert_at:].lstrip()
            if kw and not kw.upper().startswith("TOP ") and not kw.upper().startswith("TOP("):
                stripped = stripped[:insert_at] + f"TOP {max_rows} " + stripped[insert_at:]

    return stripped


def _find_select_list_end(sql: str) -> int | None:
    stripped = sql.lstrip()
    offset = len(sql) - len(stripped)
    upper = stripped.upper()
    if "SELECT " not in upper and "SELECT(" not in upper:
        return None
    idx = upper.find("SELECT")
    idx += 6
    while idx < len(stripped) and stripped[idx] in " \t\n\r":
        idx += 1
    if idx < len(stripped) and stripped[idx] == "(":
        return None
    return offset + idx


def _get_connection():
    if not DB_SERVER or not DB_NAME:
        raise DBConnectionError("Database not configured. Set DB_SERVER and DB_NAME in .env")
    if DB_TRUSTED:
        cs = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;"
        )
    else:
        cs = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASS};"
        )
    return pyodbc.connect(cs, timeout=30)


def execute_query(sql: str, valid_columns: set[str] | None = None) -> dict:
    check_not_supported(sql)
    safe_sql = validate_and_cap(sql)
    if valid_columns is not None:
        validate_columns(safe_sql, valid_columns)
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(safe_sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [list(row) for row in cursor.fetchall()]
        conn.close()
        return {
            "sql": safe_sql,
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "error": None,
        }
    except SQLValidationError:
        raise
    except DBConnectionError:
        raise
    except Exception as e:
        raise SQLQueryExecutionError(str(e))
