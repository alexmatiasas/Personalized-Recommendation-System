"""
Script to initialize the SQLite database using the provided SQL schema.
It reads the SQL commands from the init_db.sql file and applies them to the database.
"""

import sqlite3

# Path to the SQLite database and SQL initialization file
DB_PATH = "data/recommendations.db"
SQL_INIT_FILE = "scripts/init_db.sql"


def initialize_database(db_path: str, sql_file: str):
    """
    Initialize a SQLite database with the schema provided in a SQL script file.

    Args:
        db_path (str): Path to the SQLite database file.
        sql_file (str): Path to the SQL file containing the schema definition.
    """
    # Read SQL schema script
    with open(sql_file, "r") as f:
        sql_script = f.read()

    # Execute SQL script on the SQLite database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.executescript(sql_script)
        conn.commit()

    print(f"✅ Database initialized at {db_path}")


if __name__ == "__main__":
    # Run the database initialization process
    initialize_database(DB_PATH, SQL_INIT_FILE)
