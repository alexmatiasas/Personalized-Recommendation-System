# Contributing Guide

Thank you for considering contributing to the **Personalized Recommendation System** project!

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

## ✍️ How to Contribute

1. Create an issue to discuss the proposed change or bug.
2. Create a new branch from `develop`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3.	Make your changes, commit, and push:
    ```bash
    git add .
    git commit -m "✨ Add feature XYZ"
    git push origin feature/your-feature-name
    ```
4.	Open a Pull Request (PR) targeting develop.
5.	Wait for review and merge approval.

## 🛠️ Development Setup

This project uses [Poetry](https://python-poetry.org/) to manage dependencies. To get started:

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/Personalized-Recommendation-System.git
   cd Personalized-Recommendation-System
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Activate the virtual environment (optional):
   ```bash
   poetry shell
   ```

## 🧼 Code Style and Formatting

We use the following tools to maintain consistent code quality:
- `black` – for code formatting
- `isort` – for import sorting
- `ruff` – for linting and error detection

All of these are run automatically using `pre-commit`.

## ✅ Pre-commit Hooks

This project uses [pre-commit](https://pre-commit.com/) to automate code formatting and linting before each commit.

1. Install pre-commit (if not already installed):
   ```bash
   poetry add --group dev pre-commit
   ```

2. Install the hooks:
   ```bash
   poetry run pre-commit install
   ```

3. Run hooks manually on all files (optional but recommended on first setup):
   ```bash
   poetry run pre-commit run --all-files
   ```

## 🧪 Testing

To run tests:
```bash
poetry run pytest
```

To include code coverage reporting:
```bash
poetry run pytest --cov=src --cov-report=term-missing
```

---

Please follow these guidelines to ensure consistent contributions. Thank you!
