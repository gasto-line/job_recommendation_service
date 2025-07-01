#%%
import pandas as pd
def read_top_jobs(file_path: str) -> pd.DataFrame:
    """
    Reads the top jobs from a given file path and returns a DataFrame.
    
    Args:
        file_path (str): The path to the file containing job data.
        
    Returns:
        pd.DataFrame: A DataFrame containing the job data.
    """
    try:
        df = pd.read_pickle(file_path)
        return df
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return pd.DataFrame()
    
    #%%
    file_path = "../data/top_jobs.pkl"
    df=read_top_jobs(file_path)
# %%
