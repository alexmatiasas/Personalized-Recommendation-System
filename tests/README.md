# 🧪 Testing

This project includes unit tests to ensure the reliability of both the content-based and collaborative filtering recommendation systems.

## ✔️ Implemented Tests

- **Content-Based Recommender (`tests/test_content_based.py`)**
  - Tests model instantiation using a small mock DataFrame.
  - Verifies that the `get_recommendations` method:
    - Returns a list of movie titles.
    - Returns a non-empty list.
    - Ensures all recommended items are strings (titles).

- **Collaborative Filtering Recommender (`tests/test_collaborative_filtering.py`)**
  - Instantiates the recommender from in-memory mock data (ratings and metadata).
  - Checks that the user-item interaction matrix is built correctly.
  - Ensures `recommend_movies_for_user` returns a valid, non-empty list of movie IDs.

### 🛠️ Running the Tests

This project uses `pytest` and `coverage`. To run the full test suite:

```bash
poetry run pytest --cov=src --cov-report=term-missing --cov-report=xml
```

## 🧩 Test Coverage

Currently, the tests cover:

- Core recommendation logic.
- Basic input/output behaviors for both models.

### 🔜 Suggested Improvements

To further strengthen the test suite:

- Add edge case tests (e.g., users with no ratings, missing metadata).
- Include failure cases (invalid inputs, missing files).
- Test utility methods like compute_user_similarity and build_user_item_matrix.
