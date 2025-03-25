# |%%--%%| <49LIAWWqS3|YckzXtYsAr>

import json
from ax.core.types import TEvaluationOutcome
from gensim.models import Word2Vec
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm
import gensim.downloader

import keras
from keras.api.preprocessing.sequence import pad_sequences
from keras.api.callbacks import History

from utils.utils import get_keras_model

tqdm.pandas()

# |%%--%%| <YckzXtYsAr|gZQmk1cxxq>

DATA_SIZE = 500_000

print("[i] Loading clean dataset...")
data = pd.read_csv("./datasets/reviews_cleaned.csv").iloc[:DATA_SIZE]

X = data["review"]
Y = data["sentiment"]

print("[i] Splitting test and train")
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.05)

# |%%--%%| <gZQmk1cxxq|lMOOx3afg7>

print("[i] Loading embedding model")
embedding_model: Word2Vec = gensim.downloader.load(
    "glove-wiki-gigaword-100"
)  # pyright: ignore

# |%%--%%| <lMOOx3afg7|YnpMEoE5hX>


def embed(txt: str):
    return [
        embedding_model.key_to_index[word]  # pyright: ignore
        for word in txt.split(" ")
        if word in embedding_model  # pyright: ignore
    ]


print("[i] Embedding text")
X_train_seq = [embed(txt) for txt in tqdm(X_train, "Embedding XTRAIN")]
X_test_seq = [embed(txt) for txt in tqdm(X_test, "Embedding XTEST")]

# |%%--%%| <YnpMEoE5hX|4MK6ZtQ73y>


# This function takes in the hyperparameters and returns a score (Cross validation).
def keras_cv_score(parameterization, max_text_len=800):

    max_text_len = parameterization.get("max_text_len")

    keras.backend.clear_session()
    model = get_keras_model(
        embedding_model.vectors,  # pyright: ignore
        parameterization.get("lstm_units"),
        parameterization.get("neurons_dense"),
        parameterization.get("dropout_rate"),
        max_text_len,
    )

    learning_rate = parameterization.get("learning_rate")
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)

    NUM_EPOCHS = parameterization.get("num_epochs")

    # Specify the training configuration.
    model.compile(
        optimizer=optimizer,  # pyright: ignore
        loss=keras.losses.BinaryCrossentropy(),
        metrics=["accuracy"],
    )

    # pad the sequences so they're the same length.
    X_train_seq_padded = pad_sequences(X_train_seq, maxlen=max_text_len)
    X_test_seq_padded = pad_sequences(X_test_seq, maxlen=max_text_len)

    # fit the model using a 20% validation set.
    res: History = model.fit(
        x=X_train_seq_padded,
        y=Y_train,
        batch_size=parameterization.get("batch_size"),
        epochs=NUM_EPOCHS,
        validation_data=(X_test_seq_padded, Y_test),
    )
    last_score = np.array(res.history["val_loss"][-1:])
    return last_score, 0


# |%%--%%| <4MK6ZtQ73y|HzyY4oGRY8>
r"""°°°
Optimise
°°°"""
# |%%--%%| <HzyY4oGRY8|Mn18wT1Exf>

# Define the search space.
parameters = [
    {
        "name": "learning_rate",
        "type": "range",
        "bounds": [0.0001, 0.05],
        "log_scale": True,
    },
    {
        "name": "dropout_rate",
        "type": "range",
        "bounds": [0.01, 0.5],
        "log_scale": True,
    },
    {"name": "lstm_units", "type": "range", "bounds": [16, 64], "value_type": "int"},
    {
        "name": "neurons_dense",
        "type": "range",
        "bounds": [128, 1024],
        "value_type": "int",
    },
    {"name": "num_epochs", "type": "range", "bounds": [1, 10], "value_type": "int"},
    {"name": "batch_size", "type": "range", "bounds": [32, 128], "value_type": "int"},
]

MAX_TEXT_LENGTH = 800

# |%%--%%| <Mn18wT1Exf|uSkQBk3s41>

# import more packages
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.utils.notebook.plotting import init_notebook_plotting

init_notebook_plotting()

ax_client = AxClient()

# create the experiment.
ax_client.create_experiment(
    name="keras_experiment",
    parameters=parameters,
    objectives={"keras_cv": ObjectiveProperties(minimize=True)},
)


def evaluate(parameters) -> TEvaluationOutcome:
    return {
        "keras_cv": keras_cv_score(parameters, max_text_len=MAX_TEXT_LENGTH)
    }  # pyright: ignore


# |%%--%%| <uSkQBk3s41|T7ekaRL8Pk>

print("[i] Press CTRL+C to exit loop")
try:
    while True:
        parameters, trial_index = ax_client.get_next_trial()
        ax_client.complete_trial(trial_index=trial_index, raw_data=evaluate(parameters))
except:
    pass

# look at all the trials.
ax_client.get_trials_data_frame().sort_values("trial_index")

# |%%--%%| <T7ekaRL8Pk|j227tdJYHX>

print("[i] Extracting best parameters")
best_parameters, values = ax_client.get_best_parameters()  # pyright: ignore

# the best set of parameters.
for k in best_parameters.items():
    print(k)

print()

# the best score achieved.
means, covariances = values  # pyright: ignore
print(means)

# |%%--%%| <j227tdJYHX|47eX2Qr7JA>


# Save JSON with important parameters
relevant_data = {
    "max_text_len": MAX_TEXT_LENGTH,
    "gensin_model": "glove-wiki-gigaword-100",
}

for k, v in best_parameters.items():
    relevant_data[k] = v  # pyright: ignore

with open("./models/review_modelInfo.json", "w") as f:
    json.dump(relevant_data, f)
