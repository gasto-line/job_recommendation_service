
#%%
import requests, json

def debug_release(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    r = requests.get(url)
    #print("\n".join(r.json().keys()))
    print(json.dumps(r.json(),indent=4))
    '''for e in r.json():
        print(e)'''
    

debug_release("gasto-line","job_recommendation_service")
# %%
def get_release_asset_update_date(owner, repo, asset_name):
    url = f"https://api.github.com/repos/{owner}/{repo}/releases"
    try:
        r = requests.get(url)
        r.raise_for_status()
        releases = r.json()
        for release in releases:
            asset = release.get["assets"]
            if asset.get("name") == asset_name:
                return asset.get("updated_at")
        return ("(release not found)")
    except Exception:
        return ("(Error)")

get_release_asset_update_date("gasto-line","job_recommendation_service","top_jobs.pkl")
# %%
for asset in release.get("assets", []):
    print(asset)
# %%
