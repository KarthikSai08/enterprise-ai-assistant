import re
import pyodbc
import sqlglot
from sqlglot import exp
import logging
from sql_chatbot.config import DB_SERVER, DB_NAME, DB_USER, DB_PASS, DB_USE_WINDOWS_AUTH


logger = logging.getLogger(__name__)
class SQLValidationError(Exception):
    pass

class SQLQueryExecutionError(Exception):
    pass

class DBConnectionError(Exception):
    pass

_FORBIDDEN_STATEMENTS = (
    exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Alter,
    exp.Create, exp.Grant, exp.Command, exp.TruncateTable
)

def check_not_supported(sql: str) -> None:
    if sql.strip().upper().startswith("NOT_SUPPORTED"):
        raise SQLValidationError("This question isn't something I can answer from the database.")


def _parse_single_select(sql: str) ->exp.Select:
    try:
        statements = [s for s in sqlglot.parse(sql, read= "tsql") if s is not None]
    except Exception as e:
        raise SQLValidationError(f"SQL failed to parse : {e}")

    if len(statements) == 0:
        raise SQLValidationError("Empty SQL Statement")
    if len(statements) > 1:
        raise SQLValidationError("Only a single statement is allowed - no batch separators or semicolons")

    tree = statements[0]

    if isinstance(tree, _FORBIDDEN_STATEMENTS) or not isinstance(tree, exp.Select):
        raise SQLValidationError("Only SELECT statements are allowed")

    if tree.find(exp.With):
        raise SQLValidationError("CTEs (WITH .... AS) are not allowed")
    if tree.find(exp.Union) or tree.find(exp.Intersect) or tree.find(exp.Except):
        raise SQLValidationError("UNION/INTERSECT/EXCEPT are not allowed")
    if tree.find(exp.Pivot):
        raise SQLValidationError("PIVOT/UNPIVOT are not allowed")

    return tree

def _validate_columns_ast(tree: exp.Select, valid_columns : set[str]) -> None:
    lower_valid = {vc.lower() for vc in valid_columns}

    alias_to_table : dict[str, str] = {}
    query_tables: set[str] = set()
    for t in tree.find_all(exp.Table):
        real_name = t.name
        query_tables.add(real_name.lower())
        if t.alias:
            alias_to_table[t.alias.lower()] = real_name

    select_aliases = {a.alias.lower() for a in tree.find_all(exp.Alias) if a.alias}

    table_columns: dict[str, set[str]] = {}
    for vc in valid_columns:
        if "." in vc:
            tbl, col = vc.split(".", 1)
            table_columns.setdefault(tbl.lower(), set()).add(col.lower())

    scoped_unqualified: set[str] = set()
    for tbl in query_tables:
        scoped_unqualified.update(table_columns.get(tbl, set()))

    hallucinated = []
    for c in tree.find_all(exp.Column):
        col_name = c.name
        if col_name.lower() in select_aliases:
            continue

        table_ref = c.table
        if table_ref:
            real_tbl = alias_to_table.get(table_ref.lower(), table_ref)
            if f"{real_tbl}.{col_name}".lower()not in lower_valid:
                hallucinated.append(f"{real_tbl}.{col_name}")
        else:
            if col_name.lower() not in scoped_unqualified:
                hallucinated.append(col_name)

    if hallucinated:
        logger.warning("DEBUG SQL AST: %r", tree.sql(dialect="tsql"))
        logger.warning("DEBUG HALLUCIATED : %r", hallucinated)
        raise SQLValidationError(
            f"Invalid column names found in SQL: {', '.join(hallucinated[:5])}. "
            "These do not exist in DATABASE CONTEXT"
        )
    
def _cap_top(tree: exp.Select, max_rows: int = 100) -> str:
    if not tree.args.get("limit"):
        tree = tree.limit(max_rows)
    return tree.sql(dialect = "tsql")

def validate_and_cap(sql: str, valid_columns: set[str] | None, max_rows: int = 100) -> str:
    tree = _parse_single_select(sql)
    if valid_columns is not None:
        _validate_columns_ast(tree, valid_columns)
    return _cap_top(tree, max_rows)

def _get_collection():
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
    return pyodbc.connect(cs, timeout=60)

def execute_query(sql: str, valid_columns: set[str] | None = None, valid_tables: set[str] | None = None) -> dict:
    check_not_supported(sql)
    safe_sql = validate_and_cap(sql, valid_columns)
    try:
        conn = _get_collection()
        cursor = conn.cursor()
        cursor.execute(safe_sql)
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        rows = [list(row) for row in cursor.fetchall()]
        conn.close()
        return {
            "sql" : safe_sql,
            "columns" : columns,
            "rows" : rows,
            "row_count" : len(rows),
            "error" : None
        }
    except SQLValidationError:
        raise
    except DBConnectionError:
        raise
    except Exception as e:
        raise SQLQueryExecutionError(str(e))
