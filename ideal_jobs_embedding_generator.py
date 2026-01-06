# ideal_jobs_embedding_generator.py

#%%
import yaml, json, pandas as pd
from GPT_process import call_openai

IDEAL_JOB_PROMPT = """
You are an HR consultant working for various companies in the {} sector(s).
Those companies have open positions for candidates having the following caracteristics:
- profile title commonly refered to as {}
- Familiar with technologies like: {}
- Have relevant {} level of education and {} level of professionnal experience BUT not more than that

Your task is to create a title and description field for 3 jobs positions that will be posted online.
The job positions of the various companies have little in common.
Thoses titles and descriptions should be written both in french and english.

Your response must be only valid JSON having one key for title and description.
The values stored for these keys will contain the text in french and english for all the job posts.
The format should be like this:
{"title": ["title1_fr", "title1_en" ,... ,"title3_en"], "description":["description1_fr", "description1_en" ,... ,"description3_en"]}
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



















#%%
ideal_jobs = {}
for i in range(1, 6):
    path = f"config/ideal_job_{i}.yaml"
    with open(path, "r") as f:
        ideal_jobs[f"ideal_job_{i}"] = yaml.safe_load(f)

#%%
ideal_jobs_df = pd.DataFrame(ideal_jobs)
ideal_jobs_df = pd.DataFrame.transpose(ideal_jobs_df)

#%%
# Rearrange the dataframe of ideal jobs to get one job row per language
ideal_jobs_df_new=pd.DataFrame()
ideal_jobs_df_new.index=[i+lang for i in ideal_jobs_df.index for lang in ["_fr","_en"]]

ideal_jobs_df_new.loc[list(ideal_jobs_df.index+"_en"),"title"]=ideal_jobs_df["title_en"].values
ideal_jobs_df_new.loc[list(ideal_jobs_df.index+"_fr"),"title"]=ideal_jobs_df["title_fr"].values

ideal_jobs_df_new.loc[list(ideal_jobs_df.index+"_en"),"description"]=ideal_jobs_df["description_en"].values
ideal_jobs_df_new.loc[list(ideal_jobs_df.index+"_fr"),"description"]=ideal_jobs_df["description_fr"].values

ideal_jobs_df_new.loc[list(ideal_jobs_df.index+"_en"),"company"]=ideal_jobs_df["company"].values
ideal_jobs_df_new.loc[list(ideal_jobs_df.index+"_fr"),"company"]=ideal_jobs_df["company"].values

ideal_jobs_df=ideal_jobs_df_new
# %%
from fasttext_process import launch_inference_instance, run_fasttext_inference, tokenization
import numpy as np

ideal_jobs_tok_df = ideal_jobs_df.applymap(tokenization)
public_ip = launch_inference_instance()

#%%
ideal_jobs_embedding_dict = {}
for field in ["description","title"]:
    ideal_jobs_embedding_dict[field]={}
    grouped_embeddings = run_fasttext_inference(public_ip, ideal_jobs_tok_df[field].tolist())
    for lang in ["FR","EN"]:
        ideal_jobs_embedding_dict[field][lang]=np.mean(grouped_embeddings[lang][1],axis=0).tolist()

#%%
with open("data/ideal_jobs_embedding_dict.json", "w") as f:
    json.dump(ideal_jobs_embedding_dict,f)
