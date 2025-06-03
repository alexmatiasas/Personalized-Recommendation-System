"""
This script loads enriched movie data, user ratings, and user information into a SQLite database.
It assumes the presence of:
- A processed dataset at data/processed/enriched_movies_clean.csv
- Original MovieLens data at data/ml-1m/
- A schema definition in scripts/init_db.sql

The resulting database is saved as data/recommendations.db.
"""

import sqlite3

import pandas as pd


def load_data_to_db():
    """
    Load movie, ratings, and user data into the SQLite database.

    Steps:
    1. Load enriched movie metadata from a processed CSV file.
    2. Connect to a local SQLite database and initialize its schema using a SQL script.
    3. Insert the enriched movie data into the 'movies' table.
    4. Insert raw ratings data from MovieLens into the 'ratings' table.
    5. Insert distinct users into the 'users' table.
    """
    # Load the enriched movies data
    df = pd.read_csv("data/processed/enriched_movies_clean.csv")

    # Connect to the SQLite database
    conn = sqlite3.connect("data/recommendations.db")
    cursor = conn.cursor()

    # Initialize the database schema
    with open("scripts/init_db.sql", "r") as f:
        cursor.executescript(f.read())

    # Insert enriched movie data
    df.to_sql("movies", conn, if_exists="append", index=False)
    print(f"✅ Inserted {len(df)} records into 'movies' table.")

    # Insert ratings from the original MovieLens dataset
    ratings_df = pd.read_csv("data/ml-1m/ratings.csv")
    ratings_df.to_sql("ratings", conn, if_exists="append", index=False)
    print(f"✅ Inserted {len(ratings_df)} records into 'ratings' table.")

    # Insert unique users from the users.csv file
    users_df = pd.read_csv("data/ml-1m/users.csv")[["userId"]].drop_duplicates()
    users_df.to_sql("users", conn, if_exists="append", index=False)
    print(f"✅ Inserted {len(users_df)} records into 'users' table.")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    load_data_to_db()
