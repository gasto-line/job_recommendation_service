import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import Date, Boolean
from sqlalchemy.dialects.postgresql import JSON
import os

username = "irutkdcynqycaveefmpe"
port = 5432
host = "aws-0-eu-west-3.pooler.supabase.com"
database = "postgres"

def get_engine(DB_PSW):
    connection_string = f"postgresql://{username}:{DB_PSW}@{host}:{port}/{database}"
    return create_engine(connection_string, pool_pre_ping=True)

def extract_jobs_hash(engine):
    """
    Extracts job hashes from the database.
    
    Returns:
        pd.DataFrame: A DataFrame containing job hashes.
    """
    try:
        with engine.connect() as conn:
            query = text("SELECT job_hash FROM jobs")
            result = pd.read_sql(query, conn)
            return result
    except Exception as e:
        print(f"Error extracting job hashes: {e}")
        return pd.DataFrame(columns=["job_hash"])

def insert_jobs(jobs_df: pd.DataFrame,engine) -> None:
    try:
        with engine.begin() as conn:
            # ❸ Replace the tmp_jobs staging table with new data
            jobs_df.to_sql(
                "tmp_jobs",
                conn,
                if_exists="replace",
                index=False,
                dtype={
                    'area_json': JSON(),
                    'posted_date': Date(),
                    'retrieved_date': Date(),
                    'raw_payload': JSON(),
                    'applied': Boolean(),
                },
                method="multi",
            )

            # ❹ Insert new rows into the main jobs table
            conn.execute(text("""
                INSERT INTO jobs (
                    job_hash,
                    title, company,
                    location, area_json,
                    description, url,
                    posted_date, retrieved_date,
                    raw_payload,
                    prompt_version,
                    ai_score, user_score,
                    ai_justification, user_justification,
                    applied
                )
                SELECT
                    job_hash,
                    title, company,
                    location, area_json,
                    description, redirect_url,
                    posted_date, retrieved_date,
                    raw_payload,
                    prompt_version,
                    ai_score, user_score,
                    ai_justification, user_justification,
                    applied
                FROM tmp_jobs
                WHERE user_score IS NOT NULL
                ON CONFLICT (job_hash) DO NOTHING;
            """))
        print("✅ Data successfully inserted")
    except Exception as e:
        print(f"❌ Database insert failed: {e}")
