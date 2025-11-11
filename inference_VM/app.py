import boto3
import subprocess, json
from typing import List
from fastapi import FastAPI
from fastapi import HTTPException
from pandas.core import groupby
from pydantic import BaseModel

# Getting variables
bucket = "$BUCKET"
model_fr_path = "$LOCAL_FR_MODEL_PATH"
model_en_path = "$LOCAL_EN_MODEL_PATH"
model_lang_path = "$LOCAL_LANG_MODEL_PATH"

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

def call_worker(model_path, payload):
    proc = subprocess.run(
        ["python3", "worker.py", model_path],
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
        timeout=120
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Worker failed: {proc.stderr}")
    return json.loads(proc.stdout)

# Application endpoint
@app.post("/embed")
def get_embedding(data: TextInput):
    input = data.input
    # Run the language sorting worker leveraging the fasttext language detection model
    # Returns a dictionnary having one key for each language FR & EN 
    # For each key, we have a list containing the list of tokens 
    # and a list with their corresponding index
    print("Calling worker for language identification")
    try:
        group_input=call_worker(model_lang_path, input)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on language identification: {e}")
    print("Retrieving worker output")

    print("Calling worker for french model inference")
    FR_input = group_input["FR"][1]
    try:
        FR_output = call_worker(model_fr_path,FR_input)["embeddings"]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on french model inference: {e}")
    print("French model inference retrieved")

    print("Calling worker for english model inference")
    EN_input = group_input["EN"][1]
    try:
        EN_output = call_worker(model_en_path,EN_input)["embeddings"]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on english model inference: {e}")
    print("English model inference retrieved")

    # We join the french and english indexes
    order=group_input["FR"][0]+group_input["EN"][0]
    # Make sure that the index list is complete
    assert(sorted(order) == list(range(len(input))))
    # We join the outputs in the same order
    output=FR_output+EN_output
    # Get the embeddings in their original order
    ordered_output=[output[i] for i in order]

    return (ordered_output)

@app.get("/health")
def health():
    return {"status": "ok"}