#!/bin/bash

# --- Variables ---
BUCKET="sagemaker-eu-west-3-992382721552"   # replace with your bucket name
REGION="eu-west-3"
FR_MODEL_S3_PREFIX="fasttext/model_fr"

# Ensure logs are uploaded even if script fails
trap 'aws s3 cp /var/log/cloud-init-output.log s3://'"$BUCKET"'/cloud-init-output.log || echo "Log upload failed"' EXIT

# --- Update and install packages ---
dnf update -y
dnf install -y python3-pip awscli

# --- Install Python dependencies ---
pip install boto3
pip install huggingface_hub

# --- Python script to download and upload model ---
cat << EOF > /home/ec2-user/upload_fasttext.py
import boto3
from huggingface_hub import hf_hub_download
import os

prefix = "fasttext/model_fr"

# Initialize S3 client
s3 = boto3.client("s3", region_name="$REGION")

# Download model from Hugging Face
print("Downloading FastText model from Hugging Face...")
model_path = hf_hub_download(repo_id="facebook/fasttext-fr-vectors", filename="model.bin")

# Upload to S3
print("Uploading to S3...")
key = f"{"$FR_MODEL_S3_PREFIX"}/model.bin"
s3.upload_file(model_path, "$BUCKET", key)

EOF

# --- Run Python script ---
python3 /home/ec2-user/upload_fasttext.py
# --- Shut down instance after completion ---
shutdown -h now
