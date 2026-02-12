import pandas as pd

d={
    "job_hash": ["hash1", "hash2", "hash3"],
    "title": ["title1", "title2", "title3"],
    "company": [None, "company2", "company3"],
    "description": ["desc1", "desc2", "desc3"],
    "location": [None, "loc2", "loc3"],
    "area_json": ["area1", "area2", "area3"],
    "posted_date": ["2023-01-01", "2023-01-02", "2023-01-03"],
    "retrieved_date": ["2023-01-10", "2023-01-11", "2023-01-12"]}
df = pd.DataFrame(d)

df.company=df.company.fillna("unknown")

print(len(d))