# |%%--%%| <9wq1ieyyVK|0ctncoZd4X>
r"""°°°
# Setup

First we want to import required libraries
°°°"""
# |%%--%%| <0ctncoZd4X|pcA1Q2XcAJ>

from email.message import Message
import pandas as pd
import email
from tqdm import tqdm

tqdm.pandas()

# |%%--%%| <pcA1Q2XcAJ|HQuiWWOyqK>
r"""°°°
# Dataset processing

Load the dataset
°°°"""
# |%%--%%| <HQuiWWOyqK|iLnPurZSWl>

print("[i] Reading dataset")
df = pd.read_csv("./datasets/emails.csv")

# |%%--%%| <iLnPurZSWl|yCJioqGfL4>

emails = [
    email.message_from_string(txt) for txt in tqdm(df["message"], "[i] Parsing emails")
]

df.drop("message", axis=1, inplace=True)

print("[i] Splitting email into dataset")
for key in tqdm(emails[0].keys()):
    df[key] = [doc[key] for doc in emails]

# |%%--%%| <yCJioqGfL4|v8BlW0mwAM>


# Parse message contents
def get_contents(msg: Message) -> str:
    parts = []

    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            parts.append(part.get_payload())

    return "".join(parts)


df["content"] = [get_contents(e) for e in tqdm(emails, "[i] Parsing message contents")]


# |%%--%%| <v8BlW0mwAM|Y9qJv5Kv1W>


# Parse email addresses
def get_addresses(emails: str | None) -> frozenset[str]:
    if not emails:
        return frozenset()

    addresses = frozenset(map(lambda x: x.strip(), emails.split(",")))
    return addresses


print("[i] Parsing From and To fields")
df["From"] = df["From"].progress_map(get_addresses)
df["To"] = df["To"].progress_map(get_addresses)


# |%%--%%| <Y9qJv5Kv1W|WOuZsBEyF0>

# Set index
df = df.set_index("Message-ID")
df.drop(
    [
        "file",
        "Mime-Version",
        "Content-Type",
        "Content-Transfer-Encoding",
        "X-Folder",
        "X-Origin",
        "X-FileName",
        "X-cc",
        "X-From",
        "X-To",
        "X-bcc",
    ],
    axis=1,
    inplace=True,
)

# |%%--%%| <WOuZsBEyF0|tZaXDzEWW8>

# Clean the dates
print("[i] Parsing dates")
df["Date"] = pd.to_datetime(
    df["Date"].str.extract(r"^(.*? -\d{4})", expand=False),
    format="%a, %d %b %Y %H:%M:%S %z",
    errors="coerce",
)

df.dropna(subset=["Date", "To", "From"], inplace=True)

# |%%--%%| <tZaXDzEWW8|DeaztDZNgg>
r"""°°°
# Labeling the dataset
°°°"""
# |%%--%%| <DeaztDZNgg|SSbnTgX5tX>

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# |%%--%%| <SSbnTgX5tX|JTQdbUXQxu>

# Analyze all emails
print("[i] Labelling emails")
df["sentiment"] = df["content"].progress_map(
    lambda x: analyzer.polarity_scores(x)["compound"]
)

# |%%--%%| <JTQdbUXQxu|L5iovmZHLS>

# Save the dataset
print("[i] Formatting From and To fields for CSV")
df["From"] = df["From"].progress_apply(lambda x: ";;".join(x))
df["To"] = df["To"].progress_apply(lambda x: ";;".join(x))

print("[i] Saving emails")
df.to_csv("./datasets/emails_labelled.csv", index=False)
