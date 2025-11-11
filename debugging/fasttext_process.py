#%%

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
    description_response = requests.post(url, json={"input": ideal_jobs_tok_description})
    title_response = requests.post(url, json={"input": ideal_jobs_tok_title})
except RequestException as e:
        # Base class for other Requests exceptions
        print("RequestException:", str(e))
except Exception as e:
        # Fallback for unexpected errors
        print("Unexpected error:", type(e), e)

#%%
description_data = description_response.json()  # nested list(list(list(float)))
title_data = title_response.json()  # nested list(list(list(float)))
#%%
import numpy 

# For each text (description or title), take the mean token embedding 
job_description_embeddings = [np.mean(df,axis=0) for df in description_data]
job_title_embeddings = [np.mean(df,axis=0) for df in title_data]

# Create job embedding for each job offer combining title and descriptions embeddings
job_embeddings = (np.array(job_description_embeddings) + np.array(job_title_embeddings)) / 2

# Create a unique mean job embedding
job_embedding= np.mean(job_embeddings, axis=0)

#%%
import subprocess, json

def call_worker(model_path, payload):
    proc = subprocess.run(
        ["python3", "worker.py", model_path],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Worker failed: {proc.stderr}")
    return json.loads(proc.stdout)


#%%
input=[["il","elle","son"],["us","wire", "fire","style"],["all","in"], ["je","entreprise","du","technique","modélisation"]]
model_lang_path= "facebook/fasttext-language-identificationmodel.bin"
sorted_input=call_worker(model_lang_path, input)
print(sorted_input)
