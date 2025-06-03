import os
import sys

import pandas as pd
import pytest

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.content_based import ContentBasedRecommender


@pytest.fixture
def recommender():
    df = pd.DataFrame(
        {
            "movieId": [1, 2],
            "title": ["Toy Story (1995)", "Jumanji (1995)"],
            "overview": ["A story about toys.", "A magical board game."],
            "genres": ["Animation|Children|Comedy", "Adventure|Children|Fantasy"],
        }
    )
    model = ContentBasedRecommender(df)
    model.fit()
    return model


def test_recommendations_exist(recommender):
    """
    Test that the content-based recommender returns a non-empty list of movie titles
    given a known movie title from the dataset.
    """
    movie_title = "Toy Story (1995)"
    results = recommender.get_recommendations(movie_title, top_n=5)

    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(title, str) for title in results)
    print(f"\n✅ Recommendations for '{movie_title}':")
    for i, title in enumerate(results, 1):
        print(f"{i}. {title}")
