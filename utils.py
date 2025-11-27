import pandas as pd

# Function that generates a unique identifier for the jobs
def generate_job_hash(title, company, pub_date):
    year = pub_date.year
    month = pub_date.month
    identifier = f"{title.strip().lower()}_{company.strip().lower()}_{year}_{month}"
    return pd.util.hash_pandas_object(pd.Series(identifier)).astype(str)[0]