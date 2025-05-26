# %%
# GPT produced (to be revised)
# generate_top_jobs.py

import json
import os
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
from GPT_process import compute_gpt_match_score

TOP_N = 10  # Can be changed dynamically
OUTPUT_PICKLE = "top_jobs.pkl"

#Paths
adzuna_path=Path("data/adzuna_response.json")

def generate_job_hash(title, company, date):
    year = date.year
    month = date.month
    identifier = f"{title.strip().lower()}_{company.strip().lower()}_{year}_{month}"
    return pd.util.hash_pandas_object(pd.Series(identifier)).astype(str)[0]

'''
def load_and_merge_json(folder_path):
    all_jobs = []
    for file in os.listdir(folder_path):
        if file.endswith(".json"):
            with open(os.path.join(folder_path, file), "r") as f:
                jobs = json.load(f)
                all_jobs.extend(jobs)
    return pd.DataFrame(all_jobs)
'''
def load_adzuna(adzuna_path):
    # Load and flatten JSON data
    with open(adzuna_path) as f:
        data = json.load(f)
        
    #Take the first part of the JSON which contains the job details
    jobs=data['results']
    #Convert the JSON payload into a pandas dataframe
    df = pd.json_normalize(jobs)

    #Simplify names coming from subparts of the dictionary
    df.rename(columns={"company.display_name":"company","location.display_name":"location"},inplace=True)
    #to avoid problems with SQL commands later
    df.fillna("unknown",inplace=True)

    #Make title and company fields more resilient
    df.company=df.company.str.upper()
    df.title=df.title.str.lower()
    df.description=df.description.str.lower()

    # Add columns: timestamp, raw JSON payload
    df["retrieved_at"] = datetime.now(timezone.utc).date().isoformat()
    df["raw_payload"] = [json.dumps(job) for job in jobs]
    #Add the area list as a JSON in one column in case needed later
    df["area_json"] = df["location.area"].apply(json.dumps)
    #Convert the date from the response into the isoformat date
    df["created_date"] = df["created"].apply(lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")).date().isoformat())
    
    # Choose which columns to keep in the DB
    columns = [
        "redirect_url",
        "description",
        "title",
        "created_date",
        "company",
        "area_json",
        "location",
        "retrieved_at",
        "raw_payload"
    ]
    df = df[columns]
    
    return(df)

#%%
# Step 1: Load raw job data from JSON dumps
#raw_df = load_and_merge_json("./data/json_dumps")
raw_df = load_adzuna(adzuna_path)

#%%
# Step 2: Normalize and generate job_hash
raw_df["created_date"] = pd.to_datetime(raw_df["created_date"]).dt.date
raw_df["job_hash"] = raw_df.apply(lambda row: generate_job_hash(row["title"], row["company"], row["created_date"]), axis=1)
raw_df = raw_df.drop_duplicates(subset='job_hash')

#%%
# Step 3: Compute GPT scores for each job
raw_df = compute_gpt_match_score(raw_df)  # adds match_pct, model_name, prompt_ver columns

#%%
# Step 4: Sort and select top-N jobs
top_df = raw_df.sort_values("AI_score", ascending=False).head(TOP_N)

#%%
# Step 5: Save to pickle for Streamlit app
top_df.to_pickle(OUTPUT_PICKLE)
print(f"✅ Top {TOP_N} jobs saved to {OUTPUT_PICKLE}")

#%%
import smtplib
from email.message import EmailMessage
import os
# Step 6: Send myself a direct link to streamit app

#Sender and recepient
to_email = "gaston.aveline@gmail.com"
from_email = "alerts@silkworm.cloud"
#Link for streamlit
streamlit_url = "http://localhost:8501"

msg = EmailMessage()
msg["Subject"] = f"[Jobs Update] {len(top_df)} new jobs ready"
msg["From"] = from_email
msg["To"] = to_email
msg.set_content(f"""
Hi,

The job list has just been updated with {len(top_df)} offers.
Click below to rate them:

🔗 {streamlit_url}

–––
Your data pipeline
""")

# %%
import os
# Replace with your SendGrid SMTP credentials
smtp_server = 'smtp.sendgrid.net'
smtp_port = 587

username = 'apikey'  # Literally the word 'apikey'
api_key  = os.getenv("SENDGRID_API_KEY")

with smtplib.SMTP(smtp_server, smtp_port) as smtp:
    smtp.starttls()
    smtp.login(username, api_key)
    smtp.send_message(msg)
# %%
