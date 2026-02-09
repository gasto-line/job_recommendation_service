#%%
import pandas as pd
import os

# Hard code user_id for now
user_id= "8d931b75-8808-4fb8-bde9-27230c187c24"

# Defines the number of jobs that will be kept
TOP_N = 10  # Can be changed dynamically

#%%
from DB_jobs import profile_extraction

# Add a filter on jobs that are already in the reference database
user_profile = profile_extraction(user_id)

#%%
####################################################
# EXTRACT RAW DATA FROM DATA SOURCES
from data_sourcing import get_raw_df

raw_df = get_raw_df(user_profile, number_of_jobs_per_page=50, pages=2)

#%%
####################################################
# CLEANING AND FILTERING
from utils import generate_job_hash
# Add a new column job_hash that uniquely identify jobs
raw_df["posted_date_util"] = pd.to_datetime(raw_df["posted_date"])
raw_df["job_hash"] = raw_df.apply(lambda row: generate_job_hash(row["title"], row["company"], row["posted_date_util"]), axis=1)
raw_df = raw_df.drop_duplicates(subset='job_hash')

#%%
from DB_jobs import extract_jobs_hash
# Add a filter on jobs that are already in the reference database
exclude_set=set(extract_jobs_hash(user_id,"LLM").job_hash)
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
from ideal_job_embedding_generator import generate_ideal_jobs
# Generate the ideal job
ideal_jobs = generate_ideal_jobs(user_profile)
ideal_jobs = pd.DataFrame.from_dict(ideal_jobs)

#%%
from miniLM_process import gen_mean_embedding, gen_embeddings, score_embeddings
# Compute the ideal job embedding
ideal_job_embedding = gen_mean_embedding(ideal_jobs,selected_fields)
# Compute each jobs embedding
jobs_embeddings = gen_embeddings(AI_scored_df,selected_fields)

#Add similiarity score to the jobs df
AI_scored_df["miniLM_score"]=score_embeddings(jobs_embeddings,ideal_job_embedding)
toplist = AI_scored_df.sort_values("miniLM_score", ascending=False).head(TOP_N)
# %%
