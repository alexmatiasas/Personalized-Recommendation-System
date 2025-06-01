import os

import joblib
import numpy as np
import streamlit as st


def normalize_title(title):
    """
    Normalize movie titles for consistency.

    - Moves articles like 'The', 'A', and 'An' to the beginning of the title.
    - Extracts and returns the release year if present in the format '(YYYY)'.

    Parameters:
        title (str): Original movie title.

    Returns:
        tuple: A tuple containing the normalized title and the extracted year (if present).
    """
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


def save_similarity(
    similarity_matrix: np.ndarray, path: str = "models/user_similarity.joblib"
):
    """
    Save a user-user similarity matrix to disk using joblib.

    Parameters:
        similarity_matrix (np.ndarray): The matrix to be saved.
        path (str): File path where the matrix will be saved.
    """
    joblib.dump(similarity_matrix, path)


def load_similarity(path: str = "models/user_similarity.joblib"):
    """
    Load a user-user similarity matrix from disk using joblib.

    Parameters:
        path (str): Path to the joblib file.

    Returns:
        np.ndarray or None: Loaded similarity matrix or None if the file is not found.
    """
    if os.path.isfile(path):
        print(f"🔁 Found similarity file at: {path}")
        return joblib.load(path)
    else:
        print(f"⚠️ Similarity file not found at: {path}")
        return None


@st.cache_resource
def load_similarity_cached(path: str = "models/user_similarity.joblib"):
    """
    Streamlit-cached version of load_similarity to avoid redundant disk reads.

    Parameters:
        path (str): Path to the joblib file.

    Returns:
        np.ndarray or None: Loaded similarity matrix or None if the file is not found.
    """
    return load_similarity(path)
