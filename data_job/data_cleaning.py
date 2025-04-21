# %%
import json
import pandas as pd

# Load saved JSON
with open("adzuna_response.json", "r") as f:
    data = json.load(f)

# Extract job list
jobs = data["results"]

# Convert to DataFrame
df = pd.DataFrame([{
    "title": job["title"],
    "company": job.get("company", {}).get("display_name"),
    "location": job["location"]["display_name"],
    "areas": job["location"]["area"],
    "description": job["description"],
    "contract_type": job.get("contract_type"),
    "contract_time": job.get("contract_time"),
    "url": job["redirect_url"]
} for job in jobs])

# %%
# Now you can analyze and transform df without hitting the API again
print(df.head())

# %%
