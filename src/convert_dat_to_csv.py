import pandas as pd

base_path = "data/ml-1m/"

# ratings.dat
ratings = pd.read_csv(
    base_path + "ratings.dat",
    sep="::",
    engine="python",
    names=["userId", "movieId", "rating", "timestamp"],
    encoding="ISO-8859-1"
)
ratings.to_csv(base_path + "ratings.csv", index=False)

# users.dat
users = pd.read_csv(
    base_path + "users.dat",
    sep="::",
    engine="python",
    names=["userId", "gender", "age", "occupation", "zip"],
    encoding="ISO-8859-1"
)
users.to_csv(base_path + "users.csv", index=False)

# movies.dat
movies = pd.read_csv(
    base_path + "movies.dat",
    sep="::",
    engine="python",
    names=["movieId", "title", "genres"],
    encoding="ISO-8859-1"
)
movies.to_csv(base_path + "movies.csv", index=False)