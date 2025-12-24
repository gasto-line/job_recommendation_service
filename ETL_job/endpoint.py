from fastapi import FastAPI, HTTPException, Body
from ideal_job_embedding_generator import generate_ideal_jobs
from launch_VM import launch_inference_instance
from fasttext_process import call_api
from DB_jobs import insert_embeddings
from pathlib import Path
import numpy as np
import boto3

app = FastAPI()

# This file is inside: job_recommendation_service/ETL_job/...
REPO_ROOT = Path(__file__).resolve().parents[1]

VM_SCRIPT_PATH = REPO_ROOT / "inference_VM" / "VM_config.sh"
VM_USER_DATA_PATH = REPO_ROOT / "inference_VM" / "user_data.sh"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ideal_jobs_embeddings")
def generate_ideal_job_embeddings(user_profile: dict = Body(...)):

    try:
        # Generate ideal job texts
        ideal_jobs = generate_ideal_jobs(user_profile)

        # Launch inference VM
        # It returns a dict in format: {"title": ["title1_fr", "title1_en" ,... ,"title3_en"], "description":["description1_fr", "description1_en" ,... ,"description3_en"]}
        public_ip, instance_id = launch_inference_instance(
            str(VM_SCRIPT_PATH),
            str(VM_USER_DATA_PATH),
            instance_type="t3.large")

        # Call inference API
        ideal_jobs_embeddings = {}
        for field in ideal_jobs.keys():
            # The inference VM automatically sorts the list of field values by language
            field_grouped_embeddings=call_api(public_ip, ideal_jobs[field], "sentence")
            for lang in field_grouped_embeddings.keys():
                ideal_jobs_embeddings[lang]=np.mean(field_grouped_embeddings[lang][1], axis=0)
                
        # Insert in DB
        insert_embeddings(ideal_jobs_embeddings, user_profile["user_id"])

        # Terminate inference VM
        ec2 = boto3.client("ec2", region_name="eu-west-3")
        ec2.terminate_instances(InstanceIds=[instance_id])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))