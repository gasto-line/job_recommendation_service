#%%
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import Date, Boolean
from sqlalchemy.dialects.postgresql import JSON
from supabase import create_client
import os
from dotenv import load_dotenv
load_dotenv()

#%%
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

#%%
try: 
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
except Exception as e:
    print(f"Error creating Supabase client: {e}")   

def profile_extraction(user_id):
    try:
        response = supabase.table("user_profile").select("*").eq("user_id", user_id).execute()
        result = response.data[0] if response.data else None
        return result
    except Exception as e:
        print(f"Error extracting user profile: {e}")
        return None
    

def extract_jobs_hash(user_id, implementation: str) -> pd.DataFrame:
    try:
        if implementation == "FastText":
            response = supabase.table("ai_review").select("job_hash").eq("user_id", user_id).not_.is_("fasttext_score", "null").execute()
        elif implementation == "LLM":
            response = supabase.table("ai_review").select("job_hash").eq("user_id", user_id).not_.is_("llm_score", "null").execute()
        else:
            raise ValueError(f"Invalid implementation: {implementation}. Must be 'FastText' or 'LLM'.")
        result = pd.DataFrame(response.data) if response.data else None

        if implementation == "FastText":
            # Drop 
            pass
        return result
    except Exception as e:
        print(f"Error extracting job hashes: {e}")
        return pd.DataFrame(columns=["job_hash"])
    

def insert_ai_review(jobs_df: pd.DataFrame, user_id) -> list[bool, Exception]:
    jobs_df = jobs_df.copy()
    jobs_df.loc[:, "user_id"] = user_id

    # Prepare records for insertion
    selected_job_info_columns = ["job_hash",
                                 "title",
                                 "company",
                                 "description",
                                 "location",
                                 "area_json",
                                 "posted_date",
                                 "retrieved_date",
                                 "raw_payload",
                                 "redirect_url"]
    selected_job_info_columns= jobs_df.columns.intersection(selected_job_info_columns).tolist()
    job_info_df=jobs_df[selected_job_info_columns]

    selected_ai_review_columns = ["job_hash",
                                  "user_id",
                                  "ai_score",
                                  "fasttext_score",
                                  "llm_comment",
                                  "llm_version",
                                  "fasttext_version"]
    selected_ai_review_columns= jobs_df.columns.intersection(selected_ai_review_columns).tolist()
    ai_reviewed_df=jobs_df[selected_ai_review_columns]

    job_info_records = job_info_df.to_dict(orient="records")
    ai_review_records= ai_reviewed_df.to_dict(orient="records")

    # Insert into Supabase
    try:
        response1 = supabase.table("job_info").upsert(job_info_records).execute()
        response2 = supabase.table("ai_review").insert(ai_review_records).execute()
        return [True,[response1,response2]]
    except Exception as e:
        return [False,e]
    

def insert_embeddings(ideal_embeddings: dict, user_id) -> list[bool, Exception]:
    record = {"user_id": user_id, "fasttext_ref_embed": ideal_embeddings}
    try:
        response = supabase.table("user_profile").upsert(record).execute()
        return [True,response]
    except Exception as e:
        return [False,e]