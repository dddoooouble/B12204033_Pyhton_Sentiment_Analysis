import html
import re

import pandas as pd

from .config import COMMON_STOPWORDS

URL_PATTERN = re.compile(r"http\S+|www\.\S+")
MENTION_PATTERN = re.compile(r"@\w+")
NON_TEXT_PATTERN = re.compile(r"[^a-z0-9\s']")
MULTISPACE_PATTERN = re.compile(r"\s+")


def clean_tweet(text: str) -> str:
    normalized = html.unescape(str(text)).replace("\n", " ").replace("\r", " ")
    normalized = URL_PATTERN.sub(" ", normalized)
    normalized = MENTION_PATTERN.sub(" ", normalized)
    normalized = normalized.replace("#", " ").lower()
    normalized = NON_TEXT_PATTERN.sub(" ", normalized)
    normalized = MULTISPACE_PATTERN.sub(" ", normalized).strip()
    return normalized


def tokenize(text: str) -> list[str]:
    return [token for token in text.split() if len(token) > 2 and not token.isdigit()]


def build_query_stopwords(df: pd.DataFrame) -> set[str]:
    dynamic_stopwords = set(COMMON_STOPWORDS)
    if "query" not in df.columns:
        return dynamic_stopwords

    for value in df["query"].dropna().astype(str):
        dynamic_stopwords.update(tokenize(clean_tweet(value)))
    return dynamic_stopwords


def apply_cleaning(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned["clean_text"] = cleaned["text"].astype(str).apply(clean_tweet)
    cleaned = cleaned[cleaned["clean_text"].str.len() > 0].copy()
    cleaned["tokens"] = cleaned["clean_text"].apply(tokenize)
    cleaned["token_count"] = cleaned["tokens"].apply(len)
    return cleaned.reset_index(drop=True)
