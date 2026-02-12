from miniLM_process import gen_mean_embedding, gen_embeddings, score_embeddings
from ideal_job_embedding_generator import generate_ideal_jobs
import pandas as pd
from fastapi import FastAPI, Body, BackgroundTasks
from pydantic import BaseModel
from typing import Literal
import numpy as np
from DB_jobs import insert_embedding, profile_extraction, insert_ai_review
from data_sourcing import get_raw_df, filter_new_df

app = FastAPI()

selected_fields = [
    "description"
    ,"title"
    ]

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/ideal_jobs_embeddings")
def ideal_jobs_embeddings(background_tasks: BackgroundTasks, user_profile: dict = Body(...)):
    background_tasks.add_task(
        generate_ideal_job_embeddings,
        user_profile
    )
    return {"status": "Ideal embedding generation started"}

def generate_ideal_job_embeddings(user_profile: dict = Body(...)):

    # Use GPT to generate 3 ideal jobs based on user profile and take the mean of their embeddings
    ideal_jobs = generate_ideal_jobs(user_profile)
    ideal_jobs = pd.DataFrame.from_dict(ideal_jobs)
    # Compute the ideal job embedding
    ideal_job_embedding = gen_mean_embedding(ideal_jobs,selected_fields)
    insert_embedding(ideal_job_embedding, user_profile["user_id"])
    return {"ideal_job_embedding": ideal_job_embedding}

class AIScoringRequest(BaseModel):
    user_id: str
    implementation: Literal["miniLM"]

@app.post("/ai_scoring")
def ai_scoring(payload: AIScoringRequest, background_tasks: BackgroundTasks):
    user_id = payload.user_id
    implementation = payload.implementation

    background_tasks.add_task(
        run_AI_scoring_workflow,
        user_id)
    return {"status": "accepted"}

def run_AI_scoring_workflow(user_id: str):
    # Extract user profile and get raw job data based on that profile
    user_profile = profile_extraction(user_id)
    raw_df = get_raw_df(user_profile, number_of_jobs_per_page=50, pages=2)

    # Check that required fields are present
    required_cols = {"title", "company", "posted_date", "description"}
    missing = required_cols - set(raw_df.columns)
    if missing:
        raise ValueError(f"Missing columns in raw_df: {missing}")
    
    # Generate a unique job hash for each job to identify them and avoid duplicates in the database
    filtered_df = filter_new_df(raw_df, user_id)
    AI_scored_df = filtered_df.copy()

    # Run the scoring workflow on the new jobs and update the database with the scores
    AI_scored_df=run_miniLM_scoring(AI_scored_df, user_id)

    # Insert the scored jobs into the database
    insert_ai_review(AI_scored_df, user_id)


def run_miniLM_scoring(job_df, user_id):
    job_embeddings= gen_embeddings(job_df,selected_fields)
    profile = profile_extraction(user_id)
    miniLM_score= score_embeddings(job_embeddings, profile["minilm_embed"])
    job_df["minilm_score"]=miniLM_score
    return job_df

if __name__ == "__main__":
    
    input= {"user_id": "8d931b75-8808-4fb8-bde9-27230c187c24", "implementation": "miniLM"}
    pass
