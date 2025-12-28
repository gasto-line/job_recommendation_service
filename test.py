#%%
#%%
import requests
from requests.exceptions import RequestException

def call_api(public_ip, input, input_type: str):
    api_url = f"http://{public_ip}:8080/{input_type}"
    try:
        response = requests.post(api_url, json={"input": input})
        response.raise_for_status()  # Raise an error for bad status codes
        print("API call successful")
        return response.json()
    except RequestException as e:
        raise RuntimeError(f"API call failed: {e}")
    
user_profile= {'user_id': '8d931b75-8808-4fb8-bde9-27230c187c24',
 'job_titles': ['Cloud engineer', 'Data engineer', 'ML engineer'],
 'ideal_job': 'Build infrastructure for data science and AI services',
 'technical_skills': [{'name': 'Python', 'Weight (%)': 50},
  {'name': 'Cloud', 'Weight (%)': 30},
  {'name': 'SQL', 'Weight (%)': 20}],
 'general_skills': [{'Category': 'Cognitive & Technical', 'Weight (%)': 40},
  {'Category': 'Execution & Operational', 'Weight (%)': 20},
  {'Category': 'Social & Communication', 'Weight (%)': 20},
  {'Category': 'Business & Contextual', 'Weight (%)': 20}],
 'experience': 1,
 'education': 2,
 'sectors': ['ICT & Digital']}

#%%
curl -X GET "http://35.180.97.144:8080/health"
#%%
from ETL_job.fasttext_process import call_api
call_api(public_ip, user_profile, "sentence")
# %%
curl -X POST "http://35.180.97.144:8080/ideal_jobs_embeddings" \
     -H "Content-Type: application/json" \
     -d '{"user_id":"8d931b75-8808-4fb8-bde9-27230c187c24","job_titles":["Cloud engineer", "Data engineer", "ML engineer"],"ideal_job":"Build infrastructure for data science and AI services","technical_skills":[{"name":"Python", "Weight (%)":50},{"name":"Cloud", "Weight (%)":30},{"name":"SQL", "Weight (%)":20}],"general_skills":[{"Category":"Cognitive & Technical", "Weight (%)":40},{"Category":"Execution & Operational", "Weight (%)":20},{"Category":"Social & Communication", "Weight (%)":20},{"Category":"Business & Contextual", "Weight (%)":20}],"experience":1,"education":2,"sectors":["ICT & Digital"]}'

#%%
from ETL_job.DB_jobs import profile_extraction
profile=profile_extraction("8d931b75-8808-4fb8-bde9-27230c187c24")
# %%
ideal=profile["fasttext_ref_embed"]
for field,value in ideal.items():
    for lang,embed in value.items():
        print(len(embed))


#Notes

"""    if st.button("Save profile"):
        if tech_total != 100 or skill_total != 100:
            st.error("Please correct the skill weights — totals must be 100%.")

        elif not job_titles or not ideal_job or not sectors or not education.code or not experience.code:
            st.error("Please fill in all required fields.")
        
        else:
            try:
                user_profile={
                    "user_id": st.session_state["user"].id,
                    "job_titles": job_titles,
                    "ideal_job": ideal_job,
                    "technical_skills": tech_df.to_dict("records"),
                    "general_skills": skill_df.to_dict("records"),
                    "education": education_code,
                    "sectors": sectors,
                    "experience": experience_code
                    }
                response=supabase.table("user_profile").upsert(user_profile).execute()
                st.success("Profile saved successfully!")

                call_api(public_ip="35.180.97.226", input=user_profile, input_type="ideal_jobs_embeddings")
                
            except Exception as e:
                st.error(f"Error saving profile: {e}")
"""