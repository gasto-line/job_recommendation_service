# fasttext_process.py

import json, requests, numpy as np, pandas as pd
from requests.exceptions import RequestException
from utils import flatten_list


def call_api(public_ip, input, input_type: str):
    api_url = f"http://{public_ip}:8080/{input_type}"
    try:
        response = requests.post(api_url, json={"input": input})
        response.raise_for_status()  # Raise an error for bad status codes
        print("API call successful")
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"API call failed: {e}")

def token_tofield_embeddings(data: dict):
    # the data retrieved from the inference VM is in the form {"FR": [ [index],[[]..[token_embeddings]..[]] ],"EN": [ [index],[[embeddings]] ]}
    # We create an output in the form {"FR":[[index],[job_field_embeddings]],"EN":[[index],[job_field_embeddings]]}
    output = {
    "FR": [data["FR"][0], None],
    "EN": [data["EN"][0], None]
    }
    for lang in ["FR","EN"]:
        field_embeddings=[np.mean(df, axis=0) for df in data[lang][1]]
        output[lang][1]=field_embeddings
    
    return output

def get_field_embeddings(public_ip,input,input_type: str):
    data = call_api(public_ip, input, input_type)
    if input_type=="token":
        return token_tofield_embeddings(data)
    elif input_type=="sentence": 
        return data
    else:
        raise ValueError(f"Invalid input_type: {input_type}. Must be 'token' or 'sentence'.")

# Takes in the public_ip of the instance and the list of jobs field in its tokenized form
# Returns a dictionnary of format {"FR":[[index],[job_field_embeddings]],"EN":[[index],[job_field_embeddings]]}
def run_fasttext_inference(public_ip,jobs_tokenized_field: list[list[str]]):

    #  Call the API for each tokenized jobs' field
    api_url = f"http://{public_ip}:8080/token"
    response = requests.post(api_url, json={"input": jobs_tokenized_field}) 

    # Handle API call errors
    if not response.ok:  # True if status code NOT in the 200–299 range
        raise RuntimeError(
            f"API call failed with status {response.status_code}: {response.text}"
        )
    print("API call successful")

    # the data retrieved from the inference VM is in the form {"FR": [ [index],[[]..[token_embeddings]..[]] ],"EN": [ [index],[[embeddings]] ]}
    data = response.json()

    # We create an output in the form {"FR":[[index],[job_field_embeddings]],"EN":[[index],[job_field_embeddings]]}
    output = {
    "FR": [data["FR"][0], None],
    "EN": [data["EN"][0], None]
    }
    for lang in ["FR","EN"]:
        # Taking the mean of the token embeddings for each field
        field_embeddings=[np.mean(df, axis=0) for df in data[lang][1]]
        output[lang][1]=field_embeddings

    # Sanity checks 
    assert len(output["FR"][0])==len(output["FR"][1])
    assert len(output["EN"][0])==len(output["EN"][1])
    assert len(output["FR"][0])+len(output["EN"][0])==len(jobs_tokenized_field)
    return (output)

from numpy import dot
from numpy.linalg import norm

# Returns field scores in the initial job list order regardless of language
def get_field_wise_scoring(jobs_field_grouped_embeddings,field: str):

    # Retrieve the ideal job embedding for this field
    with open("data/ideal_jobs_embedding_dict.json") as f:
        ideal_jobs_field_grouped_embedding = json.load(f)[field]

    # Here we produce a similarity comparison between the the ideal jobs field and the respective job field
    # Since the french and english model have a different vector space 
    # The similarity calculation is done in batches for each language
    def similarity(vec1,vec2):
        return(dot(vec1, vec2) / (norm(vec1) * norm(vec2))) 

    zipped_similarity=[]
    #jobs_field_grouped_similarity = jobs_field_grouped_embeddings.copy()
    for lang in ["FR","EN"]:
        ref=ideal_jobs_field_grouped_embedding[lang]
        order=jobs_field_grouped_embeddings[lang][0]
        embeddings=jobs_field_grouped_embeddings[lang][1]
        #jobs_field_grouped_similarity[lang][1]= [similarity(ref,embedding) for embedding in embeddings]
        sim = [similarity(ref,embedding) for embedding in embeddings]
        zipped_similarity+=list(zip(order,sim))

    output = [v for _,v in sorted(zipped_similarity)]
    
    # Sanity checks
    assert len(output)==len(jobs_field_grouped_embeddings["FR"][0])+len(jobs_field_grouped_embeddings["EN"][0])
    return(output)
        

def get_fasttext_score(input_df,input_type, batch_size,public_ip):
    selected_fields = input_df.columns.tolist()
    fasttext_score = []
    if len(input_df) > batch_size:
        batches = [input_df.iloc[i:i+batch_size] for i in range(0, len(input_df), batch_size)]
    else:
        batches = [input_df] 

    for batch in batches:
        field_score = []
        for field in selected_fields:
            #jobs_field_grouped_embeddings=run_fasttext_inference(public_ip,batch[field].tolist())
            jobs_field_grouped_embeddings=get_field_embeddings(public_ip=public_ip
                                                               ,input=batch[field].tolist()
                                                               ,input_type=input_type)
            jobs_field_scores = get_field_wise_scoring(jobs_field_grouped_embeddings,field)
            field_score.append(jobs_field_scores)

        jobs_general_scores=np.mean(field_score,axis=0)
        fasttext_score.append(jobs_general_scores)

    return((flatten_list(fasttext_score)))

        


