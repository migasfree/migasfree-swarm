import os
import re
import logging
import psycopg2
import psycopg2.pool
from psycopg2.extras import DictCursor
from resources import read_file

logger = logging.getLogger("migasfree-mcp")


def get_secret_pass():
    stack = os.environ.get("STACK", "migasfree")
    secret_path = f"/run/secrets/{stack}_superadmin_pass"
    if os.path.exists(secret_path):
        return read_file(secret_path).strip()
    return os.getenv("POSTGRES_PASSWORD", "migasfree")


DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "database"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "migasfree"),
    "user": os.getenv("POSTGRES_USER", "migasfree"),
    "password": get_secret_pass(),
}

# Connection pool: min 1, max 10 connections
_pool = None


def _get_pool():
    global _pool
    if _pool is None or _pool.closed:
        try:
            _pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                **DB_CONFIG,
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            _pool = None
            raise
    return _pool


def get_connection():
    """Get a connection from the pool."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        # Ensure clean state: rollback any pending transaction, then set autocommit
        conn.rollback()
        conn.autocommit = True
        # Test if connection is alive
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
        # Connection is dead, close and get a fresh one
        logger.warning("Stale DB connection detected, reconnecting...")
        try:
            pool.putconn(conn, close=True)
        except Exception:
            pass
        conn = pool.getconn()
        conn.autocommit = True
    return conn


def release_connection(conn):
    """Return a connection to the pool."""
    try:
        pool = _get_pool()
        pool.putconn(conn)
    except Exception:
        logger.debug("Error returning connection to pool")


# Regex to detect multiple statements (semicolons outside of strings)
_MULTI_STATEMENT_RE = re.compile(
    r""";\s*(?=(?:[^']*'[^']*')*[^']*$)""",
    re.DOTALL,
)

# Forbidden keywords pattern (word boundaries, case-insensitive)
_FORBIDDEN_KEYWORDS = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|EXECUTE|COPY|"
    r"SET\s+ROLE|SET\s+SESSION|DO\s+\$|CALL|PERFORM)\b",
    re.IGNORECASE,
)

# Strip SQL comments
_SQL_COMMENT_RE = re.compile(
    r"(--[^\n]*|/\*.*?\*/)",
    re.DOTALL,
)


def _validate_sql(query: str) -> None:
    """Validate that a SQL query is a safe SELECT/EXPLAIN statement."""
    # Remove comments to prevent comment-based bypasses
    clean_query = _SQL_COMMENT_RE.sub(" ", query).strip()

    if not clean_query:
        raise ValueError("Empty query")

    # Must start with SELECT or EXPLAIN
    first_word = clean_query.split()[0].upper()
    if first_word not in ("SELECT", "EXPLAIN", "WITH"):
        raise ValueError("Only SELECT, EXPLAIN, and WITH (CTE) queries are allowed")

    # Check for multiple statements
    statements = [
        s.strip() for s in _MULTI_STATEMENT_RE.split(clean_query) if s.strip()
    ]
    if len(statements) > 1:
        raise ValueError("Multiple SQL statements are not allowed")

    # Check for forbidden keywords
    match = _FORBIDDEN_KEYWORDS.search(clean_query)
    if match:
        raise ValueError(f"Forbidden keyword: {match.group(0)}")


def run_sql_select_query(query: str) -> list:
    """Execute a validated SELECT query and return results as a list of dicts."""
    _validate_sql(query)

    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        return {"ERROR": str(e)}
    finally:
        release_connection(conn)


# Schema cache: loaded once, reused forever (schema only changes on redeploy)
_schema_cache = None


def get_db_schema():
    """Returns the database schema (cached in memory after first call)."""
    global _schema_cache
    if _schema_cache is not None:
        return _schema_cache

    logger.info("Loading database schema into cache...")
    schema = _fetch_db_schema()
    if not isinstance(schema, dict) or "ERROR" not in schema:
        _schema_cache = schema
    return schema


def clear_schema_cache():
    """Clear the cached schema (useful after DB migrations)."""
    global _schema_cache
    _schema_cache = None
    logger.info("Database schema cache cleared")


def _fetch_db_schema():
    """Fetches the database schema from PostgreSQL."""
    query_tables = """
        SELECT t.table_name, obj_description(c.oid) as description
        FROM information_schema.tables t
        LEFT JOIN pg_class c ON c.relname = t.table_name
        WHERE t.table_schema = 'public'
          AND t.table_type = 'BASE TABLE'
          AND t.table_name NOT LIKE 'django_%'
          AND t.table_name NOT LIKE 'auth_%'
        ORDER BY t.table_name;
    """

    tables = run_sql_select_query(query_tables)
    if isinstance(tables, dict) and "ERROR" in tables:
        return tables

    schema = {}
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            for table in tables:
                tname = table["table_name"]
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position;
                    """,
                    (tname,),
                )
                cols = [dict(r) for r in cur.fetchall()]
                schema[tname] = {"description": table["description"], "columns": cols}
    except Exception as e:
        return {"ERROR": str(e)}
    finally:
        release_connection(conn)

    return schema
