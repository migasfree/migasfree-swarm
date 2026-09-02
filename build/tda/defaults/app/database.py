"""
Database connection module for TDA service.

Reuses the same pattern as the MCP server: reads credentials from
Docker Secrets via POSTGRES_PASSWORD_FILE, connects with psycopg2.
"""

import os
import logging

import psycopg2
import psycopg2.pool
from psycopg2.extras import DictCursor

logger = logging.getLogger("migasfree-tda")


def _get_secret_pass():
    """Read the PostgreSQL password from the Docker Secret file."""
    secret_path = os.environ.get("POSTGRES_PASSWORD_FILE")
    if secret_path and os.path.exists(secret_path):
        with open(secret_path, "r") as f:
            return f.read().strip()
    raise ValueError(
        f"POSTGRES_PASSWORD_FILE not set or not found ({secret_path})"
    )


DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "database"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "migasfree"),
    "user": os.getenv("POSTGRES_USER", "migasfree"),
    "password": _get_secret_pass(),
}

_pool = None


def _get_pool():
    global _pool
    if _pool is None or _pool.closed:
        try:
            _pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=5,
                **DB_CONFIG,
            )
            logger.info("TDA database connection pool created")
        except Exception as e:
            logger.error(f"Error creating connection pool: {e}")
            _pool = None
            raise
    return _pool


def get_connection():
    """Get a connection from the pool, verifying it is alive."""
    pool = _get_pool()
    conn = pool.getconn()
    try:
        conn.rollback()
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
    except (psycopg2.OperationalError, psycopg2.InterfaceError):
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


def query_dataframe(sql, params=None):
    """Execute a SELECT query and return results as a pandas DataFrame."""
    import pandas as pd

    conn = get_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    finally:
        release_connection(conn)
