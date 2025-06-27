# app.py

import streamlit as st
import pandas as pd
from DB_insert import insert_jobs

job_list_path='data/top_jobs.pkl'

# Load the job data from a .pkl file
@st.cache_data(ttl=300)
#It might be better to refresh the cache whenever the .pkl file is updated
def load_jobs():
    try:
        return pd.read_pickle(job_list_path)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

# Main app
def main():
    st.title("Job Scoring Dashboard")
    jobs_df = load_jobs()

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

        # Optional: save to CSV or Pickle
        jobs_df.to_csv("outputs/scored_jobs.csv", index=False)
        jobs_df.to_pickle("outputs/scored_jobs.pkl")

        # Insert the new scored jobs into our permanent SQlite DataBase
        insert_jobs(jobs_df)

if __name__ == "__main__":
    main()

