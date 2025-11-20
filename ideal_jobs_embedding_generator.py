# ideal_jobs_embedding_generator.py

#%%
import yaml, json, pandas as pd

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
