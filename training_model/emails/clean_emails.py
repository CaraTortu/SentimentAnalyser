# |%%--%%| <Tz0ulJd8po|kjeOvYt42x>
import pandas as pd
from tqdm import tqdm

from utils.utils import clean_text

tqdm.pandas()

# |%%--%%| <kjeOvYt42x|cnBKfIjgwL>

print("[i] Reading dataset")
data = pd.read_csv("./datasets/emails_labelled.csv")

# |%%--%%| <cnBKfIjgwL|V7jo2OUTSh>

print("[i] Cleaning content")
data["content"] = clean_text(data["content"])  # pyright: ignore


print("[i] Scaling values")
data["sentiment"] = data["sentiment"].progress_apply(lambda x: (x + 1) / 2)

# |%%--%%| <V7jo2OUTSh|9mQfSZtv7a>

data.to_csv("./datasets/emails_cleaned.csv")
