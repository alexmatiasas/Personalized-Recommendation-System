import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """
    Test that the health check endpoint returns status 200 and the correct payload.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_movies():
    """
    Test that the /movies endpoint returns a list of movies with expected keys.
    """
    response = client.get("/movies")
    assert response.status_code == 200
    movies = response.json()
    assert isinstance(movies, list)
    assert len(movies) > 0
    first = movies[0]
    assert "movieId" in first and "title" in first


def test_list_users():
    """
    Test that the /users endpoint returns a non-empty list of integer user IDs.
    """
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert all(isinstance(u, int) for u in users)
    assert len(users) > 0


def test_content_recommendations():
    """
    Test that content-based recommendations endpoint returns correct schema and count.
    """
    movie_id = 1
    top_n = 5
    response = client.get(f"/recommendations/content/{movie_id}?top_n={top_n}")
    assert response.status_code == 200
    payload = response.json()
    # Validate top-level structure
    assert payload["source_id"] == movie_id
    assert payload["method"] == "content_based"
    assert payload["top_n"] == top_n
    recs = payload["recommendations"]
    assert isinstance(recs, list) and len(recs) == top_n
    # Validate one recommendation item
    item = recs[0]
    assert set(item.keys()) >= {"movieId", "title", "genres", "similarity"}


def test_collaborative_recommendations():
    """
    Test that collaborative filtering recommendations endpoint returns a list of ints.
    """
    user_id = 1
    top_n = 5
    response = client.get(f"/recommendations/collaborative/{user_id}?top_n={top_n}")
    assert response.status_code == 200
    payload = response.json()
    # Validate top-level structure
    assert payload["source_id"] == user_id
    assert payload["method"] == "collaborative_filtering"
    assert payload["top_n"] == top_n
    recs = payload["recommendations"]
    assert isinstance(recs, list) and len(recs) == top_n
    # Validate that each recommendation item has a movieId int
    assert all(isinstance(item.get("movieId"), int) for item in recs)


def test_collaborative_invalid_user_fallback():
    """
    Test that requesting recommendations for a non-existent user returns fallback list.
    """
    user_id = 999
    top_n = 3
    response = client.get(f"/recommendations/collaborative/{user_id}?top_n={top_n}")
    assert response.status_code == 200
    payload = response.json()
    # Even for invalid users, the schema should match
    assert payload["source_id"] == user_id
    assert payload["method"] == "collaborative_filtering"
    assert payload["top_n"] == top_n
    recs = payload["recommendations"]
    assert isinstance(recs, list) and len(recs) == top_n
    assert all(isinstance(item.get("movieId"), int) for item in recs)
