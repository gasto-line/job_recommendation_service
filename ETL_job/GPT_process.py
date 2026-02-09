
# %%
from config import settings
from openai import OpenAI
import os, json
import pandas as pd
from time import sleep

# Load client with API key (configured through pydantic settings)
client = OpenAI(api_key=settings.OPENAI_API_KEY)
#%%
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

## OUTPUT: 
Type: dictionnary with keys "score" and "justification"
score: An integer from 0 to 10 indicating the match quality (10 = perfect match, 0 = no match)
justification: A brief explanation for the score.
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


