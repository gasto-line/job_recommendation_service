from miniLM_process import gen_mean_embedding, gen_embeddings, score_embeddings
from ideal_job_embedding_generator import generate_ideal_jobs
import pandas as pd
from fastapi import FastAPI, Body, BackgroundTasks
import numpy as np
from DB_jobs import insert_embedding

app = FastAPI()

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
    selected_fields = [
        "description"
        ,"title"
    ]
    # Use GPT to generate 3 ideal jobs based on user profile and take the mean of their embeddings
    ideal_jobs = generate_ideal_jobs(user_profile)
    ideal_jobs = pd.DataFrame.from_dict(ideal_jobs)
    # Compute the ideal job embedding
    ideal_job_embedding = gen_mean_embedding(ideal_jobs,selected_fields)
    insert_embedding(ideal_job_embedding, user_profile["user_id"])
    return {"ideal_job_embedding": ideal_job_embedding}