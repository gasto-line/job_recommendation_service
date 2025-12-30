from GPT_process import call_openai
from datetime import datetime, timezone
import os, requests, pandas as pd, json

def load_adzuna( number_of_jobs: int, page: int, keywords: dict):

    # Base API URL
    base_url = "https://api.adzuna.com/v1/api/jobs/fr/search"
    base_url += f"/{page}"

    # Get paramters from GPT process
    params = keywords

    # Add authentication parameters
    params["app_id"] = os.getenv("ADZUNA_API_ID")
    params["app_key"] = os.getenv("ADZUNA_API_KEY")
    params["results_per_page"] = number_of_jobs

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

    return df

# Your Adzuna credentials
APP_ID = os.getenv("ADZUNA_API_ID")
APP_KEY = os.getenv("ADZUNA_API_KEY")

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