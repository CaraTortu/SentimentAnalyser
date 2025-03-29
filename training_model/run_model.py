# |%%--%%| <Zhy9EyA8zR|WmQmCOfCmu>
import json
import pandas as pd
from utils.utils import clean_text
import gensim.downloader
from tqdm import tqdm
from gensim.models import Word2Vec

tqdm.pandas()

import keras
from keras.api.preprocessing.sequence import pad_sequences

# |%%--%%| <WmQmCOfCmu|jceRGKedoG>

# Get model to run
model_name = input("Model name [emails, review]: ")

if model_name not in ["emails", "review"]:
    print("[-] Invalid model name")
    exit(1)

# |%%--%%| <jceRGKedoG|SYdAEdKUAG>

print("[i] Loading word embedding model")
embedding_model: Word2Vec = gensim.downloader.load(
    "glove-wiki-gigaword-100"
)  # pyright: ignore


def embed(txt: str):
    return [
        embedding_model.key_to_index[word]  # pyright: ignore
        for word in txt.split(" ")
        if word in embedding_model  # pyright: ignore
    ]


# |%%--%%| <SYdAEdKUAG|D0IGQ3Kf4k>

# Loading model
print("[i] Loading model...")
model: keras.Model = keras.models.load_model(
    f"models/{model_name}_sentiment.keras"
)  # pyright: ignore

# |%%--%%| <D0IGQ3Kf4k|OKbMXO3DwA>

with open(f"models/{model_name}_modelInfo.json", "r") as f:
    relevant_data = json.load(f)

max_text_len = relevant_data["max_text_len"]

# |%%--%%| <OKbMXO3DwA|SAn913Gkwh>

in_text = ""
while in_text != "exit":
    in_text = input("INPUT: ")
    text = pd.Series([in_text])

    embbeded = [embed(txt) for txt in clean_text(text)]
    padded = pad_sequences(embbeded, maxlen=max_text_len)
    print(padded[0])
    print(f"SCORE: {model.predict(padded)}")
