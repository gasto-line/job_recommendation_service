from GPT_process import call_openai
import json

IDEAL_JOB_PROMPT = """
You are an HR consultant working for various companies in the {} sector(s).
Those companies have open positions for candidates having the following caracteristics:
- profile title commonly refered to as {}
- Familiar with technologies like: {}
- Have relevant {} level of education and {} level of professionnal experience BUT not more than that

Your task is to create a title and description of about 500 caracters for 3 jobs positions that will be posted online.
ATTENTION: The description of the job should neither explicitely mention the caracteristics sought after nor use generic formulation. Instead you should give specific details about the role.
Thoses titles and descriptions should be written both in french and english.

Your response must be only valid JSON having one key for title and description.
The values stored for these keys will contain the text in french and english for all the job posts.
The format should be like this:
{{"title": ["title1_fr", "title1_en" ,... ,"title3_en"], "description":["description1_fr", "description1_en" ,... ,"description3_en"]}}
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

def generate_ideal_jobs(profile):
    techs= [t["name"] for t in profile["technical_skills"]]
    
    prompt = IDEAL_JOB_PROMPT.format(
        " or ".join(profile["sectors"]),
        ", ".join(profile["job_titles"]),
        ", ".join(techs),
        reverse_education_map[profile["education"]],
        reverse_experience_map[profile["experience"]]
    )
    response=call_openai(prompt, model="gpt-4")
    return (json.loads(response))