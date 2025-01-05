import pandas as pd
import os
from openai import OpenAI

def generate_embedding(text):
    """
    Generate text embedding using OpenAI API.
    Return the vector only
    """
    response = client.embeddings.create(input=text, model="text-embedding-ada-002",
                                        encoding_format = "float")
    return response.data[0].embedding


# call OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
# read data 
data = pd.read_csv("profiles/profiles.csv")
data['Embedding'] = data['About'].fillna("").apply(generate_embedding)
# save data to json file
data.to_json("output.json", orient="records", lines= False)
print("successfully output profiles with about in vector form")