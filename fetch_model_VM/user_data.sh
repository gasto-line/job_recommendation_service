#!/bin/bash

# --- Variables ---
BUCKET="sagemaker-eu-west-3-992382721552"   # replace with your bucket name
REGION="eu-west-3"
MODEL_HF_REPO_ID="facebook/fasttext-fr-vectors"

# Ensure logs are uploaded even if script fails
trap 'aws s3 cp /var/log/cloud-init-output.log s3://'"$BUCKET"'/cloud-init-output.log || echo "Log upload failed"' EXIT

# --- Update and install packages ---
dnf update -y
dnf install -y python3-pip awscli

# --- Install Python dependencies ---
pip install boto3
pip install huggingface_hub

# --- Python script to download and upload model ---
cat << EOF > /home/ec2-user/upload_model.py
import boto3
from huggingface_hub import hf_hub_download
import os

# Initialize S3 client
s3 = boto3.client("s3", region_name="$REGION")

# Download model from Hugging Face
print("Downloading model from Hugging Face...")
model_path = hf_hub_download(repo_id="$MODEL_HF_REPO_ID", filename="model.bin")

# Upload to S3
print("Uploading to S3...")
# We use the same path on S3 as hugginface hub
key = "$MODEL_HF_REPO_ID"+"/model.bin"
s3.upload_file(model_path, "$BUCKET", key)

EOF

# --- Run Python script ---
python3 /home/ec2-user/upload_model.py
# --- Shut down instance after completion ---
shutdown -h now
