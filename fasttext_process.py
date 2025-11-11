# fasttext_process.py

import subprocess, re, json, time, requests, numpy as np, pandas as pd
from requests.exceptions import RequestException

def tokenization(text):
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

# Takes tokenised list of jobs description and title 
# Returns an embedding for each jobs taking the mean of title and description embeddings
# Returns the means of all those embeddings too if needed
def run_fasttext_inference(ideal_jobs_tok_description, ideal_jobs_tok_title):
    """Run full EC2 provisioning and inference workflow, returning job embeddings."""
    
    # Step 1: Launch instance
    result = subprocess.run(
        ["bash", "inference_VM/EC2_provisioning.sh"], capture_output=True, text=True, check=True
    )
    public_ip = result.stdout.strip()
    print(f"✅ Public IP: {public_ip}")

    # Step 2: Wait for the app
    url = f"http://{public_ip}:8080/health"
    while True:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print("✅ App is ready!")
                break
        except RequestException:
            pass
        time.sleep(30)
        print("Waiting for the app to be ready...")

    # Step 3: Call the API
    api_url = f"http://{public_ip}:8080/embed"
    description_response = requests.post(api_url, json={"input": ideal_jobs_tok_description})
    title_response = requests.post(api_url, json={"input": ideal_jobs_tok_title})

    description_data = description_response.json()
    title_data = title_response.json()

    job_description_embeddings = [np.mean(df, axis=0) for df in description_data]
    job_title_embeddings = [np.mean(df, axis=0) for df in title_data]
    job_embeddings = (np.array(job_description_embeddings) + np.array(job_title_embeddings)) / 2
    job_embedding = np.mean(job_embeddings, axis=0)

    return job_embedding, job_embeddings