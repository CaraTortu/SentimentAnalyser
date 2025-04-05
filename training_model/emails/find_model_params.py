import json
import time
from ax.core.types import TEvaluationOutcome
from gensim.models import KeyedVectors
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from ax.service.ax_client import AxClient, ObjectiveProperties
from tqdm import tqdm
import gensim.downloader

import keras
from keras.api.preprocessing.sequence import pad_sequences
from keras.api.callbacks import History

from utils.utils import get_keras_model

tqdm.pandas()

MAX_TEXT_LENGTH = 800


def find_email_params(data: pd.DataFrame, output: bool = True):
    X = data["content"]
    Y = data["sentiment"]

    print("[i] Splitting test and train")
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.05)

    print("[i] Loading embedding model")
    embedding_model: KeyedVectors = gensim.downloader.load(
        "glove-wiki-gigaword-100"
    )  # pyright: ignore

    def embed(txt: str):
        return [
            embedding_model.key_to_index[word]  # pyright: ignore
            for word in txt.split(" ")
            if word in embedding_model
        ]

    print("[i] Embedding text")
    X_train_seq = [embed(txt) for txt in tqdm(X_train, "Embedding XTRAIN")]
    X_test_seq = [embed(txt) for txt in tqdm(X_test, "Embedding XTEST")]

    # This function takes in the hyperparameters and returns a score (Cross validation).
    def keras_cv_score(parameterization, max_text_len=800):

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
            loss="mse",
            metrics=["mae"],
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
        last_score = np.array(res.history["val_mae"][-1:])
        return last_score, 0

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
        {"name": "lstm_units", "type": "range", "bounds": [8, 64], "value_type": "int"},
        {
            "name": "neurons_dense",
            "type": "range",
            "bounds": [32, 1024],
            "value_type": "int",
        },
        {"name": "num_epochs", "type": "range", "bounds": [1, 10], "value_type": "int"},
        {
            "name": "batch_size",
            "type": "range",
            "bounds": [32, 128],
            "value_type": "int",
        },
    ]

    ax_client = AxClient()

    # create the experiment.
    ax_client.create_experiment(
        name="keras_experiment",
        parameters=parameters,
        objectives={
            "keras_cv": ObjectiveProperties(minimize=True),
            "runtime": ObjectiveProperties(minimize=True),
        },
    )

    def evaluate(parameters):
        now = time.time()
        result: TEvaluationOutcome = {
            "keras_cv": keras_cv_score(parameters, max_text_len=MAX_TEXT_LENGTH),
        }  # pyright: ignore

        result["runtime"] = (time.time() - now, 0)  # pyright: ignore

        return result

    try:
        print("[i] RUNNING TESTS: If you want to stop. Run Ctrl-C")
        while True:
            parameters, trial_index = ax_client.get_next_trial()
            ax_client.complete_trial(
                trial_index=trial_index, raw_data=evaluate(parameters)
            )
    except:
        pass

    # look at all the trials.
    print(ax_client.get_trials_data_frame().sort_values("trial_index"))

    print("[i] Extracting best parameters")

    pareto_optimal_trials = ax_client.get_pareto_optimal_parameters()

    # Assign weights to objectives (higher weight for more important objective)
    WEIGHT_RESULT = 0.8
    WEIGHT_TIME = 0.2

    # Compute a score for each trial
    def compute_score(trial):
        trial = trial[1][1][0]
        result_score = trial["keras_cv"]
        time_score = trial["runtime"]
        return WEIGHT_RESULT * result_score + WEIGHT_TIME * time_score

    # Find the best trial based on weighted score (minimization)
    best_trial = min(pareto_optimal_trials.items(), key=compute_score)[1]
    best_parameters, best_values = best_trial[0], best_trial[1][0]

    print("\nBest Parameters (Weighted Trade-Off - Both Minimized):", best_parameters)
    print("Objective Values:", best_values)

    if output:
        # Save JSON with important parameters
        relevant_data = {
            "max_text_len": MAX_TEXT_LENGTH,
            "gensin_model": "glove-wiki-gigaword-100",
        }

        for k, v in best_parameters.items():
            relevant_data[k] = v  # pyright: ignore

        with open("./models/emails_modelInfo.json", "w") as f:
            json.dump(relevant_data, f)
