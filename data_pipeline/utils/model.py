import gensim.downloader
from gensim.models import Word2Vec
import keras
from keras.api.preprocessing.sequence import pad_sequences
import pandas as pd
from tqdm import tqdm
import json

print("[i] Loading word2vec...")
embedding_model: Word2Vec = gensim.downloader.load(
    "glove-wiki-gigaword-100"
)  # pyright: ignore

# Load model data
with open("models/modelInfo.json", "r") as f:
    relevant_data = json.load(f)

max_text_len = relevant_data["max_text_len"]


def embed(txt: str) -> list[int]:
    return [
        embedding_model.key_to_index[word]  # pyright: ignore
        for word in txt.split(" ")
        if word in embedding_model  # pyright: ignore
    ]


def get_model(name: str) -> keras.Model:
    return keras.models.load_model(f"models/{name}_sentiment.keras")  # pyright: ignore


def predict_texts(model: keras.Model, text: pd.Series) -> list[float]:
    embbeded = [embed(txt) for txt in tqdm(text, "[i] Embedding data")]
    padded = pad_sequences(embbeded, maxlen=max_text_len)
    return model.predict(padded, batch_size=1)
