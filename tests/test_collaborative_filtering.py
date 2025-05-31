import os
import sys

import pandas as pd

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
