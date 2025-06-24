# %%
import json
import sqlite3
from datetime import datetime, timezone
import pandas as pd
from pathlib import Path

# Paths
db_path = Path("jobs_ref.db")
json_path = Path("adzuna_response.json")

# Load and flatten JSON data
with open(json_path) as f:
    data = json.load(f)

jobs=data['results']
df = pd.json_normalize(jobs)

#to avoid problems with SQL commands later
df.fillna("unknown",inplace=True)
df.columns = [col.replace('.', '_') for col in df.columns]

#Make title and company fields more resilient
df.company_display_name=df.company_display_name.str.upper()
df.title=df.title.str.lower()
df.description=df.description.str.lower()

# %%
# Add columns: timestamp, raw JSON payload
df["retrieved_at"] = datetime.now(timezone.utc).date().isoformat()
df["raw_payload"] = [json.dumps(job) for job in jobs]
#Add the area list as a JSON in one column in case needed later
df["area_json"] = df["location_area"].apply(json.dumps)
#Convert the date from the response into the isoformat date
df["created_date"] = df["created"].apply(lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")).date().isoformat())

# Choose which columns to keep in the DB
columns = [
    "redirect_url",
    "description",
    "title",
    "created_date",
    "company_display_name",
    "area_json",
    "location_display_name",
    "retrieved_at",
    "raw_payload"
]
df = df[columns]


# %%
# Insert data into SQLite database, skipping duplicates
with sqlite3.connect(db_path) as conn:
    df.to_sql("tmp_jobs", conn, if_exists="replace", index=False)
    conn.execute("""
    INSERT OR IGNORE INTO jobs (
        title, company,
        location, area_json,
        description, url,
        ad_date, retrieved_date,
        raw_payload
    )
    SELECT 
        title, company_display_name,
        location_display_name, area_json,
        description, redirect_url,
        created_date, retrieved_at,
        raw_payload
    FROM tmp_jobs
""")
    conn.commit()

# %%
