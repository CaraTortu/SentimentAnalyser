import sys
import pandas as pd

from emails.clean_emails import clean_emails
from emails.find_model_params import find_email_params
from emails.label_emails import label_emails
from emails.train import train_email_model
from reviews.clean_dataset import clean_reviews
from reviews.find_model_params import find_review_params
from reviews.train import train_reviews


def print_usage():
    print(f"Usage: {sys.argv[0]} <dataset>")
    print("Datasets:")
    print("- emails")
    print("- reviews")


if len(sys.argv) < 2 or "-h" in sys.argv:
    print_usage()
    exit(1)

if sys.argv[1] not in ["emails", "reviews"]:
    print("[-] Error: Dataset does not exist. Please choose a valid dataset")
    print_usage()
    exit(1)


def exec_emails():
    # Read csv
    df = pd.read_csv("datasets/emails.csv")

    # Label dataset
    df = label_emails(df)

    # Clean text
    df = clean_emails(df)

    # Find best model parameters
    df: pd.DataFrame = df[["content", "sentiment"]].dropna()  # pyright: ignore
    find_email_params(df)

    # Train the model
    train_email_model(df)


def exec_reviews():
    # Read the file
    print("[i] Reading dataset...")
    df = pd.read_csv(
        "datasets/train.ft.txt.bz2",
        sep="\t",
        header=None,
        names=["text"],
        compression="bz2",
    )

    # Clean reviews
    df = clean_reviews(df)

    # Find best model params
    find_review_params(df)

    # Train the model
    train_reviews(df)


match sys.argv[1]:
    case "emails":
        exec_emails()
    case "reviews":
        exec_reviews()
