import pandas as pd
from tqdm import tqdm
from utils.utils import clean_text

tqdm.pandas()

CSV_PATH = "./datasets/reviews_cleaned.csv"


def clean_reviews(df: pd.DataFrame, output: bool = True) -> pd.DataFrame:
    # Extract labels and reviews
    print("[i] Extracting labels...")
    df["label"] = df["text"].progress_apply(
        lambda x: int(x.split()[0].replace("__label__", ""))
    )

    print("[i] Extracting review texts...")
    df["review"] = df["text"].progress_apply(lambda x: " ".join(x.split()[1:]))

    data: pd.DataFrame = df[["review", "label"]].dropna()  # pyright: ignore

    # Clean review text
    print("[i] Cleaning text...")
    data["review"] = clean_text(data["review"])  # pyright: ignore

    # Assign sentiment from 0 to 1
    print("[i] Translating labels...")
    data["sentiment"] = data["label"].progress_apply(  # pyright: ignore
        lambda x: 1 if x == 2 else 0
    )

    data.drop(["label"], axis=1, inplace=True)

    if output:
        print(f"[i] Clean dataset saved to: {CSV_PATH}")
        data.to_csv(CSV_PATH)

    return data
