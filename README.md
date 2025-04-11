# Sentiment analyser

## IMPORTANT 

This project is **NOT** finished yet, you can expect some bugs or breaking updates, so please do not use this yet. If you find any issues, please open an issue on GitHub and I will review it ASAP!

## About this project
This project has been built in fulfillment of my college course for the Research in Emerging technologies and Project development modules.
The aim of this project is to improve team selection through analysing the sentiment of emails and choosing people with the best relationships.

## Main operations
If you are messing around with this project, I have included a Makefile to make your life easier.

- **docker-deploy**: Uses docker compose to deploy the neo4j and postgres containers 
- **docker-start**: Uses docker compose to start the containers

## Project structure

This project consists of 3 components:
1. Model training
2. Data pipeline
3. Web app

### Model training
This component is under the "training_model" directory of this repository, coded in python.

The purpose of this component is to train our neural network to classify sentiment of sentences.
Utilities are included to train models based on the [enron dataset](https://www.kaggle.com/datasets/wcukierski/enron-email-dataset) and [amazon reviews](https://www.kaggle.com/datasets/bittlingmayer/amazonreviews) datasets

Usage:
1. Download the datasets and place them under the **datasets** folder.
2. Create a venv with `python -m venv .venv` and activate the virtual environment
3. Download dependencies with `pip install -r requirements.txt`.
4. Run the main.py script and follow instructions

After this is done, you should have access to the model through either the `run_model.py` script or the data pipeline component

### Data pipeline

This component is to be found in the "data_pipeline" directory of the repository, coded in Rust.

The purpose of the data pipeline is to use the models to classify a CSV file passed by the user and then added to the Neo4J for our web app to interact with
This CSV file should include a column with **.eml** formatted text.

Usage:
1. Make sure you have ran the "training model" component, this should have created a model inside the **models** directory.
2. Configure your .env file with the required environment variables
3. Compile the binary and follow instructions

After this is done running, you should have a Neo4J database filled with the data from the CSV file.

#### Custom datasets
If you would like to run the data pipeline with your own personal emails, you could generate the CSV file with the following script:

```py
import imaplib
import email
import pandas as pd

# --- Configuration ---
EMAIL = "myemail@example.com"
PASSWORD = "myPassword"
IMAP_SERVER = "mail.example.com"
CSV_OUTPUT_FILE = "emails_example.csv"
MAX_EMAILS = 200

# --- Connect to IMAP ---
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
mail.login(EMAIL, PASSWORD)
mail.select("inbox")  # change folder if needed

# --- Search and fetch emails ---
result, data = mail.search(None, "ALL")
email_ids = data[0].split()[:MAX_EMAILS]

records = []

for eid in email_ids:
    res, msg_data = mail.fetch(eid, "(RFC822)")
    raw_email_bytes = msg_data[0][1]

    # Extract date
    msg = email.message_from_bytes(raw_email_bytes)
    date = msg.get("Date", "")

    # Convert raw email bytes to string (plaintext)
    raw_email_str = raw_email_bytes.decode("utf-8", errors="replace")

    # Add to dataset
    records.append({"Date": date, "message": raw_email_str})

mail.logout()

# --- Save to CSV ---
df = pd.DataFrame(records)
df.to_csv(CSV_OUTPUT_FILE, index=False)
print(f"Saved {len(df)} emails to {CSV_OUTPUT_FILE}")
```

### Web app

This component is found in the "app" directory, coded in mainly Typescript.

The purpose of the web app is for the user to interact with the Neo4J database, previous queries and more.

Usage:
1. Install dependencies with your preferred package manager: `bun i`
2. Make sure your **env** file is correct
3. Push your db tables: `bun run db:push`
4. Compile the web app: `bun run build`
5. Run the web app: `bun run start`

Technologies used:
- [Next.js](https://nextjs.org)
- [BetterAuth.js](https://better-auth.vercel.app/)
- [Drizzle](https://orm.drizzle.team)
- [Tailwind CSS](https://tailwindcss.com)
- [tRPC](https://trpc.io)


After this, you should be able to interact with the application in [http://localhost:3000](http://localhost:3000)


