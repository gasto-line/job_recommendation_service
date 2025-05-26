# %%
import sqlite3
import os
import pandas as pd

db_path = os.path.expanduser('~/job_recommendation_service/data/jobs_ref.db')

# Connect and automatically close after the block
with sqlite3.connect(db_path) as conn:
    df = pd.read_sql_query("SELECT * FROM jobs", conn)

# Show the DataFrame
print(df)
# %%
