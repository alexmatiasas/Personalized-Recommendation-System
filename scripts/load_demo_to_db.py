"""
This script loads demo movie data and user ratings into a SQLite database for the demo version.
It assumes the presence of:
- A reduced enriched dataset at data/demo/enriched_movies.csv
- A reduced ratings file at data/demo/ratings.csv
- A schema definition in scripts/init_db.sql

The resulting database is saved as data/demo/recommendations.db.
"""

import sqlite3

import pandas as pd


def load_demo_data_to_db():
    """
    Load reduced movie and ratings data into a SQLite database for demo purposes.

    Steps:
    1. Load enriched movie metadata from demo CSV.
    2. Connect to a demo SQLite database and initialize schema.
    3. Insert data into 'movies', 'ratings', and 'users' tables.
    """
    # Load the enriched movies data (demo version)
    df = pd.read_csv("data/demo/enriched_movies.csv")

    # Connect to the demo SQLite database
    conn = sqlite3.connect("data/demo/recommendations.db")
    cursor = conn.cursor()

    # Initialize the database schema
    with open("scripts/init_db.sql", "r") as f:
        cursor.executescript(f.read())

    # Insert enriched movie data
    df.to_sql("movies", conn, if_exists="append", index=False)
    print(f"✅ Inserted {len(df)} records into 'movies' table.")

    # Insert ratings (demo version)
    ratings_df = pd.read_csv("data/demo/ratings.csv")
    ratings_df.to_sql("ratings", conn, if_exists="append", index=False)
    print(f"✅ Inserted {len(ratings_df)} records into 'ratings' table.")

    # Extract unique users from ratings
    users_df = ratings_df[["userId"]].drop_duplicates()
    users_df.to_sql("users", conn, if_exists="append", index=False)
    print(f"✅ Inserted {len(users_df)} records into 'users' table.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    load_demo_data_to_db()
