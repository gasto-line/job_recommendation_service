import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("API_KEY")

# Your Adzuna credentials
APP_ID = os.getenv("ADZUNA_API_ID")
APP_KEY = os.getenv("ADZUNA_API_KEY")

# Base API URL
base_url = "https://api.adzuna.com/v1/api/jobs/fr/search/1"

# Parameters as a dictionary
params = {
    "app_id": APP_ID,
    "app_key": APP_KEY,
    "results_per_page": 50,
    "what": "data",
    "what_or": "cloud devops MLops junior platform engineer ingénieur reconversion infrastructure",
    "what_exclude": "commercial internship apprenticeship stage alternance apprentissage marketing senior architect POM",
    "where": "Paris",
    "distance": 20,
    "max_days_old": 2,
    "sort_by": "relevance"
}

# Perform GET request
response = requests.get(base_url, params=params)

# Save response locally
with open("data/adzuna_response.json", "w") as f:
    json.dump(response.json(), f, indent=2)
