#%%
import pandas as pd
import os

# Defines the number of jobs that will be kept
TOP_N = 10  # Can be changed dynamically

#%%
####################################################
# EXTRACT RAW DATA FROM DATA SOURCES
from data_sources.adzuna import load_adzuna
import pandas as pd
raw_df_1 = load_adzuna(50,1)
raw_df_2 = load_adzuna(50,2)
raw_df=pd.concat([raw_df_1,raw_df_2]).reset_index()

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
# Import the jobs database password from env variables
DB_PSW = os.getenv("DB_PSW")
if not DB_PSW:
    raise ValueError("Database password (DB_PSW) is not set in environment variables.")
# Add a filter on jobs that are already in the reference database
engine = get_engine(DB_PSW)
exclude_set=set(extract_jobs_hash(engine).job_hash)
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

public_ip, instance_id =launch_inference_instance("inference_VM/fasttext_token_VM.sh")

#%%
from fasttext_process import get_fasttext_score
from utils import tokenization

token_input_df = AI_scored_df[selected_fields].applymap(tokenization)
AI_scored_df["fasttext_score"]=get_fasttext_score(public_ip=public_ip
                                                  ,input_df=token_input_df
                                                  ,batch_size=50)

#%%
import boto3
ec2 = boto3.client("ec2", region_name="eu-west-3")
ec2.terminate_instances(InstanceIds=[instance_id])

#%%
####################################################
# GPT PROCESS
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