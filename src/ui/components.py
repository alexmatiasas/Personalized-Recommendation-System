import streamlit as st


def generate_genre_html(genres: list[str]) -> str:
    """
    Generates HTML for a list of genres styled as badges.

    Args:
        genres (list[str]): A list of genre strings.

    Returns:
        str: HTML string with styled genre badges.
    """
    return "".join(
        [
            f"<span style='background-color:#444;border-radius:8px;padding:4px 8px;margin:0 4px 4px 0;display:inline-block;font-size:12px;color:white;'>{genre}</span>"
            for genre in genres
        ]
    )


def generate_rating_html(rating: float) -> str:
    """
    Generates HTML to display rating as stars and numeric value.

    Args:
        rating (float): Rating score from 0 to 10.

    Returns:
        str: HTML string for the rating.
    """
    if rating is None:
        return ""
    stars = "⭐" * int(round(rating))
    return f"<p style='color:white;font-size:13px;'>{stars} {rating:.1f}/10</p>"


def render_movie_card(
    title: str,
    year: str,
    overview: str,
    genres: list[str],
    poster_url: str,
    trailer_url: str = None,
    rating: float = None,
    show_note: bool = False,
):
    """
    Renders a stylized movie card with poster, title, year, genres, overview, and an optional trailer link and rating.

    Args:
        title (str): The title of the movie.
        year (str): The release year of the movie.
        overview (str): A short description of the movie.
        genres (list[str]): List of genre strings.
        poster_url (str): URL to the movie's poster image.
        trailer_url (str, optional): YouTube trailer URL. Defaults to None.
        rating (float, optional): Rating score out of 10. Defaults to None.
        show_note (bool, optional): Whether to show the source note for the rating. Defaults to False.
    """
    genre_html = generate_genre_html(genres)
    rating_html = generate_rating_html(rating)

    st.markdown(
        f"""
        <div style="display: flex; margin-bottom: 20px; padding: 10px; border-radius: 10px; background-color: #222;">
            <img src="{poster_url}" width="120" style="border-radius: 10px; margin-right: 20px;" />
            <div>
                <h4 style="margin-bottom:0;color:#ffd700;">{title}</h4>
                <p style="margin-top:2px;color:gray;">{year}</p>
                <div style="margin-bottom:8px;">{genre_html}</div>
                <p style="font-size:14px;color:white;">{overview}</p>
                {rating_html}
                {"<p style='font-size:12px; color:gray; margin:0;'>Based on TMDB user ratings</p>" if show_note else ""}
                {f"<a href='{trailer_url}' target='_blank'>📽️ Watch Trailer</a>" if trailer_url else ""}
                {"<p style='font-size:11px;color:gray;margin-top:4px;'>Rating from user feedback (MovieLens)</p>" if show_note else ""}
            </div>
        """,
        unsafe_allow_html=True,
    )
