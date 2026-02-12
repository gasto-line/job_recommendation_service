"""#%%
import requests
from requests.exceptions import RequestException

def call_api(public_ip, input, input_type: str):
    api_url = f"http://{public_ip}:8080/{input_type}"
    response = requests.post(api_url, json=input)
    print(response.json())
    return (response)


    
#%%
public_ip = "35.181.57.103"

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

input_type="ideal_jobs_embeddings"

response = call_api(public_ip, user_profile, input_type)

# %%
myset = {0, 1}
mydict = {0 : False, "pop" : True}
any(mydict)
# %%
d={'job_hash': '15151cfgb3xcb'}
d["job_hash"]
# %%
payload= {"user_id": "8d931b75-8808-4fb8-bde9-27230c187c24", "implementation": "miniLM"}"""

if __name__ == "__main__":
    import requests
    from requests.exceptions import RequestException

    def call_api(public_ip, input, input_type: str):
        api_url = f"http://{public_ip}:8080/{input_type}"
        response = requests.post(api_url, json=input)
        print(response.json())
        return (response)

    input_type="ai_scoring"
    public_ip = "13.39.84.110"
    input= {"user_id": "8d931b75-8808-4fb8-bde9-27230c187c24", "implementation": "miniLM"}
    call_api(public_ip, input, input_type)