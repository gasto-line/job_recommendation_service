# %%
import pandas as pd

df=pd.read_pickle('scored_jobs.pkl')
df.rename(columns={'match_pct':'AI_score'},inplace=True)
df.AI_score=(df.AI_score//10).astype(int)
# %%
df.to_pickle("scored_jobs.pkl")