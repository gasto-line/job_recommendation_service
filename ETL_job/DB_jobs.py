#%%
import pandas as pd
from supabase import create_client
import os
from config import settings

#%%
SUPABASE_URL = settings.SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY = settings.SUPABASE_SERVICE_ROLE_KEY

#%%
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def profile_extraction(user_id) -> dict:
    response = supabase.table("user_profile").select("*").eq("user_id", user_id).execute()
    extract = response.data[0]
    return extract
    
def extract_jobs_hash(user_id) -> pd.DataFrame:
    response = supabase.table("ai_review").select("job_hash").eq("user_id", user_id).not_.is_("minilm_score", "null").execute()
    extract=pd.DataFrame(response.data)
    # We create the job_has column if empty to avoid attribute error
    if extract.empty:
        extract=pd.DataFrame(columns=["job_hash"])
    return (extract.job_hash)
    

def insert_ai_review(jobs_df: pd.DataFrame, user_id) -> None:

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
                                 "url"]
    selected_job_info_columns= jobs_df.columns.intersection(selected_job_info_columns).tolist()
    job_info_df=jobs_df[selected_job_info_columns]

    selected_ai_review_columns = ["job_hash",
                                  "user_id",
                                  "minilm_score",
                                  "llm_score",
                                  "fasttext_score",
                                  "llm_comment",
                                  "llm_version",
                                  "fasttext_version"]
    selected_ai_review_columns= jobs_df.columns.intersection(selected_ai_review_columns).tolist()
    ai_reviewed_df=jobs_df[selected_ai_review_columns]

    job_info_records = job_info_df.to_dict(orient="records")
    ai_review_records= ai_reviewed_df.to_dict(orient="records")

    # Insert into Supabase
    response1 = supabase.table("job_info").upsert(job_info_records).execute()
    response2 = supabase.table("ai_review").upsert(ai_review_records, on_conflict ="user_id,job_hash" ).execute()
    
    # Get logs
    print(f"Inserted {len(response1.data)} records into job_info table and {len(response2.data)} into ai_review table.")

def insert_embedding(ideal_embedding: dict, user_id):
    record = {"user_id": user_id, "minilm_embed": ideal_embedding}
    response = supabase.table("user_profile").upsert(record).execute()
    assert(len(response.data) == 1)
    print(f"Inserted/Updated embedding for user_id: {user_id} in user_profile table.")

if __name__ == "__main__":
    """res=profile_extraction("8d931b75-8808-4fb8-bde9-27230c187c24")
    ress=[t["name"] for t in res["technical_skills"].loc[0]]
    print(ress)"""
    