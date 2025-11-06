#%%
import yaml
import pandas as pd
import os

#%%
with open("config/ideal_job_1.yaml","r") as f:
    ideal_job_1=yaml.safe_load(f)

#%%
ideal_jobs = {}
for i in range(1, 6):
    path = f"config/ideal_job_{i}.yaml"
    with open(path, "r") as f:
        ideal_jobs[f"ideal_job_{i}"] = yaml.safe_load(f)

#%%
ideal_jobs_df = pd.DataFrame(ideal_jobs)
ideal_jobs_df = pd.DataFrame.transpose(ideal_jobs_df)
# %%
import re
import str

def tokenisation(text):
    text = re.sub(r"[^a-zA-Z0-9\s#&œ+éèêàâç'’]","",text)
    text = text.lower()
    text = re.split(r"['’\s]",text)
    while "" in text:
        text.remove("")
    while "l" in text:
        text.remove("l")
    while "d" in text:
        text.remove("d")
    return (text)

# %%
ideal_jobs_tok_df = ideal_jobs_df.applymap(tokenisation)

ideal_jobs_tok_description_fr = ideal_jobs_tok_df["description_fr"].tolist()
ideal_jobs_tok_title_fr = ideal_jobs_tok_df["title_fr"].tolist()

# %%
import subprocess, json
import time, requests

# Step 1: Launch instance and capture the Instance ID
result = subprocess.run(
    ["bash", "inference_VM/EC2_provisioning.sh"], capture_output=True, text=True, check=True
)
# The public IP will be in stdout
public_ip = result.stdout.strip()
print(f"✅ Public IP: {public_ip}")

# Step 2: Wait for the app to be ready
url = f"http://{public_ip}:8080/health"

while True:
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print("✅ App is ready!")
            break
    except requests.RequestException:
        pass
    time.sleep(30)
    print("Waiting for the app to be ready...")

# Step 3: Call the API
import pandas as pd
import numpy as np
from requests.exceptions import RequestException

url = f"http://{public_ip}:8080/embed"

try: 
    description_response = requests.post(url, json={"input": ideal_jobs_tok_description_fr})
    title_response = requests.post(url, json={"input": ideal_jobs_tok_title_fr})
except RequestException as e:
        # Base class for other Requests exceptions
        print("RequestException:", str(e))
except Exception as e:
        # Fallback for unexpected errors
        print("Unexpected error:", type(e), e)


description_data = description_response.json()["embeddings"]  # nested list(list(list(float)))
title_data = title_response.json()["embeddings"]  # nested list(list(list(float)))
#%%
import numpy 

# For each text (description or title), take the mean token embedding 
job_description_embeddings = [np.mean(df,axis=0) for df in description_data]
job_title_embeddings = [np.mean(df,axis=0) for df in title_data]

# Create job embedding for each job offer combining title and descriptions embeddings
job_embeddings = (np.array(job_description_embeddings) + np.array(job_title_embeddings)) / 2

# Create a unique mean job embedding
job_embedding= np.mean(job_embeddings, axis=0)
