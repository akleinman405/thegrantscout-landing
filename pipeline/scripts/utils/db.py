"""
Database connection module for Pipeline v2.

Provides connection pooling and helper functions for PostgreSQL access.
"""
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

import pandas as pd
import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

# Load .env from Pipeline root
PIPELINE_ROOT = Path(__file__).parent.parent.parent
load_dotenv(PIPELINE_ROOT / ".env")

# Connection pool (initialized on first use)
_pool: Optional[pool.ThreadedConnectionPool] = None

# Default schema
DEFAULT_SCHEMA = 'f990_2025'


def init_pool(minconn: int = 1, maxconn: int = 10) -> None:
    """
    Initialize the database connection pool.

    Args:
        minconn: Minimum connections to maintain
        maxconn: Maximum connections allowed
    """
    global _pool

    if _pool is not None:
        return  # Already initialized

    _pool = pool.ThreadedConnectionPool(
        minconn=minconn,
        maxconn=maxconn,
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', '5432')),
        database=os.getenv('DB_NAME', 'thegrantscout'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        options=f'-c search_path={DEFAULT_SCHEMA},public'
    )


def get_pool() -> pool.ThreadedConnectionPool:
    """Get the connection pool, initializing if needed."""
    global _pool
    if _pool is None:
        init_pool()
    return _pool


@contextmanager
def get_connection():
    """
    Context manager for database connections.

    Usage:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")

    Yields:
        psycopg2 connection object
    """
    conn = None
    try:
        conn = get_pool().getconn()
        yield conn
        conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            get_pool().putconn(conn)


def query_df(sql: str, params: dict = None) -> pd.DataFrame:
    """
    Execute a query and return results as a pandas DataFrame.

    Args:
        sql: SQL query (can use %(param)s syntax for parameters)
        params: Dictionary of parameters

    Returns:
        pandas DataFrame with query results
    """
    with get_connection() as conn:
        return pd.read_sql(sql, conn, params=params)


def execute(sql: str, params: dict = None) -> None:
    """
    Execute a SQL statement (for inserts, updates, DDL).

    Args:
        sql: SQL statement
        params: Dictionary of parameters
    """
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(sql, params)


def close_pool() -> None:
    """Close all connections in the pool."""
    global _pool
    if _pool:
        _pool.closeall()
        _pool = None
