#%%
import pandas as pd
import os

# Defines the number of jobs that will be kept
TOP_N = 10  # Can be changed dynamically

# Import the jobs database password from env variables
DB_PSW = os.getenv("DB_PSW")
if not DB_PSW:
    raise ValueError("Database password (DB_PSW) is not set in environment variables.")

# Import the jobs database password from env variables
DB_PSW = os.getenv("DB_PSW")
if not DB_PSW:
    raise ValueError("Database password (DB_PSW) is not set in environment variables.")

#%%
# Builds the data gathered from various sources
from data_sources.adzuna import load_adzuna
raw_df = load_adzuna(25)

#%%
# Function that generates a unique identifier for the jobs
def generate_job_hash(title, company, pub_date):
    year = pub_date.year
    month = pub_date.month
    identifier = f"{title.strip().lower()}_{company.strip().lower()}_{year}_{month}"
    return pd.util.hash_pandas_object(pd.Series(identifier)).astype(str)[0]
# Add a new column job_hash that uniquely identify jobs
raw_df["posted_date"] = pd.to_datetime(raw_df["posted_date"])
raw_df["job_hash"] = raw_df.apply(lambda row: generate_job_hash(row["title"], row["company"], row["posted_date"]), axis=1)
raw_df = raw_df.drop_duplicates(subset='job_hash')

#%%
# Add a filter on jobs that are already in the reference database
from DB_jobs import extract_jobs_hash, get_engine
engine = get_engine(DB_PSW)
exclude_set=set(extract_jobs_hash(engine).job_hash)
# mask rows whose 'job_hash' is NOT in that set
filtered_df = raw_df.loc[~raw_df['job_hash'].isin(exclude_set)]


#%%
from fasttext_process import run_fasttext_inference, tokenization, launch_inference_instance

input_df = filtered_df[["description","title"]].applymap(tokenization)
public_ip=launch_inference_instance()

#%%
jobs_description_grouped_embeddings=run_fasttext_inference(public_ip,input_df["description"].tolist())
jobs_title_grouped_embeddings=run_fasttext_inference(public_ip,input_df["title"].tolist())

#%%
from fasttext_process import get_field_wise_scoring
import numpy as np
AI_scored_df = filtered_df.copy()

jobs_description_scores = get_field_wise_scoring(jobs_description_grouped_embeddings,"description")
jobs_title_scores = get_field_wise_scoring(jobs_description_grouped_embeddings,"title")
jobs_general_scores=np.mean([jobs_description_scores]+[jobs_title_scores],axis=0)

AI_scored_df["fasttext_score"]=jobs_general_scores

#%%
from GPT_process import compute_gpt_match_score
# Add a column with AI_score and AI_justification for each job
AI_scored_df = compute_gpt_match_score(AI_scored_df) 

#%%
# Generate the top list for each of the implementations
fasttext_toplist = AI_scored_df.sort_values("fasttext_score", ascending=False).head(TOP_N)
FASTTEXT_PICKLE= "fasttext_toplist.pkl"
fasttext_toplist.to_pickle(FASTTEXT_PICKLE)
print(f"Top fasttext {TOP_N} jobs saved to {FASTTEXT_PICKLE}")

top_df = AI_scored_df.sort_values("ai_score", ascending=False).head(TOP_N)
OUTPUT_PICKLE = "top_jobs.pkl"
top_df.to_pickle(OUTPUT_PICKLE)
print(f"Top {TOP_N} jobs saved to {OUTPUT_PICKLE}")

"""
from email_sending import send_email
# Send myself a direct link to streamlit
send_email(TOP_N)
"""