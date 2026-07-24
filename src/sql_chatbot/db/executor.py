import re
import pyodbc
import logging
from sql_chatbot.config import DB_SERVER, DB_NAME, DB_USER, DB_PASS, DB_USE_WINDOWS_AUTH


logger = logging.getLogger(__name__)
class SQLValidationError(Exception):
    pass

class SQLQueryExecutionError(Exception):
    pass

class DBConnectionError(Exception):
    pass

_SQL_KEYWORDS = frozenset(w.upper() for w in """
    SELECT FROM WHERE AND OR NOT IN AS ON JOIN LEFT RIGHT INNER OUTER FULL CROSS
    HASH SEMI ANTI SOME ANY TOP DISTINCT ORDER BY GROUP HAVING ASC DESC BETWEEN
    LIKE IS NULL TRUE FALSE CASE WHEN THEN ELSE END EXISTS
    UNION ALL INTERSECT EXCEPT WITH
    COUNT SUM AVG MIN MAX OVER PARTITION ROW_NUMBER RANK DENSE_RANK NTILE LEAD LAG
    FIRST_VALUE LAST_VALUE CUME_DIST PERCENT_RANK PERCENTILE_CONT PERCENTILE_DISC
    GETDATE DATEADD DATEDIFF YEAR MONTH DAY DATEPART CAST CONVERT
    SUBSTRING CHARINDEX LEN REPLACE UPPER LOWER TRIM ISNULL CONCAT
    DATENAME FORMAT STUFF LEFT RIGHT
    ABS ROUND CEILING FLOOR POWER IIF COALESCE NULLIF
    ISNUMERIC ISDATE EOMONTH DATEFROMPARTS DATETIMEFROMPARTS
    SIN COS TAN LOG SQRT PI EXP SIGN RAND CHOOSE
    REVERSE REPLICATE SPACE PATINDEX STRING_AGG
    TRY_CAST TRY_CONVERT TRY_PARSE
    NEWID NEWSEQUENTIALID
    SET DECLARE BEGIN END IF ELSE WHILE RETURN PRINT RAISERROR THROW
    INSERT UPDATE DELETE MERGE DROP ALTER TRUNCATE CREATE EXEC EXECUTE
    GRANT REVOKE DENY BACKUP RESTORE DBCC OPENROWSET OPENQUERY
    BULK INSERT xp_cmdshell GO
""".split())

_HARMFUL_PATTERNS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|TRUNCATE|MERGE|EXEC(?:UTE)?|"
    r"GRANT|REVOKE|CREATE|DECLARE|BACKUP|RESTORE|DBCC|"
    r"BULK\s+INSERT|OPENROWSET|OPENQUERY|xp_cmdshell)\b",
    re.IGNORECASE,
)

_SQL_IDENTIFIER = re.compile(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b')


def check_not_supported(sql: str) -> None:
    if sql.strip().upper().startswith("NOT_SUPPORTED"):
        raise SQLValidationError("This question isn't something I can answer from the database.")


def _build_alias_map(sql: str) -> dict[str, str]:
    alias_map = {}
    for m in re.finditer(
        r'\b(?:FROM|JOIN)\s+(\w+(?:\.\w+)?)\s+(?:AS\s+)?(\w{1,30})\b',
        sql, re.IGNORECASE
    ):
        table = m.group(1)
        alias = m.group(2)
        if (alias and alias.upper() not in _SQL_KEYWORDS and alias.upper() != table.upper()):
            alias_map[alias.upper()] = table
    return alias_map

def validate_columns(sql: str, valid_columns: set[str]) -> None:
    no_strings = re.sub(r"'[^']*'", "", sql)
    no_comments = re.sub(r"--.*$", "", no_strings, flags=re.MULTILINE)

    alias_map = _build_alias_map(no_comments)

    qualified = re.findall(
        r"\b(\w+)\.(\w+)\b",
        no_comments
    )

    schema_qualified_tables = set()
    for m in re.finditer(
        r'\b(?:FROM|JOIN)\s+(\w+)\.(\w+)', 
        no_comments, re.IGNORECASE
    ):
        schema_qualified_tables.add((m.group(1), m.group(2)))

    for tbl, col in qualified:
        if (tbl, col) in schema_qualified_tables:
            continue
        real_tbl = alias_map.get(tbl.upper(), tbl)
        if f"{real_tbl}.{col}" not in valid_columns:
            raise SQLValidationError(
                f"Invalid column name '{real_tbl}.{col}' — "
                "column does not exist in DATABASE CONTEXT."
            )

    # Validate only column-like identifiers, excluding SQL structure
    table_names = set(
        re.findall(
            r"\b(?:FROM|JOIN)\s+(\w+)",
            no_comments,
            flags=re.IGNORECASE,
        )
    )

    identifiers = set(
        _SQL_IDENTIFIER.findall(no_comments)
    )

    ignored = {
        token.upper()
        for token in _SQL_KEYWORDS
    }

    ignored.update(
        table.upper()
        for table in table_names
    )
    ignored.update(
        alias.upper()
        for alias in alias_map.keys())

    table_columns: dict[str, set[str]] = {}
    for vc in valid_columns:
        if "." in vc:
            tbl, col = vc.split(".", 1)
            table_columns.setdefault(tbl.lower(), set()).add(col.lower())

    query_tables = set()
    for tn in table_names:
        query_tables.add(tn.lower())
    for alias, real_tbl in alias_map.items():
        query_tables.add(real_tbl.lower())

    scoped_unqualified_columns: set[str] = set()
    for tbl in query_tables:
        scoped_unqualified_columns.update(table_columns.get(tbl, set()))

    col_aliases = set()
    for m in re.finditer(
        r'\bAS\s+(\w+)\b', no_comments, re.IGNORECASE
    ):
        col_aliases.add(m.group(1).lower())
    ignored.update(a.upper() for a in col_aliases)

    hallucinated = []

    for token in identifiers:
        if token.upper() in ignored:
            continue
        if token.lower() in scoped_unqualified_columns:
            continue
        if token.isdigit():
            continue
        try:
            float(token)
            continue
        except ValueError:
            pass

        hallucinated.append(token)
        logger.warning("DEBUG SQL: %r", sql)
        logger.warning("DEBUG ALIAS_MAP: %r", alias_map)
        logger.warning("DEBUG SCOPED_COLS SAMPLE: %r", sorted(scoped_unqualified_columns)[:30])
        logger.warning("DEBUG HALLUCINATED: %r", hallucinated)
    if hallucinated:
        raise SQLValidationError(
            f"Invalid column names found in SQL: "
            f"{', '.join(hallucinated[:5])}. "
            "These do not exist in DATABASE CONTEXT."
        )

def validate_and_cap(sql: str, max_rows: int = 100) -> str:
    stripped = sql.strip()
    if not stripped:
        raise SQLValidationError("Empty SQL statement.")

    if _HARMFUL_PATTERNS.search(stripped):
        raise SQLValidationError("Only SELECT statements are allowed.")

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
        insert_at = _find_top_insertion_point(stripped)
        if insert_at:
            kw = stripped[insert_at:].lstrip()
            if kw and not kw.upper().startswith("TOP ") and not kw.upper().startswith("TOP("):
                stripped = stripped[:insert_at] + f"TOP {max_rows} " + stripped[insert_at:]

    return stripped


def _find_top_insertion_point(sql: str) -> int | None:
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
    if DB_USE_WINDOWS_AUTH:
        cs = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_SERVER};DATABASE={DB_NAME};Trusted_Connection=yes;"
            f"TrustServerCertificate=yes;"
        )
    else:
        cs = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={DB_SERVER};DATABASE={DB_NAME};UID={DB_USER};PWD={DB_PASS};"
            f"TrustServerCertificate=yes;"
        )
    return pyodbc.connect(cs, timeout=30)


def execute_query(sql: str, valid_columns: set[str] | None = None, valid_tables: set[str] | None = None) -> dict:
    safe_sql = validate_and_cap(sql)
    check_not_supported(safe_sql)
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
