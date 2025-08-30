# Automatic Job Recommendation Service

_A smart hybrid system to match job opportunities to your personal expectations, combining GPT matching and user feedback._

---

## Table of Contents
1. [Project Vision](#project-vision)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Getting Started](#getting-started)
5. [Daily Workflow](#daily-workflow)
6. [Data & Model Details](#data--model-details)
7. [Roadmap](#roadmap)
8. [Contributing](#contributing)
---

## Project Vision

Conventional job-alert platforms rely on static search filters and sparse metadata, often leading to mismatched suggestions. **Automatic Job Recommendation Service** improves this experience by combining:
- A first-pass GPT-driven job matching based on explicit user preferences.
- A lightweight feedback loop where the user scores job posts and optionally leaves comments to fine-tune the matching process over time.

**The goal:** Receive daily high-quality job recommendations, better tailored each day based on your feedback.

## Key Features
- **Explicit Profile Matching** – Matching based on job titles, ideal job description, skills, and education.
- **Automated Daily Pipeline** – GitHub Actions runs daily at 6 AM UTC to fetch and process new jobs.
- **Smart Deduplication** – Uses job hashes to prevent duplicate recommendations across days.
- **GPT Matching Engine** – Computes matching scores (0-10) based on profile vs job description.
- **GitHub Release Distribution** – Top jobs automatically published to GitHub Release for easy access.
- **Streamlit Feedback UI** – User scores jobs (1-10) and optionally writes short justifications.
- **PostgreSQL Integration** – User feedback stored in Supabase for future prompt improvements.
- **Email Notifications** – Daily email alerts when new recommendations are ready.

## System Architecture
```text
                         +----------------+
                         | User Profile    |
                         | (static info)   |
                         +----------------+
                                 │
                         +----------------+
                         | GitHub Actions  |
                         | (Daily 6 AM)    |
                         +----------------+
                                 │
                    Fetch 50 new job posts via Adzuna API
                                 │
                    +------------------+
                    | Raw Job Listings  |
                    | (title, desc, URL)|
                    +------------------+
                                 │
                    Generate job hashes & deduplicate
                                 │
                    Filter out existing jobs (PostgreSQL)
                                 │
                    GPT Matching Engine (0-10 scores)
                                 │
                    +-------------------------------+
                    | Top N Jobs with AI Scores     |
                    +-------------------------------+
                                 │
                    Save to GitHub Release (top_jobs.pkl)
                                 │
                    Send Email Notification
                                 │
                    +-------------------+
                    | Streamlit App:     |
                    | - Load from GitHub |
                    | - User scores jobs |
                    | - Optional comment |
                    +-------------------+
                                 │
                    Store feedback in PostgreSQL (Supabase)
```

## Getting Started

### Prerequisites
- Python 3.11+
- Required API keys: OpenAI, Adzuna, SendGrid
- PostgreSQL database (Supabase recommended)

### Environment Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables (see `.github/workflows/daily-run-v0.yaml` for required secrets)
4. Configure user profile in `config/user_profile.yaml`

### Running Locally
- **Full workflow**: `python generate_top_jobs.py`
- **Streamlit app**: `streamlit run streamlit_app/main.py`
- **Component testing**: Use Jupyter notebooks with `#%%` cell markers

### Production Deployment
The system runs automatically via GitHub Actions daily at 6 AM UTC. No manual intervention required.

## Daily Workflow
1. **10:00 AM UTC** – GitHub Action triggers automatically
2. Fetch 50 new job postings from Adzuna API
3. Generate unique job hashes and remove duplicates
4. Filter out jobs already in PostgreSQL reference database
5. GPT evaluates matching score (0-10) based on user profile
6. Select top N jobs and save to GitHub Release (`top_jobs.pkl`)
7. Send email notification with Streamlit app link
8. Streamlit app loads jobs from GitHub Release
9. User scores jobs (1-10) and optionally leaves comments
10. Feedback stored directly in PostgreSQL (Supabase) for future improvements

## Data & Model Details

| Component | Purpose | Key Fields |
|:----------|:--------|:----------|
| **Adzuna API** | Raw job data source | `title`, `company`, `description`, `redirect_url`, `location` |
| **Job Processing** | Deduplication & hashing | `job_hash` (unique identifier), `posted_date`, `retrieved_date` |
| **GPT Scoring** | AI matching engine | `ai_score` (0-10), `ai_justification`, `model_version`, `prompt_version` |
| **GitHub Release** | Job distribution | `top_jobs.pkl` (pickle file with top N jobs) |
| **PostgreSQL (Supabase)** | User feedback storage | `job_hash`, `user_score`, `user_justification`, `applied` |

## Roadmap
- **Dynamic Prompt Tuning** – Use user comments to adjust matching prompts.
- **Multi-source Job Fetching** – Integrate additional job APIs (Jooble, etc.).
- **Multi-user Profiles** – Allow several users to have separate preferences.
- **Advanced Analytics** – Dashboard for tracking recommendation quality over time.
- **Local Development Tools** – Enhanced testing and debugging infrastructure.
- **Performance Optimization** – Caching and rate limiting improvements.

---

*© 2025 — Automatic Job Recommendation Service*





