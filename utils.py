import pandas as pd
import re

# Function that generates a unique identifier for the jobs
def generate_job_hash(title, company, pub_date):
    year = pub_date.year
    month = pub_date.month
    identifier = f"{title.strip().lower()}_{company.strip().lower()}_{year}_{month}"
    return pd.util.hash_pandas_object(pd.Series(identifier)).astype(str)[0]


def tokenization(text):
    text = re.sub(r"[^a-zA-Z0-9\s#&œ+éèêàâç'’]","",text)
    text = text.lower()
    text = re.split(r"['’\s]",text)
    while "" in text:
        text.remove("")
    while "l" in text:
        text.remove("l")
    while "d" in text:
        text.remove("d")
    return (text)