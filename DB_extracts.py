#%%
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy import Date, Boolean
from sqlalchemy.dialects.postgresql import JSON
import os

# ❶ Import the database password from Streamlit secrets
DB_PSW = os.getenv("DB_PSW")
if not DB_PSW:
    raise ValueError("Database password (DB_PSW) is not set in environment variables.")
SUPABASE_DB_URL = (
    "postgresql://postgres.irutkdcynqycaveefmpe:"+ DB_PSW +"@aws-0-eu-west-3.pooler.supabase.com:5432/postgres"
)

# ❷ Create the engine once (Streamlit may cache this if needed)
engine = create_engine(SUPABASE_DB_URL, pool_pre_ping=True)

def extract_jobs_hash():
    """
    Extracts job hashes from the database.
    
    Returns:
        pd.DataFrame: A DataFrame containing job hashes.
    """
    try:
        with engine.connect() as conn:
            query = text("SELECT job_hash FROM jobs")
            result = pd.read_sql(query, conn)
            return result
    except Exception as e:
        print(f"Error extracting job hashes: {e}")
        return pd.DataFrame(columns=["job_hash"])
#%%
df= extract_jobs_hash()
# %%
