import pandas as pd
from tqdm import tqdm
from utils.utils import clean_text

tqdm.pandas()


def clean_emails(data: pd.DataFrame, output_csv: bool = True) -> pd.DataFrame:
    print("[i] Cleaning content")
    data["content"] = clean_text(data["content"])  # pyright: ignore

    print("[i] Scaling values")
    data["sentiment"] = data["sentiment"].progress_apply(lambda x: (x + 1) / 2)

    if output_csv:
        data.to_csv("datasets/emails_cleaned.csv")

    return data
