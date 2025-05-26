# %%

import pandas as pd
import sqlite3
from pathlib import Path

df = pd.read_pickle('scored_jobs.pkl')
db_path=Path("data/jobs_ref.db")

# %%
# Insert data into SQLite database, skipping duplicates
with sqlite3.connect(db_path) as conn:
    df.to_sql("tmp_jobs", conn, if_exists="replace", index=False)
    conn.execute("""
    INSERT OR IGNORE INTO jobs (
        title, company,
        location, area_json,
        description, url,
        posted_date, retrieved_date,
        raw_payload,
        prompt_version,
        AI_score, user_score,
        AI_justification, user_justification
    )
    SELECT 
        title, company,
        location, area_json,
        description, redirect_url,
        created_date, retrieved_at,
        raw_payload,
        prompt_version,
        AI_score, user_score,
        AI_justification, user_justification
                 
    FROM tmp_jobs
""")
    conn.commit()
# %%
