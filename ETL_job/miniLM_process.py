# %%
from light_embed import TextEmbedding
import pandas as pd
import numpy as np
from numpy import dot
from numpy.linalg import norm

model = TextEmbedding('sentence-transformers/all-MiniLM-L6-v2')

def similarity(vec1,vec2):
        return(dot(vec1, vec2) / (norm(vec1) * norm(vec2))) 

def gen_mean_embedding(df,fields):
    # Create a list of inputs for the model by concatenating specified fields
    embeddings = gen_embeddings(df,fields)
    # Take the mean of the embeddings to get an ideal embedding
    ideal_embedding = np.mean(embeddings, axis=0).tolist()
    return ideal_embedding

def gen_embeddings(df,fields):
    concat = df[fields].apply(lambda row: ", ".join([f"{col}: {row[col]}" for col in row.index]),axis=1)
    embeddings = model.encode(concat.tolist())
    return embeddings

def score_embeddings(embeddings,ref_embedding):
    scores = [similarity(ref_embedding,embedding) for embedding in embeddings]
    return scores

if __name__ == "__main__":
    print("Testing gen_mean_embedding...")
    df = pd.DataFrame.from_dict({"title": ["a", "b" ,"c"], "description":["yo", "yoyo" ,"yoyoyo"]})
    res = gen_mean_embedding(df,["title","description"])
    print (res)