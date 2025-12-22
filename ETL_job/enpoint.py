from fastapi import FastAPI, HTTPException
from ideal_jobs_test import generate_ideal_jobs
from inference_VM.launch_VM import launch_inference_instance
from fasttext_process import call_api
from DB_jobs import get_engine, insert_embeddings
import numpy as np
import boto3

app = FastAPI()


@app.post("/ideal_jobs_embeddings")
def generate_ideal_job_embeddings(input, user_profile):

    try:
        # Generate ideal job texts
        ideal_jobs = generate_ideal_jobs(user_profile)

        # Launch inference VM
        public_ip, instance_id = launch_inference_instance(
            "inference_VM/fasttext_VM.sh",
            instance_type="t3.large")

        # Call inference API
        ideal_jobs_embeddings = {}
        for field in ideal_jobs.keys():
            field_grouped_embeddings=call_api(public_ip, ideal_jobs[field], "sentence")
            for lang in field_grouped_embeddings.keys():
                ideal_jobs_embeddings[lang]=np.mean(field_grouped_embeddings[lang][1], axis=0)
                
        # Insert in DB
        engine = get_engine()
        insert_embeddings(ideal_jobs_embeddings, engine, user_profile["user_id"])

        # Terminate inference VM
        ec2 = boto3.client("ec2", region_name="eu-west-3")
        ec2.terminate_instances(InstanceIds=[instance_id])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))