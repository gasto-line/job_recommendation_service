import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# ❶ Define your connection string directly (this is safe with anon key and correct RLS policy)
SUPABASE_DB_URL = (
    "postgresql://postgres.YOURPROJECTREF:[YOUR-ANON-PASSWORD]@aws-0-REGION.pooler.supabase.com:5432/postgres"
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
                    AI_score, user_score,
                    AI_justification, user_justification,
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
                    AI_score, user_score,
                    AI_justification, user_justification,
                    applied
                FROM tmp_jobs
                ON CONFLICT (job_hash) DO NOTHING;
            """))

        st.success("✅ Data successfully inserted")

    except Exception as e:
        st.error(f"❌ Database insert failed: {e}")
