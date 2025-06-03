-- Schema for SQLite movie recommendation system

-- Drop existing tables if they exist to ensure clean initialization
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS movies;

-- Create movies table with enriched metadata and features
CREATE TABLE movies (
    movieId INTEGER PRIMARY KEY,
    title TEXT,
    genres TEXT,
    overview TEXT,
    popularity REAL,
    poster_path TEXT,
    release_date TEXT,
    release_year INTEGER,
    release_decade TEXT,
    vote_average REAL,
    tmdb_id INTEGER,
    n_genres INTEGER,
    overview_length INTEGER
);

-- Create users table for unique user identifiers
CREATE TABLE users (
    userId INTEGER PRIMARY KEY
);

-- Create ratings table with foreign keys and cascade delete behavior
CREATE TABLE ratings (
    userId INTEGER,
    movieId INTEGER,
    rating REAL,
    timestamp INTEGER,  -- Unix timestamp format
    PRIMARY KEY (userId, movieId),
    FOREIGN KEY (userId) REFERENCES users(userId) ON DELETE CASCADE,
    FOREIGN KEY (movieId) REFERENCES movies(movieId) ON DELETE CASCADE
);

-- Optional indexes to improve query performance (if large dataset)
-- CREATE INDEX idx_userId ON ratings(userId);
-- CREATE INDEX idx_movieId ON ratings(movieId);