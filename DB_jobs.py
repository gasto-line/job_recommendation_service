import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import Date, Boolean
from sqlalchemy.dialects.postgresql import JSON
import os

# Import the jobs database password from env variables
DB_PSW = os.getenv("DB_PSW")
if not DB_PSW:
    raise ValueError("Database password (DB_PSW) is not set in environment variables.")

username = "irutkdcynqycaveefmpe"
port = 5432
host = "aws-0-eu-west-3.pooler.supabase.com"
database = "postgres"

def get_engine():
    connection_string = f"postgresql://{database}.{username}:{DB_PSW}@{host}:{port}/{database}"
    return create_engine(connection_string, pool_pre_ping=True)

def profile_extraction(engine, user_id):
    try:
        with engine.connect() as conn:
            query = text("""
                SELECT *
                FROM user_profile
                WHERE user_id = :user_id
            """)
            result = conn.execute(query, {"user_id": user_id}).mappings().one()
            return dict(result) if result else None
    except Exception as e:
        print(f"Error extracting user profile: {e}")
        return None
    

def extract_jobs_hash(engine,user_id):
    """
    Extracts job hashes from the database.
    
    Returns:
        pd.DataFrame: A DataFrame containing job hashes.
    """
    try:
        with engine.connect() as conn:
            query = text("SELECT job_hash FROM ai_review WHERE user_id = :user_id")
            result = pd.read_sql(query, conn, params = {"user_id": user_id})
            return result
    except Exception as e:
        print(f"Error extracting job hashes: {e}")
        return pd.DataFrame(columns=["job_hash"])
    

def insert_ai_review(jobs_df: pd.DataFrame,engine, user_id) -> list[bool, Exception]:
    records = jobs_df.to_dict(orient="records")
    records = [{**record, "user_id": user_id} for record in records]

    optional_fields = ["ai_score",
                        "fasttext_score",
                          "llm_comment",
                            "llm_version",
                              "fasttext_version",
                                "company",
                                  "description",
                                    "location",
                                      "area_json"]
    
    for record in records:
        for field in optional_fields:
            if field not in record:
                record[field] = None

    try:
        with engine.begin() as conn:

            conn.execute(text("""
                            INSERT INTO job_info (
                                job_hash, title, company, description, location, area_json, posted_date, retrieved_date, raw_payload, url
                            )
                            VALUES (
                                :job_hash, :title, :company, :description, :location, :area_json, :posted_date, :retrieved_date, :raw_payload, :redirect_url
                            )
                            ON CONFLICT (job_hash) DO NOTHING
                            """),
                            records)
            
            conn.execute(text("""
                            INSERT INTO ai_review (
                                job_hash, user_id, llm_score, fasttext_score, llm_comment, llm_version, fasttext_version 
                            )
                            VALUES (
                                :job_hash, :user_id, :llm_score, :fasttext_score, :llm_comment, :llm_version, :fasttext_version
                            )
                            """),
                            records)
        return [True,None]
    except Exception as e:
        return [False,e]