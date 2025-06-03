"""
Script to convert the MovieLens 1M dataset from .dat format to .csv format.

This script reads `ratings.dat`, `users.dat`, and `movies.dat` files located in the 
`data/ml-1m/` directory, and converts them into respective CSV files: `ratings.csv`, 
`users.csv`, and `movies.csv`.

Encoding used: ISO-8859-1
Separator: '::'
"""

import pandas as pd

base_path = "data/ml-1m/"

# Convert ratings.dat to ratings.csv
ratings = pd.read_csv(
    base_path + "ratings.dat",
    sep="::",
    engine="python",
    names=["userId", "movieId", "rating", "timestamp"],
    encoding="ISO-8859-1",
)
ratings.to_csv(base_path + "ratings.csv", index=False)

# Convert users.dat to users.csv
users = pd.read_csv(
    base_path + "users.dat",
    sep="::",
    engine="python",
    names=["userId", "gender", "age", "occupation", "zip"],
    encoding="ISO-8859-1",
)
users.to_csv(base_path + "users.csv", index=False)

# Convert movies.dat to movies.csv
movies = pd.read_csv(
    base_path + "movies.dat",
    sep="::",
    engine="python",
    names=["movieId", "title", "genres"],
    encoding="ISO-8859-1",
)
movies.to_csv(base_path + "movies.csv", index=False)
