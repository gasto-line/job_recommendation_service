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
