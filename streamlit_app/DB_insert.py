import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import Date, Boolean
from sqlalchemy.dialects.postgresql import JSON

# ❶ Import the database password from Streamlit secrets
DB_PSW=st.secrets["DB_PSW"]
SUPABASE_DB_URL = (
    "postgresql://postgres.irutkdcynqycaveefmpe:"+DB_PSW+"@aws-0-eu-west-3.pooler.supabase.com:5432/postgres"
)

# ❷ Create the engine once (Streamlit may cache this if needed)
engine = create_engine(SUPABASE_DB_URL, pool_pre_ping=True)

def insert_jobs(jobs_df: pd.DataFrame) -> None:
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

        st.success("✅ Data successfully inserted")

    except Exception as e:
        st.error(f"❌ Database insert failed: {e}")
