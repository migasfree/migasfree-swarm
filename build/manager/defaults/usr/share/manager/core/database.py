import psycopg2
from contextlib import contextmanager
from core.config import (
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_PASSWORD,
)


@contextmanager
def get_db_connection(host=None, port=None, user=None, password=None, dbname=None):
    """
    Get a database connection.
    This is a synchronous connection using psycopg2.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=dbname or POSTGRES_DB,
            user=user or POSTGRES_USER,
            password=password or POSTGRES_PASSWORD,
            host=host or POSTGRES_HOST,
            port=port or POSTGRES_PORT,
            connect_timeout=3,
        )
        yield conn
    finally:
        if conn:
            conn.close()
