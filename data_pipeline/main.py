import sys
from os.path import exists
from tqdm import tqdm

from utils.emails import get_email_from_csv, group_data_and_agg
from utils.tokenize import clean_text
from utils.model import get_model, predict_texts
from utils.neo4j import add_users, get_driver, SentimentUser

# Set up tqdm
tqdm.pandas()

# Print the usage if we did not pass the CSV file
if len(sys.argv) < 2:
    print(f"Usage: {sys.argv[0]} <csv file>")
    exit(1)

# Make sure the file exists
if not exists(sys.argv[1]):
    print(f"ERROR: File {sys.argv[1]} does not exist")
    exit(1)

datasetName = input("Dataset name: ")

# Get messages from the CSV file
messages = get_email_from_csv(sys.argv[1], max_emails=None)

messages["From"] = messages["From"].apply(lambda x: list(x)[0])
messages["To"] = messages["To"].apply(lambda x: list(x)[0])

# Clean the text
print("[i] Cleaning text...")
messages["clean_content"] = clean_text(messages["content"])  # pyright: ignore

# Label the text
print("[i] Classifying text")
model_name = input("Model name [review, emails]: ")

while model_name not in ["review", "emails"]:
    print("[-] Incorrect model name")
    model_name = input("Model name [review, emails]: ")

model = get_model(model_name)
messages["sentiment"] = predict_texts(
    model, messages["clean_content"]  # pyright: ignore
)

# Group by sender and receiver
print("[i] Grouping data by email 'To' and 'From'")
grouped_data = group_data_and_agg(messages)

# Get driver for neo4j
print("[i] Getting neo4j driver...")
driver = get_driver()

# Add them users
for _, row in tqdm(
    grouped_data.iterrows(), "[i] Adding users to neo4j", total=grouped_data.shape[0]
):
    userA = SentimentUser(email=row["From"])  # pyright: ignore
    userB = SentimentUser(email=row["To"])  # pyright: ignore

    add_users(
        driver,
        datasetName,
        userA,
        userB,
        row["mean_sentiment"],  # pyright: ignore
        row["email_count"],  # pyright: ignore
    )
