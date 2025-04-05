import json
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from utils.utils import get_keras_model
import gensim.downloader
from gensim.models import Word2Vec

import keras
from keras.api.preprocessing.sequence import pad_sequences
from keras.api.callbacks import EarlyStopping, ModelCheckpoint

tqdm.pandas()


def train_email_model(data: pd.DataFrame):
    with open("./models/emails_modelInfo.json", "r") as f:
        relevant_data = json.load(f)

    print(f"[i] Using parameters: {relevant_data}")

    print("[i] Loading embedding model")
    embedding_model: Word2Vec = gensim.downloader.load(
        "glove-wiki-gigaword-100"
    )  # pyright: ignore

    def embed(txt: str):
        return [
            embedding_model.key_to_index[word]  # pyright: ignore
            for word in txt.split(" ")
            if word in embedding_model  # pyright: ignore
        ]

    print("[i] Loading dataset")

    X = data["content"]
    Y = data["sentiment"]

    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.05)

    X_train_seq = [embed(txt) for txt in tqdm(X_train, "Embedding XTRAIN")]
    X_test_seq = [embed(txt) for txt in tqdm(X_test, "Embedding XTEST")]

    model_checkpoint_callback = ModelCheckpoint(
        filepath=f"./models/emails_model.keras",
        save_weights_only=False,
        monitor="val_loss",
        mode="min",
        save_best_only=True,
    )
    callbacks = [EarlyStopping(patience=3), model_checkpoint_callback]

    max_text_len = relevant_data["max_text_len"]

    keras.backend.clear_session()
    model = get_keras_model(
        embedding_model.vectors,  # pyright: ignore
        relevant_data["lstm_units"],
        relevant_data["neurons_dense"],
        relevant_data["dropout_rate"],
        max_text_len,
    )

    model.summary()

    learning_rate: float = relevant_data["learning_rate"]  # pyright: ignore
    optimizer = keras.optimizers.Adam(learning_rate=learning_rate)

    NUM_EPOCHS: int = relevant_data["num_epochs"]  # pyright: ignore

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
    model.fit(
        x=X_train_seq_padded,
        y=Y_train,
        batch_size=relevant_data["batch_size"],
        epochs=NUM_EPOCHS,
        validation_data=(X_test_seq_padded, Y_test),
        callbacks=callbacks,
    )

    # Save model to disk
    model.save("./models/emails_sentiment.keras")
    model.export("../data_pipeline/models/emails")
