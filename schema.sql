CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    fingerprint_js VARCHAR(255)
);

CREATE TABLE fingerprint_attempts (
    id SERIAL PRIMARY KEY,
    fingerprint VARCHAR(255) NOT NULL,
    attempted_at TIMESTAMP DEFAULT NOW()
);