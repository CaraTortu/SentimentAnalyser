# |%%--%%| <7pOtjexOMm|csy4L9KM4s>
import json
from typing import List
from numpy.typing import NDArray
import pandas as pd
import gensim.downloader
from tqdm import tqdm
from gensim.models import KeyedVectors

tqdm.pandas()

import keras
from keras.api.preprocessing.sequence import pad_sequences
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)

# Get model to run
print("[i] Loading word embedding model")
embedding_model: KeyedVectors = gensim.downloader.load(
    "glove-wiki-gigaword-100"
)  # pyright: ignore


def embed(txt: str):
    return [
        embedding_model.key_to_index[word]  # pyright: ignore
        for word in txt.split(" ")
        if word in embedding_model
    ]


# Loading model
print("[i] Loading model...")
model: keras.Model = keras.models.load_model(
    f"models/emails_sentiment.keras"
)  # pyright: ignore

with open(f"models/emails_modelInfo.json", "r") as f:
    relevant_data = json.load(f)
    max_text_len = relevant_data["max_text_len"]

# Read dataset
data = pd.read_csv("./datasets/emails_cleaned.csv", nrows=10000).dropna(
    subset=["content", "sentiment"]
)

X = data["content"]
Y = data["sentiment"]

X_seq = [embed(txt) for txt in tqdm(X, "Embedding X")]
X_padded = pad_sequences(X_seq, maxlen=max_text_len)

Y_pred: NDArray = model.predict(X_padded, batch_size=1)

# |%%--%%| <csy4L9KM4s|7J8vQU96kU>

METRICS = {
    "MSE": mean_squared_error,
    "MAE": mean_absolute_error,
    "MAPE": mean_absolute_percentage_error,
    "R2": r2_score,
}

for k, v in METRICS.items():
    result = v(Y, Y_pred)
    print(f"{k}: ", result)

# |%%--%%| <7J8vQU96kU|8Lv1zurvON>

NEG = -1
NEU = 0
POS = 1


def n_to_lbl(n: int) -> int:
    if n < 0.5:
        return NEG

    if n == 0:
        return NEU

    return POS


def map_to_label(d: List[int]) -> List[int]:
    return [n_to_lbl(x) for x in d]


Y_LBL = map_to_label(Y)  # pyright: ignore
Y_PRED_LBL = map_to_label(Y_pred)  # pyright: ignore

print("Accuracy: ", accuracy_score(Y_LBL, Y_PRED_LBL))
