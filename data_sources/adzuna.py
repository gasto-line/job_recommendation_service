#%%
import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime, timezone

load_dotenv()
api_key = os.getenv("API_KEY")

# Your Adzuna credentials
APP_ID = os.getenv("ADZUNA_API_ID")
APP_KEY = os.getenv("ADZUNA_API_KEY")




#%%
def load_adzuna( number_of_jobs: int, page: int):

    # Base API URL
    base_url = "https://api.adzuna.com/v1/api/jobs/fr/search"
    base_url += f"/{page}"

    # Parameters as a dictionary
    params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": number_of_jobs,
    "what": "data",
    "what_or": "cloud devops MLops junior platform engineer ingénieur stage infrastructure",
    "what_exclude": "commercial apprenticeship alternance apprentissage marketing senior architect POM",
    "where": "Paris",
    "distance": 20,
    "max_days_old": 2,
    "sort_by": "relevance"
    }

    # Perform GET request
    response = requests.get(base_url, params=params)
    #Take the first part of the JSON which contains the job details
    jobs=response.json()['results']
    #Convert the JSON payload into a pandas dataframe
    df = pd.json_normalize(jobs)

    #Simplify names coming from subparts of the dictionary
    df.rename(columns={"company.display_name":"company","location.display_name":"location"},inplace=True)
    #to avoid problems with SQL commands later
    df.fillna("unknown",inplace=True)

    #Make title and company fields more resilient
    df.company=df.company.str.upper()
    df.title=df.title.str.lower()
    df.description=df.description.str.lower()

    # Add columns: timestamp, raw JSON payload
    df["retrieved_date"] = datetime.now(timezone.utc).date().isoformat()
    df["raw_payload"] = [json.dumps(job) for job in jobs]
    #Add the area list as a JSON in one column in case needed later
    df["area_json"] = df["location.area"].apply(json.dumps)
    #Convert the date from the response into the isoformat date
    df["posted_date"] = df["created"].apply(lambda x: datetime.fromisoformat(x.replace("Z", "+00:00")).date().isoformat())
    
    # Choose which columns to keep in the DB
    columns = [
        "redirect_url",
        "description",
        "title",
        "posted_date",
        "company",
        "area_json",
        "location",
        "retrieved_date",
        "raw_payload"
    ]
    df = df[columns]
    
    return(df)
