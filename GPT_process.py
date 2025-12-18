
# %%
from openai import OpenAI
import yaml
import os
import pandas as pd
from time import sleep

# Load client with API key (assumes set in environment)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

#%%
# Load user profile once
with open("config/user_profile.yaml", "r") as f:
    USER_PROFILE = yaml.safe_load(f)

PROMPT_TEMPLATE = """
You are a job-matching assistant. Based on the user's profile below, evaluate how well this job matches their expectations.

## User Profile:
Job Titles: {titles}
Ideal Job Description: {description}
Skills: {skills}
Education Level: {education}
Level of experience: {experience}

## Job Posting:
Title: {job_title}
Company: {company}
Description: {description_text}

Rate the match as a score between 0 and 10. Add a short justification of less than 200 characters.
"""
def build_prompt(row, user_profile):
    techs= [t["name"] for t in user_profile["technical_skills"]]
    reverse_education_map={0: 'None',
                        1: 'Bachelor',
                          2: 'Master',
                            3: 'PhD'}

    reverse_experience_map={0: '0-6 months',
                        1: '1-2 years',
                        2: '3-5 years',
                        3: '6-10 years',
                        4: '10+ years'}
    
    return PROMPT_TEMPLATE.format(
        titles=", ".join(user_profile["job_titles"]),
        description=user_profile["ideal_job"],
        skills=", ".join(techs),
        education=reverse_education_map[user_profile["education"]],
        experience=reverse_experience_map[user_profile["experience"]],

        job_title=row.get("title", ""),
        company=row.get("company", ""),
        description_text=row.get("description", "")[:1000]  # limit to 1000 tokens for simplicity
    )

def call_openai(prompt, model="gpt-3.5-turbo"):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI error: {e}")
        return None

def extract_score(response_text):
    try:
        score=int(list(filter(str.isdigit, response_text))[0])
        return(score)
    except:
        pass
    return None


def compute_gpt_match_score(df, user_profile, model="gpt-3.5-turbo", delay=2):
    scores = []
    for _, row in df.iterrows():
        prompt = build_prompt(row,user_profile)
        response = call_openai(prompt, model=model)
        ai_score = extract_score(response) if response else None
        scores.append({
            "job_hash": row["job_hash"],
            "ai_score": ai_score,
            "model_version": model,
            "llm_comment": response,
            "llm_version": "1.0.0",
            "model_implementation": "LLM_scoring"
        })
        sleep(delay)  # Respect rate limits

    scores_df = pd.DataFrame(scores)
    return df.merge(scores_df, on="job_hash")

