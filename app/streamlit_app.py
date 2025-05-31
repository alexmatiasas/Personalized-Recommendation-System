import os
import sys

# Add src/ to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joblib
import numpy as np
import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

from src.collaborative_filtering import CollaborativeFilteringRecommender
from src.content_based import ContentBasedRecommender


def normalize_title(title):
    if ", The" in title:
        title = "The " + title.replace(", The", "")
    elif ", A" in title:
        title = "A " + title.replace(", A", "")
    elif ", An" in title:
        title = "An " + title.replace(", An", "")
    name = title.rsplit("(", 1)[0].strip()
    year = ""
    if "(" in title and ")" in title:
        try:
            raw_year = title.split("(")[-1].replace(")", "").strip()
            if raw_year.isdigit() and len(raw_year) == 4:
                year = raw_year
        except Exception:
            pass
    return name, year


# Utility functions for saving/loading similarity matrices


def save_similarity(
    similarity_matrix: np.ndarray, path: str = "models/user_similarity.joblib"
):
    """
    Save the user-user similarity matrix to disk using joblib.
    """
    joblib.dump(similarity_matrix, path)


def load_similarity(path: str = "models/user_similarity.joblib"):
    """
    Load a precomputed user-user similarity matrix from disk using joblib.
    """
    if os.path.isfile(path):
        print(f"🔁 Found similarity file at: {path}")
        return joblib.load(path)
    else:
        print(f"⚠️ Similarity file not found at: {path}")
        return None


load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
base_url = "https://image.tmdb.org/t/p/w500/"


@st.cache_resource
def load_similarity_cached(path: str = "models/user_similarity.joblib"):
    return load_similarity(path)


def get_trailer_url(title):
    try:
        query = title.replace(" ", "%20")
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}"
        response = requests.get(search_url).json()
        movie_id = response["results"][0]["id"]

        videos_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={TMDB_API_KEY}"
        videos = requests.get(videos_url).json()["results"]
        trailer = next(
            (
                vid
                for vid in videos
                if vid["type"] == "Trailer" and vid["site"] == "YouTube"
            ),
            None,
        )
        return f"https://www.youtube.com/watch?v={trailer['key']}" if trailer else None
    except Exception:
        return None


st.title("🎬 Movie Recommender System")

# Sidebar options
option = st.sidebar.selectbox(
    "Choose Recommender:", ("Content-Based", "Collaborative Filtering")
)

if option == "Content-Based":
    # Load content-based recommender
    movies_df = pd.read_csv("data/processed/enriched_movies_clean.csv")

    @st.cache_resource
    def fit_recommender():
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
        genre_html = " ".join(
            [
                f"<span style='background-color:#444;border-radius:8px;padding:4px 8px;margin-right:5px;font-size:12px;color:white;'>{g}</span>"
                for g in genres
            ]
        )
        score = selected_movie["vote_average"]
        stars = "★" * int(round(score)) + "☆" * (10 - int(round(score)))
        score_html = f"<span style='color:#ffc107;'>{stars}</span> <span style='color:#bbb;'>({score}/10)</span><br><small><em style='color:#888;'>Based on TMDB user ratings</em></small>"
        st.markdown(
            f"""
            <div style='background-color:#1a1a40; padding:20px; border-radius:12px; margin-bottom:25px; display: flex; align-items: flex-start; box-shadow: 0 6px 12px rgba(0,0,0,0.3);'>
                <img src="{base_url + selected_movie['poster_path']}" style="width:140px; height:auto; border-radius:5px; margin-right:25px;" />
                <div style="flex:1;">
                    <h3 style='margin-bottom:5px; color:#b3beff;'>🎬 {normalize_title(selected_movie['title'])[0]}</h3>
                    <p style='margin-top:0; color:#bbb; font-size:14px;'>📅 {year}</p>
                    <div style='margin:5px 0;'>
                        <strong style='color:#e0e0e0;'>Genres:</strong>
                        {genre_html}
                    </div>
                    <p style='margin:5px 0; color:#e0e0e0;'>{selected_movie['overview']}</p>
                    <div style='margin:5px 0;'>
                        <strong style='color:#e0e0e0;'>Rating:</strong> {score_html}
                    </div>
                    <p style='margin-top:10px;'>
                      <a href="https://www.themoviedb.org/search?query={normalize_title(selected_movie['title'])[0].replace(' ', '%20')}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                    </p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    trailer_url = get_trailer_url(normalize_title(selected_movie["title"])[0])
    if trailer_url:
        st.markdown("### 🎬 Watch Trailer")
        st.video(trailer_url)

    top_n = st.slider("How many recommendations?", min_value=1, max_value=10, value=5)
    if st.button("Get Recommendations", key="cb_button"):
        recommender = fit_recommender()
        recs = recommender.get_recommendations(selected_movie["title"], top_n=top_n)
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
                genre_html = " ".join(
                    [
                        f"<span style='background-color:#333; color:white; padding:3px 8px; border-radius:10px; margin-right:6px; font-size:12px;'>{genre}</span>"
                        for genre in genres
                    ]
                )
                score = row["vote_average"]
                stars = "★" * int(round(score)) + "☆" * (10 - int(round(score)))
                score_html = f"<span style='color:#ffc107;'>{stars}</span> <span style='color:#bbb;'>({score}/10)</span><br><small><em style='color:#888;'>Based on TMDB user ratings</em></small>"
                # Compose the card HTML, with More Info link inside the card div
                card_html = f"""
                    <div style='background-color:#111111; padding:15px; border-radius:10px; margin-bottom:20px; display: flex; align-items: flex-start; box-shadow: 0 4px 8px rgba(0,0,0,0.25); transition: transform 0.2s;'>
                        <img src="{base_url + row['poster_path']}" style="width:120px; height:auto; border-radius:5px; margin-right:15px;" />
                        <div style="flex:1;">
                            <h4 style='margin-bottom:0px; color:#b3beff;'>🎬 {title}</h4>
                            <p style='margin-top:2px; color:#bbb; font-size:14px;'>📅 {year}</p>
                            <div style='margin:5px 0;'>
                                <strong style='color:#ccc;'>Genres:</strong>
                                {genre_html}
                            </div>
                            <p style='margin:5px 0; color:#ccc;'>{row['overview'][:300]}...</p>
                            <div style='margin:5px 0;'>
                                <strong style='color:#ccc;'>Rating:</strong> {score_html}
                            </div>
                            <p style='margin-top:10px;'>
                              <a href="https://www.themoviedb.org/search?query={title.replace(" ", "%20")}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                            </p>
                        </div>
                    </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                trailer_url = get_trailer_url(title)
                if trailer_url:
                    st.video(trailer_url)

else:
    max_user_id = 10000  # default fallback
    try:
        ratings_df = pd.read_csv("data/ml-1m/ratings.csv")
        max_user_id = ratings_df["userId"].max()
    except Exception:
        st.warning(
            "⚠️ Could not load user data to determine max user ID. Default max=10000 used."
        )

    user_id = st.number_input(
        "Enter User ID", min_value=1, max_value=int(max_user_id), step=1
    )

    if st.button("Get Recommendations", key="cf_button"):
        if not os.path.exists("data/ml-1m/ratings.csv"):
            st.error(
                "⚠️ Ratings data file not found. Please ensure 'data/ml-1m/ratings.csv' exists."
            )
            st.stop()
        recommender = CollaborativeFilteringRecommender(
            ratings_path="data/ml-1m/ratings.csv",
            enriched_movies_path="data/processed/enriched_movies_clean.csv",
        )
        recommender.load_data()

        # Ensure models/ directory exists
        os.makedirs("models", exist_ok=True)

        similarity_matrix = load_similarity_cached()
        if similarity_matrix is None:
            st.warning("⚠️ Precomputed matrix not found, computing similarity...")
            recommender.compute_user_similarity()
            save_similarity(recommender.similarity_matrix)
            st.success("✅ Similarity matrix computed and saved")
        else:
            recommender.similarity_matrix = similarity_matrix
            st.info("🔁 Loaded precomputed similarity matrix from disk")

        if user_id not in recommender.ratings_df["userId"].unique():
            st.warning(f"User ID {user_id} not found in dataset.")
            st.stop()
        recs = recommender.recommend_movies_for_user(user_id)
        movies_df = pd.read_csv("data/processed/enriched_movies_clean.csv")
        recommended_df = movies_df[movies_df["movieId"].isin(recs)][
            ["title", "genres", "overview", "poster_path", "vote_average", "popularity"]
        ]

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
            genre_html = " ".join(
                [
                    f"<span style='background-color:#333; color:white; padding:3px 8px; border-radius:10px; margin-right:6px; font-size:12px;'>{genre}</span>"
                    for genre in genres
                ]
            )
            score = row["vote_average"]
            stars = "★" * int(round(score)) + "☆" * (10 - int(round(score)))
            score_html = f"<span style='color:#ffc107;'>{stars}</span> <span style='color:#bbb;'>({score}/10)</span><br><small><em style='color:#888;'>Based on TMDB user ratings</em></small>"
            title_normalized = title.replace(" ", "%20")
            card_html = f"""
                <div style='background-color:#111111; padding:15px; border-radius:10px; margin-bottom:20px; display: flex; align-items: flex-start; box-shadow: 0 4px 8px rgba(0,0,0,0.25); transition: transform 0.2s;'>
                    <img src="{base_url + row['poster_path']}" style="width:120px; height:auto; border-radius:5px; margin-right:15px;" />
                    <div style="flex:1;">
                        <h4 style='margin-bottom:0px; color:#b3beff;'>🎬 {title}</h4>
                        <p style='margin-top:2px; color:#bbb; font-size:14px;'>📅 {year}</p>
                        <div style='margin:5px 0;'>
                            <strong style='color:#ccc;'>Genres:</strong>
                            {genre_html}
                        </div>
                        <p style='margin:5px 0; color:#ccc;'>{row['overview'][:300]}...</p>
                        <div style='margin:5px 0;'>
                            <strong style='color:#ccc;'>Rating:</strong> {score_html}
                        </div>
                        <p style='margin-top:10px;'>
                          <a href="https://www.themoviedb.org/search?query={title_normalized}" target="_blank" style="color:#00ffff;">More Info ↗</a>
                        </p>
                    </div>
                </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            trailer_url = get_trailer_url(title)
            if trailer_url:
                st.video(trailer_url)
