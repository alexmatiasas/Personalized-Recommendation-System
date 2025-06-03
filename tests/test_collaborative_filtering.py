import os
import sys

import pandas as pd
import pytest

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.collaborative_filtering import CollaborativeFilteringRecommender


def test_recommender_instantiation_from_memory():
    # Create a small dummy ratings DataFrame
    ratings_df = pd.DataFrame(
        {
            "userId": [1, 1, 2, 2, 3],
            "movieId": [10, 20, 10, 30, 20],
            "rating": [4, 5, 3, 2, 5],
        }
    )

    # Create a small dummy enriched movies DataFrame
    enriched_df = pd.DataFrame(
        {
            "movieId": [10, 20, 30],
            "title": ["Movie A", "Movie B", "Movie C"],
            "overview": ["Overview A", "Overview B", "Overview C"],
            "genres": ["Action", "Drama", "Comedy"],
        }
    )

    recommender = CollaborativeFilteringRecommender()
    recommender.load_data(ratings_df=ratings_df, enriched_df=enriched_df)
    recommender.build_user_item_matrix()
    recommender.compute_user_similarity()

    assert recommender.user_item_matrix is not None
    assert recommender.user_item_matrix.shape == (3, 3)

    recs = recommender.recommend_movies_for_user(user_id=1, exclude_watched=True)
    assert isinstance(recs, list)


# Additional tests
def test_recommendation_for_invalid_user():
    """
    Test that requesting recommendations for a non-existent user raises a ValueError.
    """
    ratings_df = pd.DataFrame(
        {
            "userId": [1, 2],
            "movieId": [10, 20],
            "rating": [4, 5],
        }
    )
    enriched_df = pd.DataFrame(
        {
            "movieId": [10, 20],
            "title": ["Movie A", "Movie B"],
            "overview": ["Overview A", "Overview B"],
            "genres": ["Action", "Drama"],
        }
    )

    recommender = CollaborativeFilteringRecommender()
    recommender.load_data(ratings_df=ratings_df, enriched_df=enriched_df)
    recommender.build_user_item_matrix()
    recommender.compute_user_similarity()

    with pytest.raises(ValueError, match="User ID 999 not found in dataset"):
        recommender.recommend_movies_for_user(user_id=999)


def test_empty_dataframes():
    """
    Test that the recommender raises a ValueError when provided with empty input DataFrames.
    """
    ratings_df = pd.DataFrame(columns=["userId", "movieId", "rating"])
    enriched_df = pd.DataFrame(columns=["movieId", "title", "overview", "genres"])

    recommender = CollaborativeFilteringRecommender()
    recommender.load_data(ratings_df=ratings_df, enriched_df=enriched_df)
    recommender.build_user_item_matrix()

    with pytest.raises(ValueError, match="Similarity matrix not computed"):
        recommender.recommend_movies_for_user(user_id=1)
