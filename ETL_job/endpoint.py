from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
from ideal_job_embedding_generator import generate_ideal_jobs
from launch_VM import launch_inference_instance
from fasttext_process import call_api, get_fasttext_score
from DB_jobs import insert_embeddings, profile_extraction, extract_jobs_hash, insert_ai_review
from data_sourcing import get_raw_df
from utils import generate_job_hash
from pathlib import Path
from GPT_process import compute_gpt_match_score
from pydantic import BaseModel
from typing import Literal
import numpy as np
import pandas as pd
import boto3
import traceback
import logging

app = FastAPI()
logger = logging.getLogger(__name__)

# This file is inside: job_recommendation_service/ETL_job/...
REPO_ROOT = Path(__file__).resolve().parents[1]

VM_SCRIPT_PATH = REPO_ROOT / "inference_VM" / "VM_config.sh"
VM_USER_DATA_PATH = REPO_ROOT / "inference_VM" / "user_data.sh"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ideal_jobs_embeddings")
def ideal_jobs_embeddings(background_tasks: BackgroundTasks,user_profile: dict = Body(...)):
    background_tasks.add_task(
        generate_ideal_job_embeddings,
        user_profile
    )
    return {"status": "Ideal embedding generation started"}

def generate_ideal_job_embeddings(user_profile: dict = Body(...)):

    instance_id = None  # so we can always clean up
    try:
        print("[1/4] Generating ideal job texts")
        ideal_jobs = generate_ideal_jobs(user_profile)

        print("[2/4] Launching inference VM")
        public_ip, instance_id = launch_inference_instance(
            str(VM_SCRIPT_PATH),
            str(VM_USER_DATA_PATH),
            instance_type="t3.large"
        )

        print("[3/4] Calling inference API")
        ideal_jobs_embeddings = {}

        for field, texts in ideal_jobs.items():
            ideal_jobs_embeddings[field] = {}

            field_grouped_embeddings = call_api(
                public_ip,
                texts,
                "sentence"
            )

            for lang, values in field_grouped_embeddings.items():
                ideal_jobs_embeddings[field][lang] = np.mean(
                    values[1], axis=0
                ).tolist()  # convert to list for JSON serialization

        print("[4/4] Inserting embeddings into DB")
        success, error = insert_embeddings(
            ideal_jobs_embeddings,
            user_profile["user_id"]
        )

        if not success:
            raise RuntimeError(f"DB insert failed: {error}")

        return {"status": "success"}

    except KeyError as e:
        # Input structure error
        print(f"Input structure error: {e}")

    except Exception:
        traceback.print_exc()
        return

    finally:
        if instance_id:
            print("Cleaning up inference VM")
            try:
                ec2 = boto3.client("ec2", region_name="eu-west-3")
                ec2.terminate_instances(InstanceIds=[instance_id])
            except Exception as e:
                print(f"Failed to terminate instance {instance_id}: {e}")



def run_fasttext_scoring(AI_scored_df, user_profile):
    instance_id = None  # so we can always clean up
    try:   
        print("[1/3] Launching inference VM")
        public_ip, instance_id = launch_inference_instance(
            str(VM_SCRIPT_PATH),
            str(VM_USER_DATA_PATH),
            instance_type="t3.large")
            
        print("[2/3] Calling inference API for fasttext scoring")
        sentence_input_df = AI_scored_df[["description","title"]]
        AI_scored_df["fasttext_score"]=get_fasttext_score(public_ip=public_ip
                                                            ,input_df=sentence_input_df
                                                            ,input_type="sentence"
                                                            ,batch_size=50
                                                            ,user_profile=user_profile)
        AI_scored_df["fasttext_version"]= "1.0.0"
    except Exception:
        traceback.print_exc()
        return
    finally:
        print("[3/3] Terminate inference VM")
        if instance_id:
            try:
                ec2 = boto3.client("ec2", region_name="eu-west-3")
                ec2.terminate_instances(InstanceIds=[instance_id])
                logger.info("EC2 instance terminated", instance_id=instance_id)
            except Exception:
                logger.exception(
                    "Failed to terminate EC2 instance",
                    instance_id=instance_id
                )

    return AI_scored_df

def run_llm_scoring(AI_scored_df, user_profile):
    try:
        print("Computing GPT match score")
        AI_scored_df = compute_gpt_match_score(AI_scored_df,user_profile)
    except Exception:
        traceback.print_exc()
        return
    return AI_scored_df


def run_AI_scoring_workflow(user_id: str, implementation: str):
    try:
        print("1.0 Data sourcing and filtering")
        user_profile = profile_extraction(user_id)
        raw_df = get_raw_df(user_profile, number_of_jobs_per_page=50, pages=2)

        # Check that required fields are present
        required_cols = {"title", "company", "posted_date", "description"}
        missing = required_cols - set(raw_df.columns)
        if missing:
            raise ValueError(f"Missing columns in raw_df: {missing}")
        
        # Add a new column job_hash that uniquely identify jobs
        raw_df["posted_date_util"] = pd.to_datetime(raw_df["posted_date"])
        raw_df["job_hash"] = raw_df.apply(lambda row: generate_job_hash(row["title"], row["company"], row["posted_date_util"]), axis=1)
        raw_df = raw_df.drop_duplicates(subset='job_hash')

        # Add a filter on jobs that are already in the reference database
        extract=extract_jobs_hash(user_id, implementation) 
        if extract is None:
            exclude_set=set()
        else:
            exclude_set=set(extract_jobs_hash(user_id, implementation).job_hash)
        # mask rows whose 'job_hash' is NOT in that set
        filtered_df = raw_df.loc[~raw_df['job_hash'].isin(exclude_set)]

        AI_scored_df = filtered_df.copy()
    except Exception:
        traceback.print_exc()
        return
    
    SCORERS = {
    "FastText": run_fasttext_scoring,
    "LLM": run_llm_scoring
    }
    scorer = SCORERS.get(implementation)
    if scorer:
        AI_scored_df = scorer(AI_scored_df, user_profile)
    else: 
        raise KeyError(f"Invalid implementation: {implementation}. Must be 'FastText' or 'LLM'.")
    
    try:                
        print("3.0 Inserting AI review into DB")
        success, error = insert_ai_review(AI_scored_df,user_id)
        if not success:
            raise RuntimeError(f"DB insert failed: {error}")
        return {"status": "success"}
    except KeyError as e:
        print(f"Input structure error: {e}")
    except Exception:
        traceback.print_exc()
        return  

class AIScoringRequest(BaseModel):
    user_id: str
    implementation: Literal["FastText", "LLM"]

@app.post("/ai_scoring")
def ai_scoring(payload: AIScoringRequest, background_tasks: BackgroundTasks):
    user_id = payload.user_id
    implementation = payload.implementation

    background_tasks.add_task(
        run_AI_scoring_workflow,
        user_id,
        implementation)
    return {"status": "accepted"}