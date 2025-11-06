#!/bin/bash

# --- Variables ---
BUCKET="sagemaker-eu-west-3-992382721552"  
REGION="eu-west-3"
S3_MODEL_KEY="fasttext/model_fr/model.bin"
LOCAL_MODEL_PATH="/home/ec2-user/model.bin"

# --- Update and install packages ---
dnf update -y
dnf install -y python3-pip awscli gcc gcc-c++ make git python3-devel

# --- Install Python dependencies ---
python3 -m venv /home/ec2-user/venv
source /home/ec2-user/venv/bin/activate
python3 -m pip install --upgrade setuptools wheel boto3 fasttext fastapi uvicorn

# create the inference srcipt to run
cat << EOF > app.py
import boto3
import fasttext
from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

s3 = boto3.client("s3", region_name = "$REGION")

# Download model from S3
print("Downloading from S3...")
s3.download_file("$BUCKET", "$S3_MODEL_KEY", "$LOCAL_MODEL_PATH")

#Load model and do the inference
model = fasttext.load_model("$LOCAL_MODEL_PATH")

app = FastAPI()

# Define input schema
class TextInput(BaseModel):
    input: List[List[str]]

# Example endpoint
@app.post("/embed")
def get_embedding(data: TextInput):
    input = data.input
    embeddings = []
    for text in input:
        embeddings.append([model.get_sentence_vector(token).tolist() for token in text])
    return {"embeddings": embeddings}

@app.get("/health")
def health():
    return {"status": "ok"}
EOF

uvicorn app:app --host 0.0.0.0 --port 8080