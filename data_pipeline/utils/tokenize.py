import re

import pandas as pd
import nltk
from nltk.corpus import stopwords

nltk.download("stopwords")
nltk.download("punkt")
nltk.download("punkt_tab")

emoticon_meanings = {
    " :)": "happy",
    " :(": "sad",
    " :D": "very happy",
    " :|": "neutral",
    " :O": "surprised",
    " <3": "love",
    " ;)": "wink",
    " :P": "playful",
    " :/": "confused",
    " :*": "kiss",
    " :')": "touched",
    " XD": "laughing",
    " :3": "cute",
    " >:(": "angry",
    " :-O": "shocked",
    " :|]": "robot",
    " :>": "sly",
    " ^_^": "happy",
    " O_o": "confused",
    " :-|": "straight face",
    " :X": "silent",
    " B-)": "cool",
    " <(‘.'<)": "dance",
    " (-_-)": "bored",
    " (>_<)": "upset",
    " (¬‿¬)": "sarcastic",
    " (o_o)": "surprised",
    " (o.O)": "shocked",
    " :0": "shocked",
    " :*(": "crying",
    " :v ": "pac-Man",
    " (^_^)v ": "double victory",
    " :-D": "big grin",
    " :-*": "blowing a kiss",
    " :^)": "nosey",
    " :-((": "very sad",
    " :-(": "frowning",
}


# Functions for cleaning
def remove_pattern(input_txt: str, pattern: str) -> str:
    input_txt = re.sub(pattern, "", input_txt)
    return input_txt


def remove_links(content: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return content.progress_apply(remove_pattern, pattern=r"https?://\S+|www\.\S+")


def remove_repeats(content: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return content.progress_apply(lambda x: re.sub(r"(.)\1{2,}", r"\1", x))


def remove_lots_space(content: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return content.progress_apply(lambda x: re.sub(r"\s+", " ", x))


def replace_emoticons(content: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    def convert_text(txt: str) -> str:
        for emoticon, meaning in emoticon_meanings.items():
            txt = txt.replace(emoticon, f" {meaning}")

        return txt

    return content.progress_apply(convert_text)


def remove_unwanted_chars(
    content: pd.DataFrame | pd.Series,
) -> pd.DataFrame | pd.Series:
    return content.progress_apply(lambda x: re.sub(r"[^a-zA-Z#]", " ", x))


def remove_short_words(
    content: pd.DataFrame | pd.Series,
) -> pd.DataFrame | pd.Series:
    return content.progress_apply(lambda x: re.sub(r"\b\w{1,2}\b", " ", x))


def remove_redundant_words(
    content: pd.DataFrame | pd.Series,
) -> pd.DataFrame | pd.Series:
    def remove_redundant_words_extra_spaces(text: str):
        ## Remove contractions using regular expressions
        contraction_pattern = re.compile(r"'\w+|\w+'\w+|\w+'")
        text = contraction_pattern.sub("", text)

        ## Define a set of stopwords
        stop_words = set(stopwords.words("english"))

        ## Remove stopwords and extra spaces
        words = text.split()
        filtered_words = [word for word in words if word.lower() not in stop_words]
        clean_text = " ".join(filtered_words)

        ## Remove extra spaces
        clean_text = " ".join(clean_text.split())

        return clean_text

    return content.progress_apply(remove_redundant_words_extra_spaces)


def remove_numbers(content: pd.DataFrame | pd.Series) -> pd.DataFrame | pd.Series:
    return content.progress_apply(lambda x: re.sub(r"(?<=\w)\d+|\d+(?=\w)", "", x))


def clean_text(content: pd.Series) -> pd.Series:
    content = content.str.lower()
    content = remove_links(content)  # pyright: ignore
    content = replace_emoticons(content)  # pyright: ignore
    content = remove_unwanted_chars(content)  # pyright: ignore
    content = remove_repeats(content)  # pyright: ignore
    content = remove_short_words(content)  # pyright: ignore
    content = remove_numbers(content)  # pyright: ignore
    content = remove_lots_space(content)  # pyright: ignore

    return content
