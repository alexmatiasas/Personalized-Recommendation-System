import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.collaborative_filtering import CollaborativeFilteringRecommender


def test_recommender_instantiation():
    recommender = CollaborativeFilteringRecommender(
        "data/ml-1m/ratings.csv", "data/processed/enriched_movies.csv"
    )
    assert recommender is not None
