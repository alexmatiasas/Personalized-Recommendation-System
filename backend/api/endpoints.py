import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from typing import List

from fastapi import APIRouter, HTTPException, Query

from backend.models.movie import RecommendationItem, RecommendationResponse
from backend.services.recommender import ContentBasedRecommender
from backend.services.recommender import (
    get_collaborative_recommendations as service_collaborative_recommendations,
)
from backend.services.recommender import get_content_recommendations

router = APIRouter()

content_recommender = ContentBasedRecommender()
collaborative_recommender = (
    ContentBasedRecommender()
)  # or a separate CollaborativeFilteringRecommender if defined


@router.get(
    "/recommendations/content/{movie_id}",
    response_model=RecommendationResponse,
    summary="Get Content-Based Recommendations",
    tags=["Content"],
)
def get_content_based_recommendations(
    movie_id: int, top_n: int = Query(5, ge=1, le=20)
) -> RecommendationResponse:
    """
    Retrieve top-N content-based movie recommendations for a given movie ID.
    """
    try:
        recs = get_content_recommendations(movie_id=movie_id, top_n=top_n)
        items = [RecommendationItem(**r) for r in recs]
        return RecommendationResponse(
            source_id=movie_id,
            method="content_based",
            top_n=top_n,
            recommendations=items,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get(
    "/movies",
    response_model=List[RecommendationItem],
    summary="List all available movies",
    tags=["Movies"],
)
def list_all_movies():
    """
    Retrieve a list of all movies available in the system.
    Useful for populating frontend dropdowns or selectors.
    """
    try:
        items = content_recommender.get_all_movies()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/users",
    response_model=List[int],
    summary="List all valid user IDs",
    tags=["Users"],
)
def list_users() -> List[int]:
    """
    Retrieve a list of all distinct user IDs present in the ratings table.
    """
    import sqlite3

    from backend.core.config import DB_PATH

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT userId FROM ratings")
    user_rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in user_rows]


@router.get(
    "/recommendations/collaborative/{user_id}",
    response_model=RecommendationResponse,
    summary="Get Collaborative Filtering Recommendations",
    tags=["Collaborative"],
)
def get_collaborative_recommendations(
    user_id: int,
    top_n: int = Query(
        10, ge=1, le=20, description="Number of recommendations to return"
    ),
) -> RecommendationResponse:
    """
    Retrieve top-N collaborative filtering movie recommendations for a given user ID.
    """
    ids = service_collaborative_recommendations(user_id=user_id, top_n=top_n)
    items = [RecommendationItem(movieId=i) for i in ids]
    return RecommendationResponse(
        source_id=user_id,
        method="collaborative_filtering",
        top_n=top_n,
        recommendations=items,
    )


@router.get("/health", summary="Health Check")
def health_check():
    """
    Simple health check endpoint.
    """
    return {"status": "ok"}
