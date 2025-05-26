# Automatic Job Recommendation Service

_A smart hybrid system to match job opportunities to your personal expectations, combining GPT matching and user feedback._

---

## Table of Contents
1. [Project Vision](#project-vision)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
5. [Getting Started](#getting-started)
6. [Daily Workflow](#daily-workflow)
7. [Data & Model Details](#data--model-details)
8. [Roadmap](#roadmap)
9. [Contributing](#contributing)
---

## Project Vision

Conventional job-alert platforms rely on static search filters and sparse metadata, often leading to mismatched suggestions. **Automatic Job Recommendation Service** improves this experience by combining:
- A first-pass GPT-driven job matching based on explicit user preferences.
- A lightweight feedback loop where the user scores job posts and optionally leaves comments to fine-tune the matching process over time.

**The goal:** Receive daily high-quality job recommendations, better tailored each day based on your feedback.

## Key Features
- **Explicit Profile Matching** – Matching based on job titles, ideal job description, skills, and education.
- **Daily Fresh Listings** – Automatic daily fetch of new job postings.
- **GPT Matching Engine** – Computes matching percentages based on profile vs job description.
- **Streamlit Feedback UI** – User scores jobs (1-10) and optionally writes short justifications.
- **Self-Improving System** – Future prompt adaptation and model improvements based on historical user feedback.

## System Architecture
```text
                         +----------------+
                         | User Profile    |
                         | (static info)   |
                         +----------------+
                                 │
                +----------------+----------------+
                |                                 |
        (Daily) GitHub Action              (Trigger via API Call)
                |                                 |
     Fetch 50 new job posts via API                |
                ▼                                 ▼
        +------------------+             +------------------+
        | Raw Job Listings  |             | User Feedback DB |
        | (title, desc, URL)|             | (job_id, score,  |
        +------------------+             | justification)   |
                │                                 ▲
        Baseline GPT Matching (prompt)            |
                ▼                                 |
    +-------------------------------+             |
    | Jobs with % Match (0-100%)     |             |
    +-------------------------------+             |
                │                                 |
         Filter Top N Jobs                      |
                ▼                                 |
         Send Email Digest +                     |
         Available on Streamlit UI                |
                ▼                                 |
          +-------------------+                  |
          | Streamlit App:     |                  |
          | - User scores job  |                  |
          | - Optional comment |-----------------+
          +-------------------+
```

## Daily Workflow
1. **00:00 UTC** – GitHub Action fetches 50 new jobs.
2. GPT evaluates matching score based on your user profile.
3. Top N jobs are selected and sent by email / available on Streamlit.
4. You score jobs (1–10) and optionally leave comments.
5. Feedback is stored for future dynamic adjustment of matching prompts.

## Data & Model Details

| Table | Purpose | Key Fields |
|:-----|:--------|:----------|
| `jobs_raw` | Untouched API responses | `id`, `title`, `description`, `url` |
| `jobs_ranked` | Jobs with GPT-matching scores | `job_id`, `match_percentage` |
| `feedback` | User scores and comments | `job_id`, `score`, `comment`, `timestamp` |

## Roadmap
- **Dynamic Prompt Tuning** – Use user comments to adjust matching prompts.
- **Web Scraping Integration** – Cover sites without APIs.
- **Multi-user Profiles** – Allow several users to have separate preferences.
- **Fine-tuning Option** – Small custom ranking model trained on historical feedback.
- **Cloud Deployment** – Move to AWS/GCP for full automation.

> *Have ideas to improve? Feel free to create a [discussion](https://github.com/<repo>/discussions) or open an issue!*


---

*© 2025 — Automatic Job Recommendation Service*





