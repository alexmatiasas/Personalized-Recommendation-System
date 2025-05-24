# Personalized Recommendation System

> **Objective**: Build a personalized movie recommendation system using enriched metadata from TMDb and collaborative user ratings from the MovieLens dataset. The goal is to demonstrate advanced skills in data ingestion, preprocessing, content-based modeling, hybrid systems, NoSQL data handling, and deployable ML pipelines—all suitable for real-world product integration and data science portfolios.

---

## 🔍 Project Overview

This project builds a movie recommender system by integrating collaborative filtering (MovieLens ratings) with content-based recommendations (using TMDb metadata). The enriched dataset is stored in MongoDB Atlas, processed through Python and R workflows, and prepared for deployment using modern ML practices.

---

## 📁 Project Structure

    ```
    .
    ├── data/
    │   ├── ml-1m/                  # Original MovieLens dataset
    │   └── processed/             # Enriched movie metadata from TMDb
    ├── notebooks/
    │   ├── 01_EDA_in_R.Rmd        # Exploratory analysis in R
    │   ├── 03_EDA_Enriched.ipynb  # Metadata analysis and preparation
    │   └── 04_Content_Recommender.ipynb
    ├── src/
    │   ├── enrich_movies.py       # TMDb API enrichment
    │   ├── check_enriched_movies.py
    │   ├── collaborative_filtering.py
    │   └── hybrid_recommendation.py
    ├── models/
    ├── reports/
    ├── requirements.txt
    ├── pyproject.toml             # Poetry environment
    ├── .env.example
    ├── security_checklist.md
    └── README.md
    ```

---

## 🚀 Tech Stack

### Data Acquisition & Enrichment

* Python (`pandas`, `requests`)
* TMDb API
* MongoDB Atlas (NoSQL storage)
* `pymongo`, `dotenv`

### Modeling & Recommendation

* Content-based filtering (TF-IDF, cosine similarity)
* Collaborative filtering (Surprise)
* Hybrid systems

### Analysis & Visualization

* R (`ggplot2`, `dplyr`)
* Python (`matplotlib`, `seaborn`, `plotly`)
* Jupyter Notebooks

### Dev & Deployment

* Poetry (environment management)
* FastAPI or Streamlit (planned)
* Docker (optional)
* GitHub Actions (CI/CD – optional)

---

## 📦 Getting Started

    ```bash
    # Clone the repository
    $ git clone https://github.com/alexmatiasas/Personalized-Recommendation-System.git
    $ cd Personalized-Recommendation-System

    # Install Python dependencies
    $ poetry install

    # Set up environment variables
    $ cp .env.example .env
    # Add your TMDb API key and MongoDB URI in .env
    ```

---

## 📊 EDA & Preprocessing

* MovieLens ratings explored in R
* Movie metadata enriched from TMDb (title, genres, overview, popularity, vote average)
* Exported dataset with 3755 enriched movies
* Stored in MongoDB Atlas (`movies_enriched` collection)

---

## 🔍 Recommender Models

* ✅ Content-based recommender using TF-IDF over overviews
* ✅ Genre-based similarity
* 🧪 Hybrid model planned (ratings + content)

---

## 📈 Deployment (Planned)

* Build a Streamlit or FastAPI app to serve recommendations
* Connect live to MongoDB Atlas or use preprocessed `.csv`
* Deploy using Render or Railway (free-tier compatible)

---

## 🔐 Security

See [security\_checklist.md](./security_checklist.md) for full practices.

* All secrets stored in `.env`
* `.env` excluded from Git
* TMDb keys and Mongo credentials never exposed
* MongoDB access limited to authenticated users (dev/prod separation planned)

---

## 🧠 Author

**Manuel Alejandro Matías Astorga**
PhD in Physics | Data Scientist | Machine Learning Engineer
[Portfolio](https://alexmatiasas.github.io) | [GitHub](https://github.com/alexmatiasas)

---

## 📄 License

MIT License — see the LICENSE file for details.
