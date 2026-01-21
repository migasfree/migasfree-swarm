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
def get_db_connection():
    """
    Get a database connection.
    This is a synchronous connection using psycopg2.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname=POSTGRES_DB,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
        )
        yield conn
    finally:
        if conn:
            conn.close()
