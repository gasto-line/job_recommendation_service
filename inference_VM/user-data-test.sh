#!/bin/bash

# --- Variables ---
BUCKET="sagemaker-eu-west-3-992382721552"  
REGION="eu-west-3"
S3_FR_MODEL_KEY="facebook/fasttext-fr-vectors/model.bin"
S3_EN_MODEL_KEY="facebook/fasttext-en-vectors/model.bin"
S3_LANG_MODEL_KEY="facebook/fasttext-language-identification/model.bin"
LOCAL_FR_MODEL_PATH="/home/ec2-user/fr_model.bin"
LOCAL_EN_MODEL_PATH="/home/ec2-user/en_model.bin"
LOCAL_LANG_MODEL_PATH="/home/ec2-user/lang_model.bin"

# Ensure logs are uploaded even if script fails
trap 'aws s3 cp /var/log/cloud-init-output.log s3://'"$BUCKET"'/cloud-init-output.log || echo "Log upload failed"' EXIT

# --- Update and install packages ---
dnf update -y
dnf install -y python3-pip awscli gcc gcc-c++ make git python3-devel

# --- Install Python dependencies ---
#python3 -m venv /home/ec2-user/venv
# /home/ec2-user/venv/bin/activate
python3 -m pip install --upgrade --ignore-installed "numpy<2.0.0" setuptools wheel boto3 fasttext fastapi uvicorn psutil

# create the worker script for inference and language identification
cat << EOF > worker.py
import sys, json, fasttext

model_path = sys.argv[1]
model = fasttext.load_model(model_path)

payload_path = sys.argv[2]
payload = json.load(open(payload_path))

# payload contains list of texts / tokens ...
if "lang" in model_path:
    result = {"FR": [[],[]], "EN": [[],[]]}
    for i,text in enumerate(payload):
        full_text=" ".join(text)
        lang = model.predict(full_text)[0][0]
        if lang == "__label__fra_Latn":
            result["FR"][0].append(i)
            result["FR"][1].append(text)
        elif lang == "__label__eng_Latn":
            result["EN"][0].append(i)
            result["EN"][1].append(text)
else:
    result = {"embeddings": []}
    for text in payload:
        result["embeddings"].append([model.get_word_vector(token).tolist() for token in text])

print(json.dumps(result))
# process exits -> memory freed
EOF

# create the inference srcipt to run
cat << EOF > app.py
import boto3
import subprocess, json, os, time, psutil
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Getting variables
model_fr_path = "$LOCAL_FR_MODEL_PATH"
model_en_path = "$LOCAL_EN_MODEL_PATH"
model_lang_path = "$LOCAL_LANG_MODEL_PATH"

input_path = "/home/ec2-user/input.json"
fr_embeddings_path = "/home/ec2-user/fr_embeddings.json"
en_embeddings_path = "/home/ec2-user/en_embeddings.json"

s3 = boto3.client("s3", region_name = "$REGION")

# Download model from S3
print("Downloading from S3...")
# Choose the same directory as s3 to store on EBS volume
s3.download_file("$BUCKET", "$S3_FR_MODEL_KEY", "$LOCAL_FR_MODEL_PATH")
s3.download_file("$BUCKET", "$S3_EN_MODEL_KEY", "$LOCAL_EN_MODEL_PATH")
s3.download_file("$BUCKET", "$S3_LANG_MODEL_KEY", "$LOCAL_LANG_MODEL_PATH")
print("Download completed")

app = FastAPI()

# Define input schema
class TextInput(BaseModel):
    input: List[List[str]]

def call_worker(model_path, input_path):
    print(f"Input path from call_worker: {input_path}")
    proc = subprocess.run(
        ["python3", "worker.py", model_path, input_path],
        text=True,
        capture_output=True,
        check=False,
        timeout=100
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Worker failed: {proc.stderr}")
    return json.loads(proc.stdout)

def print_memory(label):
    process = psutil.Process(os.getpid())
    mem_mb = process.memory_info().rss / (1024*1024)
    print(f"[RAM] {label}: {mem_mb:.2f} MB")

# Application endpoint
@app.post("/embed")
def get_embedding(data: TextInput):

    print_memory("after calling enpoint, before loading input")
    input = data.input
    print_memory("after loading input")

    print("Writing the input tokens to disk")
    with open(input_path,"w") as f:
        json.dump(input, f)
    print("File size:", os.path.getsize(input_path))
    print_memory("after writing input to disk")

    # Run the language sorting worker leveraging the fasttext language detection model
    # Returns a dictionnary having one key for each language FR & EN 
    # For each key, we have two lists
    # The first is the index of that language job field in the input list
    # The second is a list for each job field containing the list of tokens of this job's field
    print("Calling worker for language identification")
    try:
        group_input=call_worker(model_lang_path, input_path)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on language identification: {e}")
    print("Retrieving worker output")
    print_memory("after getting grouped input from language identification worker")

    print("Writing french inference model input to disk")
    with open(fr_embeddings_path,"w") as f:
        json.dump(group_input["FR"][1],f)

    print("Writing english inference model input to disk")
    with open(en_embeddings_path,"w") as f:
        json.dump(group_input["EN"][1],f)

    print_memory("after writing the grouped input to disk")

    # With the output grouped by language key we can run the inference in batches
    # The inference is applied running a subprocess on the second list
    print("Calling worker for french model inference")
    try:
        FR_output = call_worker(model_fr_path,fr_embeddings_path)["embeddings"]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on french model inference: {e}")
    print("French model inference retrieved")
    print_memory("after getting the french model output")

    time.sleep(0.2)

    print("Calling worker for english model inference")
    try:
        EN_output = call_worker(model_en_path,en_embeddings_path)["embeddings"]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on english model inference: {e}")
    print("English model inference retrieved")
    print_memory("after getting the english model output")

    # Create a output variable
    group_output=group_input.copy()
    group_output["FR"][1]=FR_output
    group_output["EN"][1]=EN_output
    print_memory("after merging for final output")

    return (group_output)
    
@app.get("/health")
def health():
    return {"status": "ok"}
EOF

uvicorn app:app --host 0.0.0.0 --port 8080