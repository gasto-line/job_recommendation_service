from GPT_process import call_openai
from datetime import datetime, timezone
from DB_jobs import extract_jobs_hash
from utils import generate_job_hash
import os, requests, json
import pandas as pd
from config import settings

def load_adzuna( number_of_jobs: int, page: int, keywords: dict):

    # Adzuna credentials
    APP_ID = settings.ADZUNA_API_ID
    APP_KEY = settings.ADZUNA_API_KEY

    # Base API URL
    base_url = "https://api.adzuna.com/v1/api/jobs/fr/search"
    base_url += f"/{page}"

    # Get paramters from GPT process
    params = keywords

    # Add authentication parameters
    params["app_id"] = APP_ID
    params["app_key"] = APP_KEY
    params["results_per_page"] = number_of_jobs

    # Perform GET request
    response = requests.get(base_url, params=params)
    #Take the first part of the JSON which contains the job details
    jobs=response.json()['results']
    #Convert the JSON payload into a pandas dataframe
    df = pd.json_normalize(jobs)

    #Simplify names coming from subparts of the dictionary
    df.rename(columns={"company.display_name":"company","location.display_name":"location"},inplace=True)
    # replace missing values for company that isn't critical
    df.company=df.company.fillna("unknown")

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
    df.rename(columns={"redirect_url":"url"}, inplace=True)

    return df

ADZUNA_PROMPT = """
You are a candidate open for a new position in the {} sector(s).
Knowing that:
- you are looking for a position commonly refered to as {}
- you are familiar with technologies like: {}
- you have a relevant {} level of education and {} level of professionnal experience
- you want to keep doors open only for positions that doesn't exceed your level of experience and education

Your task is to generate keywords in french and english to identifing relevent jobs posts.
Produce:
- what_or: 25 Positively correlated **one-word** terms
- what_exclude: 10 Negatively correlated **one-word** terms

Your response must be only valid JSON with three fields described above:
{{"what_or": "keyword1 keyword2 ... keyword25", "what_exclude": "keyword1 keyword2 ... keyword10"}}
"""

reverse_education_map={0: 'None',
                        1: 'Bachelor',
                          2: 'Master',
                            3: 'PhD'}

reverse_experience_map={0: '0-6 months',
                        1: '1-2 years',
                        2: '3-5 years',
                        3: '6-10 years',
                        4: '10+ years'}

def generate_adzuna_keywords(profile):
    techs= [t["name"] for t in profile["technical_skills"]]
    
    prompt = ADZUNA_PROMPT.format(
        ", ".join(profile["sectors"]),
        ", ".join(profile["job_titles"]),
        ", ".join(techs),
        reverse_education_map[profile["education"]],
        reverse_experience_map[profile["experience"]]
    )
    response=call_openai(prompt, model="gpt-4")
    return (json.loads(response))
    
def get_raw_df(profile, number_of_jobs_per_page=50, pages=2):
    keywords=generate_adzuna_keywords(profile)
    raw_dfs=[]
    for page in range(1,pages+1):
        raw_df=load_adzuna(number_of_jobs_per_page, page, keywords)
        raw_dfs.append(raw_df)
    return pd.concat(raw_dfs).reset_index(drop=True)


def filter_new_df(raw_df, user_id):
    # Add a new column job_hash that uniquely identify jobs
    raw_df["posted_date_util"] = pd.to_datetime(raw_df["posted_date"])
    raw_df["job_hash"] = raw_df.apply(lambda row: generate_job_hash(row["title"], row["company"], row["posted_date_util"]), axis=1)
    raw_df = raw_df.drop_duplicates(subset='job_hash')

    # Add a filter on jobs that are already in the reference database
    extract=extract_jobs_hash(user_id)
    exclude_set=set(extract)
    # mask rows whose 'job_hash' is NOT in that set
    filtered_df = raw_df.loc[~raw_df['job_hash'].isin(exclude_set)]
    return filtered_df
