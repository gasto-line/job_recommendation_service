# Automatic Job Recommendation Service

_Automatically surfaces job opportunities that truly match your interests by learning directly from your feedback._

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
9. [License](#license)

---

## Project Vision
Conventional job‑alert platforms rely on static search filters and sparse metadata supplied by the job poster, often leading to mismatched recommendations. **Automatic Job Recommendation Service** closes that gap by continuously training on your personal scoring of past job posts, enabling far more accurate and individualized suggestions.

*In the first release the system is fully self‑hosted and trains exclusively on one job‑board API, but the design keeps expansion and multi‑user scale‑out in mind.*

## Key Features
- **Active‑Learning Recommendation Engine** – A lightweight ML pipeline (TF‑IDF + linear model) learns from a 1–10 score you assign to each job post.
- **End‑to‑End Automation** – A GitHub Action fetches fresh listings daily, ranks them, and emails the top 10 for scoring.
- **Streamlit Feedback UI** – One‑click scoring from any device; new scores immediately enrich the dataset.
- **Zero‑Ops Storage** – Uses SQLite for simplicity while prototyping; interchangeable with cloud DBs later.
- **Modular Data Layer** – Distinct *raw*, *processed*, and *labeled* tables make it easy to iterate on feature engineering or swap in new sources.

## System Architecture

to be updated...

### Tech Stack
| Layer | Tooling |
|-------|---------|
| Language | Python ≥ 3.10 |
| Data Store | SQLite (soon: Postgres/Cloud SQL) |
| ML | scikit‑learn, pandas, numpy |
| Scheduling | GitHub Actions (cron) |
| Web UI | Streamlit |
| Email | SMTP via GitHub Secrets |

## Getting Started
### 1. Clone & Install
```bash
git clone https://github.com/<your‑handle>/automatic‑job‑recommendation‑service.git
cd automatic‑job‑recommendation‑service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables
Create `.env` in the project root:
```env
JOBBOARD_API_KEY=xxx
EMAIL_HOST=smtp.gmail.com
EMAIL_USER=you@example.com
EMAIL_PASS=app‑password
RECIPIENT_EMAIL=you@example.com
```

### 3. Bootstrap Dataset
Run the data‑seed script to fetch the first 100 posts and start manual scoring:
```bash
python scripts/seed_dataset.py --n 100
streamlit run app/label_ui.py
```

## Daily Workflow
1. **00:00 UTC** – GitHub Action `fetch‑and‑rank.yml` retrieves 50 fresh postings via API.
2. Posts are vectorized using the current TF‑IDF vocabulary, and a predicted score is generated.
3. Top 10 predictions are emailed (HTML digest) and surfaced in the Streamlit UI for scoring during the day.
4. **23:00 UTC** – Action `retrain.yml` merges the day’s new scores into `jobs_raw.db`, rebuilds features, and retrains the model.
5. Metrics (MAE, top‑10 precision) are logged to the repository’s **Actions → Artifacts** tab.

## Data & Model Details
| Table | Purpose | Key Fields |
|-------|---------|-----------|
| `jobs_raw` | Untouched API responses | `id`, `json`, `fetched_at` |
| `jobs_vect` | Sparse vectors & engineered fields | `job_id`, `tfidf_vec`, `years_exp`, … |
| `scores` | Human labels | `job_id`, `score`, `label_time` |

Current model: **Logistic Regression (one‑vs‑rest)** on TF‑IDF + engineered numeric features. For a deeper dive, see [`notebooks/model_exploration.ipynb`](notebooks/model_exploration.ipynb).

## Roadmap
- **Multi‑Source Intake** – Add Jooble API and web‑scraped boards.
- **AI Field Enrichment** – LLM agents fetch job pages to fill missing metadata (years exp, sector, technicality).
- **Cold‑Start Mitigation** – Start with a generic language‑model embedding and fine‑tune as labels grow.
- **Public SaaS Beta** – Dockerised backend, Postgres, AWS/GCP deployment.
- **Collaboration Features** – Multi‑user auth, shared or personal models, leaderboard.

> *Have an idea? Create a [discussion](https://github.com/<repo>/discussions) or open an issue!*

## Contributing
PRs are welcome 🎉  For major changes, please open an issue first to discuss what you would like to change. Be sure to update tests as appropriate.


---

*© 2025 — Automatic Job Recommendation Service*



