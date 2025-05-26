import os
import sys

import pandas as pd
import pytest

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.content_based import ContentBasedRecommender


@pytest.fixture
def recommender():
    df = pd.read_csv("data/processed/enriched_movies_clean.csv")
    model = ContentBasedRecommender(df)
    model.fit()
    return model


def test_recommendations_exist(recommender):
    movie_title = "Toy Story (1995)"
    results = recommender.get_recommendations(movie_title, top_n=5)

    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(title, str) for title in results)
    print(f"\n✅ Recommendations for '{movie_title}':")
    for i, title in enumerate(results, 1):
        print(f"{i}. {title}")
