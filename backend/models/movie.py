"""
This module defines the data models used for API responses related to movie recommendations.
"""

from typing import List, Optional

from pydantic import BaseModel


class RecommendationItem(BaseModel):
    """
    Represents a single recommended movie item.

    Attributes:
        movieId (int): The unique identifier of the recommended movie.
        title (Optional[str]): The title of the recommended movie.
        genres (Optional[str]): A comma-separated string of genres associated with the movie.
        similarity (Optional[float]): The similarity score between the input movie and the recommended movie.
    """

    movieId: int
    title: Optional[str] = None
    genres: Optional[str] = None
    similarity: Optional[float] = None


class RecommendationResponse(BaseModel):
    """
    Represents the response model for recommendations.

    Attributes:
        source_id (int): The ID of the movie or user for which recommendations are generated.
        method (str): The recommendation method used (e.g., 'content_based', 'collaborative_filtering').
        top_n (int): The number of top recommendations returned.
        recommendations (List[RecommendationItem]): A list of recommended movie items.
    """

    source_id: int
    method: str
    top_n: int
    recommendations: List[RecommendationItem]
