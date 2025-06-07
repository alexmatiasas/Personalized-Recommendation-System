from pathlib import Path

import pandas as pd

# Paths
ratings_path = Path("data/ml-1m/ratings.csv")
enriched_movies_path = Path("data/processed/enriched_movies_clean.csv")
output_dir = Path("data/demo")
output_dir.mkdir(parents=True, exist_ok=True)

# Parameters
NUM_USERS = 20  # You can adjust this number depending on memory limits

# Load data
print("🔄 Loading original ratings and movie metadata...")
ratings_df = pd.read_csv(ratings_path)
enriched_df = pd.read_csv(enriched_movies_path)

# Filter ratings
selected_users = ratings_df["userId"].unique()[:NUM_USERS]
filtered_ratings = ratings_df[ratings_df["userId"].isin(selected_users)]

# Filter enriched movies
filtered_movie_ids = filtered_ratings["movieId"].unique()
filtered_enriched = enriched_df[enriched_df["movieId"].isin(filtered_movie_ids)]

# Save reduced datasets
print(f"💾 Saving reduced ratings and movies to {output_dir}...")
filtered_ratings.to_csv(output_dir / "ratings.csv", index=False)
filtered_enriched.to_csv(output_dir / "enriched_movies.csv", index=False)

print("✅ Demo dataset saved successfully.")
