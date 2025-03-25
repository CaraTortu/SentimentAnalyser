# |%%--%%| <N30kLAzScK|eEqREJZHNN>
r"""°°°
# EDA of training dataset
°°°"""
# |%%--%%| <eEqREJZHNN|DBPL0bOeg2>

from collections import Counter
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm

from utils.utils import clean_text

tqdm.pandas()

# |%%--%%| <DBPL0bOeg2|IhG7VLyHGh>

file_path = "./datasets/train.ft.txt.bz2"

# Read the file
data = pd.read_csv(file_path, sep="\t", header=None, names=["text"], compression="bz2")

# Extract labels
labels: pd.Series = (
    data["text"]
    .progress_apply(lambda x: int(x.split()[0].replace("__label__", "")))
    .progress_apply(lambda x: "Positive" if x == 2 else "Negative")
    .dropna()
)

# Extract reviews
reviews: pd.Series = (
    data["text"].progress_apply(lambda x: " ".join(x.split()[1:])).dropna()
)

# Clean up memory
# del data
# del labels
# del reviews

# |%%--%%| <IhG7VLyHGh|NG8KGMghSq>
r"""°°°
## See label distribution

As we can see the distribution between positive and negative labels is equal, each being 1800000
°°°"""
# |%%--%%| <NG8KGMghSq|eQnplEyPvU>

print(labels.value_counts())

plt.hist(labels)
plt.show()

# |%%--%%| <eQnplEyPvU|pWY7GtrbVy>
r"""°°°
## Text information

We can see that on average, text length goes down from 78.5 words to 62.5
We can also go that the new maximum length text is 174 instead of 257
°°°"""
# |%%--%%| <pWY7GtrbVy|rrMbPwZno1>

review_length = reviews.progress_map(lambda x: len(x.split(" ")))

# Get text statistics
print(f"Average review length: {review_length.mean()}")
print(f"Min review length: {review_length.min()}")
print(f"Max review length: {review_length.max()}")

# |%%--%%| <rrMbPwZno1|oeNCxhbZdf>

# Clean text
clean_text_data = clean_text(reviews)
clean_review_length = clean_text_data.progress_map(lambda x: len(x.split(" ")))

# Get text statistics
print(f"Average review length: {clean_review_length.mean()}")
print(f"Min review length: {clean_review_length.min()}")
print(f"Max review length: {clean_review_length.max()}")

# |%%--%%| <oeNCxhbZdf|N8ImsCOCm1>

plt.subplot(1, 2, 1)
sns.boxplot(y=clean_review_length, hue=labels)
plt.ylabel("Clean review length", labelpad=12.5)

plt.subplot(1, 2, 2)
sns.kdeplot(x=clean_review_length, hue=labels)
plt.legend(labels.unique())
plt.xlabel("")
plt.ylabel("")

plt.show()

# |%%--%%| <N8ImsCOCm1|KNtI0BDJnF>

corpus = clean_text_data.progress_map(lambda x: x.split(" "))
mostCommon = Counter(clean_text_data).most_common(10)

words = []
freq = []
for word, count in mostCommon:
    words.append(word)
    freq.append(count)

sns.barplot(x=freq, y=words)
plt.title("Top 10 Most Frequently Occuring Words")
plt.show()
