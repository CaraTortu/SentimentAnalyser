# |%%--%%| <olPxAz6NAy|iErJbJL6me>

import pandas as pd
from tqdm import tqdm
from utils.utils import clean_text

tqdm.pandas()

# |%%--%%| <iErJbJL6me|4Qfj8DWK5R>

file_path = "./datasets/train.ft.txt.bz2"

# Read the file
print("[i] Reading dataset...")
data = pd.read_csv(file_path, sep="\t", header=None, names=["text"], compression="bz2")

# Extract labels and reviews
print("[i] Extracting labels...")
data["label"] = data["text"].progress_apply(
    lambda x: int(x.split()[0].replace("__label__", ""))
)

print("[i] Extracting review texts...")
data["review"] = data["text"].progress_apply(lambda x: " ".join(x.split()[1:]))

data = data[["review", "label"]]
data = data.dropna()

# |%%--%%| <4Qfj8DWK5R|0m2Ezwwnum>

# Clean review text
print("[i] Cleaning text...")
data["review"] = clean_text(data["review"])  # pyright: ignore

# Assign sentiment from 0 to 1
print("[i] Translating labels...")
data["sentiment"] = data["label"].progress_apply(  # pyright: ignore
    lambda x: 1 if x == 2 else 0
)

data.drop(["label"], axis=1, inplace=True)

# |%%--%%| <0m2Ezwwnum|YckzXtYsAr>

CSV_PATH = "./datasets/reviews_cleaned.csv"

print(f"[i] Clean dataset saved to: {CSV_PATH}")
data.to_csv(CSV_PATH)
