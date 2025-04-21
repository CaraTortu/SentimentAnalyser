import json
from typing import Iterable

import gensim.downloader
import keras
import pandas as pd
from gensim.models import KeyedVectors
from keras.api.preprocessing.sequence import pad_sequences
from numpy.typing import NDArray
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_absolute_percentage_error,
    mean_squared_error,
    r2_score,
)
from tqdm import tqdm

# Setup TQDM for pandas
tqdm.pandas()

# Get the amount of emails to read and analyse
maxrows = int(input("Rows to test?: "))

###########
# LOADERS #
###########

print("[i] Loading word embedding model")
embedding_model: KeyedVectors = gensim.downloader.load(
    "glove-wiki-gigaword-100"
)  # pyright: ignore

print("[i] Loading model...")
model: keras.Model = keras.models.load_model(
    "models/emails_sentiment.keras"
)  # pyright: ignore

print("[i] Reading model info")
with open("models/emails_modelInfo.json", "r") as f:
    relevant_data = json.load(f)
    max_text_len: int = relevant_data["max_text_len"]

# Read dataset
print("[i] Reading dataset")
data = pd.read_csv("./datasets/emails_cleaned.csv", nrows=maxrows).dropna(
    subset=["content", "sentiment"]
)

#############
# FUNCTIONS #
#############


def embed(txt: str) -> list[int]:
    """
    Embeds a piece of text into keyed vector indeces
    """
    return [
        embedding_model.key_to_index[word]  # pyright: ignore
        for word in txt.split(" ")
        if word in embedding_model
    ]


NEG = -1
NEU = 0
POS = 1


def n_to_lbl(n: int) -> int:
    """
    Transforms a number into negative, positive or neutral
    """
    if n < 0.5:
        return NEG

    if n == 0:
        return NEU

    return POS


def map_to_label(d: Iterable[int]) -> list[int]:
    return [n_to_lbl(x) for x in d]


###################
# GET PREDICTIONS #
###################

X = data["content"]
Y = data["sentiment"]

X_seq = [embed(txt) for txt in tqdm(X, "Embedding X")]
X_padded = pad_sequences(X_seq, maxlen=max_text_len)

Y_pred: NDArray = model.predict(X_padded, batch_size=1)

# Number to label
Y_LBL = map_to_label(Y)
Y_PRED_LBL = map_to_label(Y_pred)


###############
# GET METRICS #
###############


METRICS = {
    "MSE": mean_squared_error,
    "MAE": mean_absolute_error,
    "MAPE": mean_absolute_percentage_error,
    "R2": r2_score,
}

for metric_name, metric_function in METRICS.items():
    result = metric_function(Y, Y_pred)
    print(f"{metric_name}: {result:.4f}")

accuracy = accuracy_score(Y_LBL, Y_PRED_LBL) * 100
print(f"Accuracy: {accuracy:.2f}%")
