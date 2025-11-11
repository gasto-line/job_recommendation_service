# ideal_jobs_embedding_generator.py

#%%
import yaml
import pandas as pd
import json

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
from fasttext_process import run_fasttext_inference, tokenization

ideal_jobs_tok_df = ideal_jobs_df.applymap(tokenization)
mean_embedding, _ = run_fasttext_inference(ideal_jobs_tok_df["description"].tolist(), ideal_jobs_tok_df["title"].tolist())

with open("data/ideal_jobs_embedding.json", "w") as f:
    json.dump(mean_embedding.tolist(),f)