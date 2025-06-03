"""
This module provides utility functions for interacting with a local SQLite database.
It defines a default database path and functions for executing SELECT queries and
retrieving data either as a single row or a list of rows.
"""

import sqlite3
from typing import Any, List, Tuple

DB_PATH = "data/recommendations.db"  # Puedes parametrizar esto si prefieres


def get_connection(db_path: str = DB_PATH):
    """
    Establishes and returns a connection to the specified SQLite database.

    Args:
        db_path (str): Path to the SQLite database file. Defaults to DB_PATH.

    Returns:
        sqlite3.Connection: A connection object to the SQLite database.
    """
    return sqlite3.connect(db_path)


def fetch_all(query: str, params: Tuple = ()) -> List[Tuple[Any]]:
    """
    Executes a SELECT query and fetches all resulting rows.

    Args:
        query (str): The SQL query to execute.
        params (Tuple, optional): The parameters to substitute into the SQL query.

    Returns:
        List[Tuple[Any]]: A list of tuples representing the rows returned by the query.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def fetch_one(query: str, params: Tuple = ()) -> Tuple[Any] | None:
    """
    Executes a SELECT query and fetches a single row.

    Args:
        query (str): The SQL query to execute.
        params (Tuple, optional): The parameters to substitute into the SQL query.

    Returns:
        Tuple[Any] | None: A single tuple representing the row returned by the query,
                           or None if no result is found.
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
