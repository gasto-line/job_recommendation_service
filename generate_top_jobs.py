#%%
import pandas as pd

# Defines the number of jobs that will be kept
TOP_N = 10  # Can be changed dynamically

#%%
# Builds the data gathered from various sources
from data_sources.adzuna import load_adzuna
raw_df = load_adzuna()

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
from DB_extracts import extract_jobs_hash
exclude_set=set(extract_jobs_hash().job_hash)
# mask rows whose 'job_hash' is NOT in that set
filtered_df = raw_df.loc[~raw_df['job_hash'].isin(exclude_set)]

#%%
from GPT_process import compute_gpt_match_score
# Add a column with AI_score and AI_justification for each job
AI_scored_df = compute_gpt_match_score(filtered_df) 
# Sort and select top-N jobs
top_df = AI_scored_df.sort_values("ai_score", ascending=False).head(TOP_N)
# Save to pickle for Streamlit app
OUTPUT_PICKLE = "data/top_jobs.pkl"
top_df.to_pickle(OUTPUT_PICKLE)
print(f"Top {TOP_N} jobs saved to {OUTPUT_PICKLE}")


'''
#%%
from email_sending import send_email
# Send myself a direct link to streamlit
send_email(TOP_N)
'''