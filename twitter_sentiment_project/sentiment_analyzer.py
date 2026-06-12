from functools import lru_cache

import pandas as pd


@lru_cache(maxsize=1)
def get_sentiment_analyzer():
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'vaderSentiment'. Run 'pip install -r requirements.txt' first."
        ) from exc
    return SentimentIntensityAnalyzer()


def get_sentiment_score(text: str) -> float:
    analyzer = get_sentiment_analyzer()
    return analyzer.polarity_scores(text)["compound"]


def label_sentiment(score: float, positive_threshold: float = 0.05, negative_threshold: float = -0.05) -> str:
    if score >= positive_threshold:
        return "Positive"
    if score <= negative_threshold:
        return "Negative"
    return "Neutral"


def apply_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    analyzed = df.copy()
    analyzed["sentiment_score"] = analyzed["clean_text"].apply(get_sentiment_score)
    analyzed["sentiment"] = analyzed["sentiment_score"].apply(label_sentiment)
    analyzed["sentiment_strength"] = analyzed["sentiment_score"].abs()
    return analyzed
