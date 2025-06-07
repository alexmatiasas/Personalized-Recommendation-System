"""
Streamlit-based web application for a movie recommender system.
Supports both content-based and collaborative filtering approaches.
Logs user feedback and displays movie data enriched with TMDB metadata.
"""

import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from pymongo import MongoClient

from src.content_based import ContentBasedRecommender
from src.db.repository import get_all_movies
from src.db.sqlite_client import get_connection
from src.services.recommender_service import get_user_recommendations
from src.ui.components import generate_genre_html, generate_rating_html
from src.ui.helpers import load_similarity, normalize_title
from src.ui.tmdb import get_movie_trailer_url

load_dotenv()

DATA_MODE = os.getenv("DATA_MODE", "full").lower()
BASE_DIR = Path("data")
DATA_DIR = BASE_DIR / ("demo" if DATA_MODE == "demo" else "ml-1m")
# Define the directory for processed matrices
MATRIX_DIR = BASE_DIR / ("processed_demo" if DATA_MODE == "demo" else "processed")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    st.error(
        "⚠️ No se ha definido la variable de entorno MONGO_URI. Verifica tu archivo .env o configuración en Render."
    )
    st.stop()
base_url = "https://image.tmdb.org/t/p/w500/"


def log_feedback(
    user_id: int, recommended_movies: list, method: str, source_movie: str = None
):
    """
    Log user feedback into MongoDB.

    Parameters:
        user_id (int): The ID of the user giving feedback.
        recommended_movies (list): List of recommended movie titles.
        method (str): The recommendation method used.
        source_movie (str, optional): The movie from which recommendations were generated (for content-based).
    """
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.server_info()  # force connection to check for errors
        db = client["recommender_logs"]
    except Exception as e:
        st.error(f"MongoDB connection failed: {e}")
        return
    feedback_collection = db["user_feedback"]
    feedback_collection.insert_one(
        {
            "user_id": user_id,
            "method": method,
            "recommended_movies": recommended_movies,
            "timestamp": datetime.now(timezone.utc),
            "source_movie": source_movie,
        }
    )


@st.cache_resource
def load_similarity_cached(path: str = str(MATRIX_DIR / "user_similarity.joblib")):
    """
    Load user similarity matrix from a cached file.

    Parameters:
        path (str): Path to the joblib file.

    Returns:
        object: Loaded similarity matrix object.
    """
    return load_similarity(path)


st.title("🎬 Movie Recommender System")
if DATA_MODE == "demo":
    st.markdown(
        "<div style='background-color:#444;padding:10px;border-radius:8px;margin-bottom:15px;'>"
        "<strong style='color:#efb810;'>⚠️ Demo Mode Enabled:</strong> "
        "The app is using a reduced dataset with 20 users and 1100+ movies for live preview purposes."
        "</div>",
        unsafe_allow_html=True,
    )

# Sidebar options
option = st.sidebar.selectbox(
    "Choose Recommender:", ("Content-Based", "Collaborative Filtering")
)

# --- Content-Based Recommender Workflow ---
if option == "Content-Based":

    @st.cache_resource
    def load_movies_from_db():
        """
        Load movie data from the SQLite database.

        Returns:
            pd.DataFrame: DataFrame containing all movies with metadata.
        """
        conn = get_connection(str(DATA_DIR / "recommendations.db"))
        rows = get_all_movies(conn)
        return pd.DataFrame(
            rows,
            columns=[
                "movieId",
                "title",
                "genres",
                "overview",
                "poster_path",
                "vote_average",
                "popularity",
            ],
        )

    movies_df = load_movies_from_db()

    @st.cache_resource
    def fit_recommender():
        """
        Fit the content-based recommender using the loaded movie dataset.

        Returns:
            ContentBasedRecommender: Fitted recommender instance.
        """
        recommender = ContentBasedRecommender(movies_df)
        recommender.fit()
        return recommender

    st.markdown("---")

    movie_options = movies_df["title"].apply(normalize_title)
    movie_labels = movie_options.apply(lambda x: x[0])
    movie_title = st.selectbox("Choose a Movie Title", sorted(movie_labels.unique()))

    if not movie_title:
        st.warning("⚠️ Please select a movie first.")
        st.stop()

    # Find the true movie row based on the normalized title
    # (since dropdown is normalized, match accordingly)
    selected_movie = movies_df[
        movies_df["title"].apply(lambda t: normalize_title(t)[0] == movie_title)
    ].iloc[0]
    st.markdown("### 🎞️ Selected Movie")
    with st.container():
        # Try to extract year for display if present
        year = ""
        if "(" in selected_movie["title"] and ")" in selected_movie["title"]:
            try:
                year = selected_movie["title"].split("(")[1].replace(")", "")
            except Exception:
                year = ""
        try:
            genres = (
                eval(selected_movie["genres"])
                if isinstance(selected_movie["genres"], str)
                else selected_movie["genres"]
            )
        except Exception:
            genres = []
        genre_html = generate_genre_html(genres)
        score = selected_movie["vote_average"]
        score_html = generate_rating_html(score)
    poster_path = selected_movie["poster_path"] or ""
    img_src = (
        base_url + poster_path
        if poster_path
        else "https://via.placeholder.com/120x180?text=No+Image"
    )
    st.markdown(
        """
        <div style='background-color:#1a1a40; padding:20px; border-radius:12px; margin-bottom:25px; display: flex; align-items: flex-start; box-shadow: 0 6px 12px rgba(0,0,0,0.3);'>
            <img src="{}" style="width:140px; height:auto; border-radius:5px; margin-right:25px;" />
            <div style="flex:1;">
                <h3 style='margin-bottom:5px; color:#efb810;'>🎬 {}</h3>
                <p style='margin-top:0; color:#bbb; font-size:14px;'>📅 {}</p>
                <div style='margin:5px 0;'>
                    <strong style='color:#e0e0e0;'>Genres:</strong>
                    {}
                </div>
                <p style='margin:5px 0; color:#e0e0e0;'>{}</p>
                <div style='margin:5px 0;'>
                    <strong style='color:#e0e0e0;'>Rating:</strong> {}
                </div>
                {}
                <p style='margin-top:10px;'>
                  <a href="https://www.themoviedb.org/search?query={}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                </p>
            </div>
        </div>
        """.format(
            img_src,
            normalize_title(selected_movie["title"])[0],
            year,
            genre_html,
            selected_movie["overview"],
            score_html,
            (
                "<p style='font-size:12px; color:gray; margin:0;'>Based on TMDB user ratings</p>"
                if score_html != 0
                else ""
            ),
            normalize_title(selected_movie["title"])[0].replace(" ", "%20"),
        ),
        unsafe_allow_html=True,
    )
    trailer_url = get_movie_trailer_url(normalize_title(selected_movie["title"])[0])
    if trailer_url:
        st.markdown("### 🎬 Watch Trailer")
        st.video(trailer_url)

    top_n = st.slider("How many recommendations?", min_value=1, max_value=10, value=5)
    if st.button("Get Recommendations", key="cb_button"):
        recommender = fit_recommender()
        recs = recommender.get_recommendations(selected_movie["title"], top_n=top_n)
        recommended_ids = movies_df[movies_df["title"].isin(recs)]["movieId"].tolist()
        recommended_titles = movies_df[movies_df["movieId"].isin(recommended_ids)][
            "title"
        ].tolist()
        log_feedback(
            user_id=-1,
            recommended_movies=recommended_titles,
            method="content_based",
            source_movie=selected_movie["title"],
        )
        st.subheader("🎯 Recommended Movies")
        # Include poster_path for image display
        recommended_df = movies_df[movies_df["title"].isin(recs)][
            ["title", "genres", "overview", "poster_path", "vote_average", "popularity"]
        ]

        for _, row in recommended_df.iterrows():
            title_normalized = normalize_title(row["title"])[0].replace(" ", "%20")
            with st.container():
                title, year = normalize_title(row["title"])
                try:
                    genres = (
                        eval(row["genres"])
                        if isinstance(row["genres"], str)
                        else row["genres"]
                    )
                except Exception:
                    genres = []
                genre_html = generate_genre_html(genres)
                score = row["vote_average"]
                score_html = generate_rating_html(score)
                # Compose the card HTML, with More Info link inside the card div
                card_html = """
                    <div style='background-color:#111111; padding:15px; border-radius:10px; margin-bottom:20px; display: flex; align-items: flex-start; box-shadow: 0 4px 8px rgba(0,0,0,0.25); transition: transform 0.2s;'>
                        <img src="{}" style="width:120px; height:auto; border-radius:5px; margin-right:15px;" />
                        <div style="flex:1;">
                            <h4 style='margin-bottom:0px; color:#efb810;'>🎬 {}</h4>
                            <p style='margin-top:2px; color:#bbb; font-size:14px;'>📅 {}</p>
                            <div style='margin:5px 0;'>
                                <strong style='color:#ccc;'>Genres:</strong>
                                {}
                            </div>
                            <p style='margin:5px 0; color:#ccc;'>{}...</p>
                            <div style='margin:5px 0;'>
                                <strong style='color:#ccc;'>Rating:</strong> {}
                            </div>
                            {}
                            <p style='margin-top:10px;'>
                              <a href="https://www.themoviedb.org/search?query={}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                            </p>
                        </div>
                    </div>
                """.format(
                    base_url + row["poster_path"],
                    title,
                    year,
                    genre_html,
                    row["overview"][:300],
                    score_html,
                    (
                        "<p style='font-size:12px; color:gray; margin:0;'>Based on TMDB user ratings</p>"
                        if score_html != 0
                        else ""
                    ),
                    title.replace(" ", "%20"),
                )
                st.markdown(card_html, unsafe_allow_html=True)
                trailer_url = get_movie_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)

# --- Collaborative Filtering Recommender Workflow ---
else:
    max_user_id = 20 if DATA_MODE == "demo" else 10000
    user_id = st.number_input(
        "Enter User ID", min_value=1, max_value=max_user_id, step=1
    )

    if st.button("Get Recommendations", key="cf_button"):
        try:
            recs = get_user_recommendations(user_id, top_n=10)
            conn = get_connection(str(DATA_DIR / "recommendations.db"))
            rows = get_all_movies(conn)
            movies_df = pd.DataFrame(
                rows,
                columns=[
                    "movieId",
                    "title",
                    "genres",
                    "overview",
                    "poster_path",
                    "vote_average",
                    "popularity",
                ],
            )
            recommended_titles = movies_df[movies_df["movieId"].isin(recs)][
                "title"
            ].tolist()
            log_feedback(
                user_id=user_id,
                recommended_movies=recommended_titles,
                method="collaborative_filtering",
            )
        except ValueError as e:
            st.error(str(e))
            st.stop()

        recommended_df = movies_df[movies_df["movieId"].isin(recs)]

        st.subheader("🎯 Recommended Movies")
        for _, row in recommended_df.iterrows():
            title, year = normalize_title(row["title"])
            try:
                genres = (
                    eval(row["genres"])
                    if isinstance(row["genres"], str)
                    else row["genres"]
                )
            except Exception:
                genres = []
            genre_html = generate_genre_html(genres)
            score = row["vote_average"]
            score_html = generate_rating_html(score)
            title_normalized = title.replace(" ", "%20")
            poster_path = row["poster_path"] or ""
            img_src = (
                base_url + poster_path
                if poster_path
                else "https://via.placeholder.com/120x180?text=No+Image"
            )
            card_html = f"""
                <div style='background-color:#111111; padding:15px; border-radius:10px; margin-bottom:20px; display: flex; align-items: flex-start; box-shadow: 0 4px 8px rgba(0,0,0,0.25); transition: transform 0.2s;'>
                    <img src="{img_src}" style="width:120px; height:auto; border-radius:5px; margin-right:15px;" />
                    <div style="flex:1;">
                        <h4 style='margin-bottom:0px; color:#efb810;'>🎬 {title}</h4>
                        <p style='margin-top:2px; color:#bbb; font-size:14px;'>📅 {year}</p>
                        <div style='margin:5px 0;'>
                            <strong style='color:#ccc;'>Genres:</strong>
                            {genre_html}
                        </div>
                        <p style='margin:5px 0; color:#ccc;'>{row["overview"][:300]}...</p>
                        <div style='margin:5px 0;'>
                            <strong style='color:#ccc;'>Rating:</strong> {score_html}
                        </div>
                        <p style='font-size:12px; color:gray; margin:0;'>Based on TMDB user ratings</p>
                        <p style='margin-top:10px;'>
                          <a href="https://www.themoviedb.org/search?query={title_normalized}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                        </p>
                    </div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            trailer_url = get_movie_trailer_url(title)
            if trailer_url:
                st.video(trailer_url)

# --- Feedback Log Viewer Section ---
with st.expander("📝 View User Feedback Logs"):
    method_filter = st.selectbox(
        "Filter by method", ["All", "content_based", "collaborative_filtering"]
    )

    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        db = client["recommender_logs"]
        feedback_collection = db["user_feedback"]

        query = {} if method_filter == "All" else {"method": method_filter}
        logs = list(feedback_collection.find(query).sort("timestamp", -1))

        if not logs:
            st.info("No feedback logs found.")
        else:
            for log in logs:
                # Display each feedback entry nicely
                st.markdown(
                    f"""
                ---
                👤 **User ID:** {log.get("user_id", "N/A")}  
                🧠 **Method:** `{log.get("method", "N/A")}`  
                🎬 **Source Movie:** {log.get("source_movie", "—")}  
                📅 **Timestamp:** {log.get("timestamp").strftime("%Y-%m-%d %H:%M:%S")}  
                ✅ **Recommendations:** {', '.join(str(title) for title in log.get("recommended_movies", []))}
                """
                )
    except Exception as e:
        st.error(f"Error loading logs: {e}")
