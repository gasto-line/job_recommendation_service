# app.py

import streamlit as st
import pandas as pd
from DB_jobs import get_engine, insert_jobs
import io, os
import requests

IMPLEMENTATIONS = {
    "LLM": {
        "url": 'https://github.com/gasto-line/job_recommendation_service/releases/download/top-jobs-latest/top_jobs.pkl',
        "label": "GPT3.5-based recommendation"
    },
    "fasttext": {
        "url": 'https://github.com/gasto-line/job_recommendation_service/releases/download/fasttext_toplist/fasttext_toplist.pkl',
        "label": "FastText-based recommendation"
    }
}

DB_PSW=st.secrets["DB_PSW"]

# Load the job data from a .pkl file
@st.cache_data(ttl=300)
#It might be better to refresh the cache whenever the .pkl file is updated
def load_jobs(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP errors
        # Convert the binary file extracted from HTTP request into a file-like object
        job_list_file = io.BytesIO(response.content)
        # Load the DataFrame from the bytes object
        st.info("Job data loaded successfully from GitHub.")
        return pd.read_pickle(job_list_file)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

def get_file_last_commit_date(owner, repo, file_path):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?path={file_path}&page=1&per_page=1"
    try:
        r = requests.get(url)
        r.raise_for_status()
        commit = r.json()[0]
        return commit["commit"]["author"]["date"]
    except:
        return ("?")

# Main app
def main():
    st.sidebar.title("Configuration")
    implementation = st.sidebar.selectbox(
                        "Select recommendation engine:",
                        options=list(IMPLEMENTATIONS.keys()),
                        format_func=lambda x: IMPLEMENTATIONS[x]["label"]
                        )
    selected_url = IMPLEMENTATIONS[implementation]["url"]
    jobs_df = load_jobs(selected_url)

    lastest_update= get_file_last_commit_date("gasto-line", "job_recommendation_service", os.path.basename(selected_url))
    st.title(f"{IMPLEMENTATIONS[implementation]["label"]} job scoring Dashboard")
    st.info(f"Lastest list update: {lastest_update}")

    if jobs_df.empty:
        st.warning("No job data found.")
        return

    st.subheader("Rate the Jobs")
    scores = {}
    justifications = {}
    applications = {}

    for idx, row in jobs_df.iterrows():
        job_title = row.get("title", "Unknown Title")
        company = row.get("company", "Unknown Company")
        job_url = row.get("redirect_url", "#")

        with st.expander(f"{job_title} at {company}"):
            st.write(f"[{job_url}]({job_url})")
            st.write(f"**Location**: {row.get('location', 'N/A')}")
            st.write(f"**Description**: {row.get('description', 'No description available.')[:500]}...")

            # Enable rating this job
            wants_to_rate = st.checkbox("Rate this job?", key=f"rate_{idx}")

            if wants_to_rate:

                # Score input
                score = st.slider(f"Score this job", 1, 10, 5, key=f"score_{idx}")
                scores[idx] = score

                # Justification input
                justification = st.text_area("Optional justification", key=f"justif_{idx}")
                justifications[idx] = justification

                # Application checkbox
                applied = st.checkbox("Tick if you applied", key=f"applied_{idx}")
                applications[idx] = applied

    if st.button("Submit Scores"):
        jobs_df["user_score"] = jobs_df.index.map(scores.get)
        jobs_df["user_justification"] = jobs_df.index.map(justifications.get)
        jobs_df["applied"] = jobs_df.index.map(applications.get)

        st.success("Scores submitted!")
        st.dataframe(jobs_df[["title", "company", "user_score", "applied"]])

        # Insert the new scored jobs into our permanent SQlite DataBase
        if DB_PSW:
            engine = get_engine(DB_PSW)
        else:
            raise ValueError("Database password (DB_PSW) is not set streamlit secrets")
            
        reponse = insert_jobs(jobs_df,engine)
        if reponse[0]:
            st.success("Jobs inserted successfully!")
        else:
            st.error("Failed to insert jobs!"+str(reponse[1]))

if __name__ == "__main__":
    main()

