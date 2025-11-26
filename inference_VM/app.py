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

    print("Writing the input tokens to disk")
    with open(input_path,"w") as f:
        json.dump(input, f)

    print("File size:", os.path.getsize(input_path))

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

    print("Writing french inference model input to disk")
    with open(fr_embeddings_path,"w") as f:
        json.dump(group_input["FR"][1],f)

    print("Writing english inference model input to disk")
    with open(en_embeddings_path,"w") as f:
        json.dump(group_input["EN"][1],f)

    # With the output grouped by language key we can run the inference in batches
    # The inference is applied running a subprocess on the second list
    print("Calling worker for french model inference")
    try:
        FR_output = call_worker(model_fr_path,fr_embeddings_path)["embeddings"]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on french model inference: {e}")
    print("French model inference retrieved")

    print("Calling worker for english model inference")
    try:
        EN_output = call_worker(model_en_path,en_embeddings_path)["embeddings"]
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=f"worker failed on english model inference: {e}")
    print("English model inference retrieved")

    # Create a output variable
    group_output=group_input.copy()
    group_output["FR"][1]=FR_output
    group_output["EN"][1]=EN_output

    return (group_output)

@app.get("/health")
def health():
    return {"status": "ok"}