from email.message import Message
from pandas import DataFrame
import pandas as pd
import email

from tqdm import tqdm

# Global vars
EMAIL_COL = "message"


# Parse message contents
def get_contents(msg: Message) -> str:
    parts = []

    for part in msg.walk():
        if part.get_content_type() == "text/plain":
            parts.append(part.get_payload())

    return "".join(parts)


def parse_email_adresses(emails: str | None) -> frozenset[str]:
    if not emails:
        return frozenset()

    addresses = frozenset(map(lambda x: x.strip(), emails.split(",")))
    return addresses


def get_email_from_csv(filename: str, max_emails: int | None = None) -> DataFrame:
    # Load the file
    print("[i] Loading file...")
    with open(filename, "r") as f:
        df = pd.read_csv(f)

    if max_emails:
        df = df.iloc[:max_emails]

    # Check columns
    if EMAIL_COL not in df.columns:
        print(f"ERROR: CSV file does not have an email column")
        exit(1)

    # Make sure the dataset only has the email colum
    messages = df[EMAIL_COL]

    # Parse emails
    emails = list(map(email.message_from_string, tqdm(messages, "[i] Parsing emails")))

    # Add the fields to the dataframe
    print("[i] Splitting fields for the dataframe")
    for k in emails[0].keys():
        df[k] = [doc[k] for doc in emails]

    # Parse email contents
    df["content"] = list(map(get_contents, tqdm(emails, "[i] Parsing email contents")))

    print("[i] Parsing email adresses...")
    df["From"] = df["From"].progress_map(parse_email_adresses)
    df["To"] = df["To"].progress_map(parse_email_adresses)

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
            "X-bcc",
            "X-cc",
            "X-From",
            "X-To",
        ],
        axis=1,
        inplace=True,
    )

    # Clean the dates
    print("[i] Formatting dates...")
    df["Date"] = pd.to_datetime(
        df["Date"].str.extract(r"^(.*? -\d{4})", expand=False),
        format="%a, %d %b %Y %H:%M:%S %z",
        errors="coerce",
        utc=True,
    )

    df.dropna(subset=["Date", "To", "From"], inplace=True)

    # Remove rows with emails sent to multiple people
    print("[i] Removing emails with multiple or no 'To' adressess")
    index_delete = df[
        (df["To"].progress_map(len) > 1) | (df["To"].progress_map(len) == 0)
    ].index
    print(f"[i] Found {len(index_delete)} emails to delete")
    df.drop(index_delete, inplace=True)  # pyright: ignore

    return df


def group_data_and_agg(messages: pd.DataFrame) -> pd.DataFrame:
    grouped = messages[["From", "To", "sentiment"]].copy()

    # Create a new column to ensure email pairs are always sorted
    grouped["pair"] = grouped.apply(
        lambda row: tuple(sorted([row["From"], row["To"]])), axis=1
    )

    # Group by the pair and compute mean sentiment & email count
    aggregated = (
        grouped.groupby("pair")
        .agg(
            mean_sentiment=("sentiment", "mean"),
            email_count=("sentiment", "count"),
        )
        .reset_index()
    )

    # Split the "pair" tuple into separate "From" and "To" columns
    aggregated[["From", "To"]] = pd.DataFrame(
        aggregated["pair"].tolist(), index=aggregated.index
    )

    # Drop the temporary "pair" column
    aggregated = aggregated.drop(columns=["pair"])

    # Reorder columns
    aggregated = aggregated[["From", "To", "mean_sentiment", "email_count"]]

    return aggregated  # pyright: ignore
