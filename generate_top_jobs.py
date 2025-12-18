#%%
import pandas as pd
import os

# Hard code user_id for now
user_id= "8d931b75-8808-4fb8-bde9-27230c187c24"

# Defines the number of jobs that will be kept
TOP_N = 10  # Can be changed dynamically

#%%
from DB_jobs import profile_extraction, get_engine

# Add a filter on jobs that are already in the reference database
engine = get_engine()
user_profile = profile_extraction(engine, user_id)

#%%
####################################################
# EXTRACT RAW DATA FROM DATA SOURCES
from data_sourcing import generate_adzuna_keywords, load_adzuna

adzuna_keywords=generate_adzuna_keywords(user_profile)
raw_df = None
for i in range(5):
    raw_dfi= load_adzuna(50,i+1,adzuna_keywords)
    raw_df = pd.concat([raw_df,raw_dfi]) if raw_df is not None else raw_dfi
raw_df= raw_df.reset_index()

#%%
"""####################################################
# EXTRACT RAW DATA FROM DATA SOURCES
from data_sources.adzuna import load_adzuna
import pandas as pd
raw_df_1 = load_adzuna(50,1)
raw_df_2 = load_adzuna(50,2)
raw_df=pd.concat([raw_df_1,raw_df_2]).reset_index()"""

#%%
####################################################
# CLEANING AND FILTERING
from utils import generate_job_hash
# Add a new column job_hash that uniquely identify jobs
raw_df["posted_date"] = pd.to_datetime(raw_df["posted_date"])
raw_df["job_hash"] = raw_df.apply(lambda row: generate_job_hash(row["title"], row["company"], row["posted_date"]), axis=1)
raw_df = raw_df.drop_duplicates(subset='job_hash')

#%%
from DB_jobs import extract_jobs_hash, get_engine
# Add a filter on jobs that are already in the reference database
engine = get_engine()
exclude_set=set(extract_jobs_hash(engine,user_id).job_hash)
# mask rows whose 'job_hash' is NOT in that set
filtered_df = raw_df.loc[~raw_df['job_hash'].isin(exclude_set)]

#%%
AI_scored_df = filtered_df.copy()

####################################################
# FASTEXT PROCESS

# Fields taken into account for fasttext scoring
selected_fields = [
    "description"
    ,"title"
]

#%%
from inference_VM.launch_VM import launch_inference_instance

public_ip, instance_id =launch_inference_instance("inference_VM/fasttext_VM.sh",instance_type="t3.large")

#%%
from fasttext_process import get_fasttext_score
from utils import tokenization

#token_input_df = AI_scored_df[selected_fields].applymap(tokenization)
sentence_input_df = AI_scored_df[selected_fields]
AI_scored_df["fasttext_score"]=get_fasttext_score(public_ip=public_ip
                                                  ,input_df=sentence_input_df
                                                  ,input_type="sentence"
                                                  ,batch_size=50)
AI_scored_df["fasttext_version"]= "1.0.0"

#%%
import boto3
ec2 = boto3.client("ec2", region_name="eu-west-3")
ec2.terminate_instances(InstanceIds=[instance_id])

#%%
####################################################
# GPT PROCESS
from GPT_process import compute_gpt_match_score
# Add a column with AI_score and AI_justification for each job
AI_scored_df = compute_gpt_match_score(AI_scored_df,user_profile) 

#%%
####################################################
# INSERT INTO THE DATABASE
from DB_jobs import insert_ai_review, get_engine

engine = get_engine()
insert_ai_review(AI_scored_df,engine,user_id)

#%%
# Generate the top list for each of the implementations
fasttext_toplist = AI_scored_df.sort_values("fasttext_score", ascending=False).head(TOP_N)
FASTTEXT_PICKLE= "fasttext_toplist.pkl"
fasttext_toplist.to_pickle(FASTTEXT_PICKLE)
print(f"Top fasttext {TOP_N} jobs saved to {FASTTEXT_PICKLE}")

#%%
llm_toplist = AI_scored_df.sort_values("ai_score", ascending=False).head(TOP_N)
OUTPUT_PICKLE = "llm_toplist.pkl"
llm_toplist.to_pickle(OUTPUT_PICKLE)
print(f"Top {TOP_N} jobs saved to {OUTPUT_PICKLE}")

"""
from email_sending import send_email
# Send myself a direct link to streamlit
send_email(TOP_N)
"""