# |%%--%%| <49LIAWWqS3|YckzXtYsAr>

import json
import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm
from utils.utils import get_keras_model
import gensim.downloader
from gensim.models import KeyedVectors

import keras
from keras.api.preprocessing.sequence import pad_sequences
from keras.api.callbacks import EarlyStopping, History, ModelCheckpoint

tqdm.pandas()

# |%%--%%| <YckzXtYsAr|6COvVKbRpI>
r"""°°°
# Run the thing!
°°°"""
# |%%--%%| <6COvVKbRpI|6KaSnXw5HG>

with open("./models/review_modelInfo.json", "r") as f:
    relevant_data = json.load(f)

# |%%--%%| <6KaSnXw5HG|To3qwvntx6>

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


# |%%--%%| <To3qwvntx6|ZwQkIvg91P>

LIMIT = 1_250_000

print("[i] Loading dataset")
data = pd.read_csv("./datasets/reviews_cleaned.csv").iloc[:LIMIT]

X = data["review"]
Y = data["sentiment"]

X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.05)

X_train_seq = [embed(txt) for txt in tqdm(X_train, "Embedding XTRAIN")]
X_test_seq = [embed(txt) for txt in tqdm(X_test, "Embedding XTEST")]

# |%%--%%| <ZwQkIvg91P|PYIXTP49nu>

model_checkpoint_callback = ModelCheckpoint(
    filepath=f"./models/review_model.keras",
    save_weights_only=False,
    monitor="val_loss",
    mode="min",
    save_best_only=True,
)
callbacks = [EarlyStopping(patience=3), model_checkpoint_callback]

# |%%--%%| <PYIXTP49nu|TrbzpXrj0N>

max_text_len = relevant_data["max_text_len"]

keras.backend.clear_session()
model = get_keras_model(
    embedding_model.vectors,
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
try:
    res: History = model.fit(
        x=X_train_seq_padded,
        y=Y_train,
        batch_size=relevant_data["batch_size"],
        epochs=NUM_EPOCHS,
        validation_data=(X_test_seq_padded, Y_test),
        callbacks=callbacks,
    )
except:
    pass

# |%%--%%| <TrbzpXrj0N|94VNjw8J8m>

# Save model to disk
model.save("models/review_sentiment.keras")
model.save("../data_pipeline/models/review_sentiment.keras")
