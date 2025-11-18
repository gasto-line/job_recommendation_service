# fasttext_process.py

import subprocess, re, json, time, requests, numpy as np, pandas as pd
from requests.exceptions import RequestException

def tokenization(text):
    text = re.sub(r"[^a-zA-Z0-9\s#&œ+éèêàâç'’]","",text)
    text = text.lower()
    text = re.split(r"['’\s]",text)
    while "" in text:
        text.remove("")
    while "l" in text:
        text.remove("l")
    while "d" in text:
        text.remove("d")
    return (text)

# Takes tokenised list of jobs description and title 
# Returns an embedding for each jobs taking the mean of title and description embeddings
# Returns the means of all those embeddings too if needed
def launch_inference_instance():
    """Run full EC2 provisioning and inference workflow, returning job embeddings."""
    
    # Step 1: Launch instance
    try:
        result = subprocess.run(
            ["bash", "inference_VM/EC2_provisioning.sh"], capture_output=True, text=True, check=True
        )
        public_ip = result.stdout.strip()
        print(f"✅ Public IP: {public_ip}")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
    
    except subprocess.CalledProcessError as e:
        print("❌ EC2 provisioning script failed!")
        print("Return code:", e.returncode)
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        raise  # important: re-raise to fail the workflow

    # Step 2: Wait for the app
    url = f"http://{public_ip}:8080/health"
    while True:
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print("✅ App is ready!")
                break
        except RequestException:
            pass
        time.sleep(30)
        print("Waiting for the app to be ready...")
    return (public_ip)

# Takes in the public_ip of the instance and the list of jobs field in its tokenized form
# Returns a dictionnary of format {"FR":[[index],[job_field_embeddings]],"EN":[[index],[job_field_embeddings]]}
def run_fasttext_inference(public_ip,jobs_tokenized_field: list[list[str]]):

    #  Call the API for each tokenized jobs' field
    api_url = f"http://{public_ip}:8080/embed"
    response = requests.post(api_url, json={"input": jobs_tokenized_field}) 
    print("response returned")

    # the data retrieved from the inference VM is in the form {"FR": [ [index],[[]..[token_embeddings]..[]] ],"EN": [ [index],[[embeddings]] ]}
    data = response.json()
    with open("data/response_tmp.json", "w") as f:
        json.dump(data,f)

    # We create an output in the form {"FR":[[index],[job_field_embeddings]],"EN":[[index],[job_field_embeddings]]}
    output = data.copy()
    for lang in ["FR","EN"]:
        # Taking the mean of the token embeddings for each field
        output[lang][1]=[np.mean(df, axis=0) for df in data[lang][1]]
        
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
    jobs_field_grouped_similarity = jobs_field_grouped_embeddings.copy()
    for lang in ["FR","EN"]:
        ref=ideal_jobs_field_grouped_embedding[lang]
        order=jobs_field_grouped_embeddings[lang][0]
        embeddings=jobs_field_grouped_embeddings[lang][1]
        #jobs_field_grouped_similarity[lang][1]= [similarity(ref,embedding) for embedding in embeddings]
        sim = [similarity(ref,embedding) for embedding in embeddings]

        zipped_similarity+=list(zip(order,sim))

    output = [v for _,v in sorted(zipped_similarity)]

    return(output)

    
    # Now that we have our similarity result for the field in question for french and english
    # We can merge the similarity results and order them using their index list

    FR_zipped = jobs_field_grouped_similarity["FR"][0] + jobs_field_grouped_similarity["FR"][1]
    EN_zipped = jobs_field_grouped_similarity["EN"][0] + jobs_field_grouped_similarity["EN"][1]
    zipped_similarity = list(zip(jobs_field_grouped_similarity["FR"]))+list(zip(jobs_field_grouped_similarity["EN"]))
    #output = [v for _,v in sorted(zipped_similarity)]

    #return(output)
        
        


