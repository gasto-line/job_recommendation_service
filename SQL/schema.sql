PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS jobs (
    job_hash      TEXT PRIMARY KEY, 
    title         TEXT,
    company       TEXT,
    location      TEXT,
    area_json     JSON,
    description   TEXT,
    url           TEXT,
    posted_date       TEXT,
    retrieved_date   TEXT,               -- ISO-8601 timestamp
    raw_payload   JSON,             -- full Adzuna response
    user_score         INTEGER CHECK(user_score BETWEEN 1 and 10),
    user_justification  TEXT,
    prompt_version  TEXT,
    AI_score    INTEGER CHECK(AI_score BETWEEN 1 and 10),
    AI_justification    TEXT,
    applied BOOLEAN DEFAULT 0,

    UNIQUE(title,company)
);