from collections import Counter

import pandas as pd

from .config import EVENT_KEYWORDS, SENTIMENT_LABELS
from .preprocessor import build_query_stopwords


def compute_time_sentiment(df: pd.DataFrame, freq: str = "15min", min_tweets: int = 10) -> pd.DataFrame:
    working = df.copy()
    working["time_bin"] = working["created_at"].dt.floor(freq)

    sentiment_counts = (
        working.groupby(["time_bin", "sentiment"]).size().unstack(fill_value=0).reindex(columns=SENTIMENT_LABELS, fill_value=0)
    )
    sentiment_counts["tweet_count"] = sentiment_counts.sum(axis=1)

    for sentiment in SENTIMENT_LABELS:
        sentiment_counts[f"{sentiment}_ratio"] = sentiment_counts[sentiment] / sentiment_counts["tweet_count"]

    sentiment_counts["dominant_sentiment"] = sentiment_counts[list(SENTIMENT_LABELS)].idxmax(axis=1)
    sentiment_counts["sentiment_gap"] = sentiment_counts["Positive_ratio"] - sentiment_counts["Negative_ratio"]
    filtered = sentiment_counts[sentiment_counts["tweet_count"] >= min_tweets].copy()
    return filtered


def compute_sentiment_distribution(df: pd.DataFrame) -> pd.DataFrame:
    counts = df["sentiment"].value_counts().reindex(SENTIMENT_LABELS, fill_value=0)
    distribution = counts.reset_index()
    distribution.columns = ["sentiment", "count"]
    distribution["ratio"] = distribution["count"] / distribution["count"].sum()
    distribution["ratio_pct"] = distribution["ratio"] * 100
    return distribution


def compute_top_terms(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    stopwords = build_query_stopwords(df)
    rows: list[dict[str, str | int]] = []

    for sentiment in SENTIMENT_LABELS:
        counter: Counter[str] = Counter()
        subset = df.loc[df["sentiment"] == sentiment, "tokens"]
        for tokens in subset:
            counter.update(token for token in tokens if token not in stopwords and len(token) > 2)

        for term, count in counter.most_common(top_n):
            rows.append({"sentiment": sentiment, "term": term, "count": int(count)})

    return pd.DataFrame(rows)


def compute_query_distribution(df: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    if "query" not in df.columns:
        return pd.DataFrame(columns=["query", "count", "ratio", "ratio_pct"])

    queries = df["query"].dropna().astype(str).str.strip()
    queries = queries[queries != ""]
    if queries.empty:
        return pd.DataFrame(columns=["query", "count", "ratio", "ratio_pct"])

    all_counts = queries.value_counts()
    total_queries = all_counts.sum()
    counts = all_counts.head(top_n)
    query_df = counts.reset_index()
    query_df.columns = ["query", "count"]
    query_df["ratio"] = query_df["count"] / total_queries
    query_df["ratio_pct"] = query_df["ratio"] * 100
    return query_df


def filter_event_subset(df: pd.DataFrame, keywords: tuple[str, ...] = EVENT_KEYWORDS) -> pd.DataFrame:
    if "text" not in df.columns:
        return df.iloc[0:0].copy()

    pattern = "|".join(keywords)
    mask = df["text"].astype(str).str.contains(pattern, case=False, na=False, regex=True)
    subset = df.loc[mask].copy()
    return subset.sort_values("created_at").reset_index(drop=True)


def compute_sentiment_comparison(full_df: pd.DataFrame, subset_df: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str | float]] = []

    for group_name, df in (("Overall", full_df), ("Capitol Event Subset", subset_df)):
        if df.empty:
            continue
        distribution = compute_sentiment_distribution(df)
        for _, row in distribution.iterrows():
            rows.append(
                {
                    "group": group_name,
                    "sentiment": row["sentiment"],
                    "count": int(row["count"]),
                    "ratio_pct": float(row["ratio_pct"]),
                }
            )

    return pd.DataFrame(rows)


def compute_event_summary(subset_df: pd.DataFrame, full_df: pd.DataFrame, time_df: pd.DataFrame) -> pd.DataFrame:
    if subset_df.empty:
        return pd.DataFrame(
            [
                {"metric": "subset_size", "value": 0},
                {"metric": "subset_share_pct", "value": 0.0},
            ]
        )

    distribution = compute_sentiment_distribution(subset_df).set_index("sentiment")
    busiest_window = time_df["tweet_count"].idxmax() if not time_df.empty else pd.NaT
    average_score = float(subset_df["sentiment_score"].mean())

    metrics = [
        {"metric": "subset_size", "value": int(len(subset_df))},
        {"metric": "subset_share_pct", "value": round(int(len(subset_df)) / max(int(len(full_df)), 1) * 100, 2)},
        {"metric": "subset_average_sentiment_score", "value": round(average_score, 4)},
        {"metric": "subset_negative_ratio_pct", "value": round(float(distribution.loc["Negative", "ratio_pct"]), 2)},
        {"metric": "subset_positive_ratio_pct", "value": round(float(distribution.loc["Positive", "ratio_pct"]), 2)},
        {"metric": "subset_neutral_ratio_pct", "value": round(float(distribution.loc["Neutral", "ratio_pct"]), 2)},
        {"metric": "subset_start_time", "value": _format_timestamp(subset_df["created_at"].min())},
        {"metric": "subset_end_time", "value": _format_timestamp(subset_df["created_at"].max())},
        {"metric": "subset_busiest_window", "value": _format_timestamp(busiest_window)},
        {
            "metric": "subset_peak_window_tweet_count",
            "value": int(time_df["tweet_count"].max()) if not time_df.empty else 0,
        },
    ]
    return pd.DataFrame(metrics)


def compute_overall_summary(
    df: pd.DataFrame,
    time_df: pd.DataFrame,
    dataset_info: dict[str, str | int],
    freq: str,
    min_tweets: int,
    source_path: str,
) -> pd.DataFrame:
    distribution = compute_sentiment_distribution(df).set_index("sentiment")
    average_score = float(df["sentiment_score"].mean())

    busiest_window = time_df["tweet_count"].idxmax() if not time_df.empty else pd.NaT
    peak_positive_window = time_df["Positive_ratio"].idxmax() if not time_df.empty else pd.NaT
    peak_negative_window = time_df["Negative_ratio"].idxmax() if not time_df.empty else pd.NaT

    metrics = [
        {"metric": "source_file", "value": source_path},
        {"metric": "total_tweets", "value": int(len(df))},
        {"metric": "date_range_start", "value": dataset_info["start_time"]},
        {"metric": "date_range_end", "value": dataset_info["end_time"]},
        {"metric": "time_frequency", "value": freq},
        {"metric": "min_tweets_threshold", "value": int(min_tweets)},
        {"metric": "time_windows_retained", "value": int(len(time_df))},
        {"metric": "average_sentiment_score", "value": round(average_score, 4)},
        {
            "metric": "positive_ratio_pct",
            "value": round(float(distribution.loc["Positive", "ratio_pct"]), 2),
        },
        {
            "metric": "neutral_ratio_pct",
            "value": round(float(distribution.loc["Neutral", "ratio_pct"]), 2),
        },
        {
            "metric": "negative_ratio_pct",
            "value": round(float(distribution.loc["Negative", "ratio_pct"]), 2),
        },
        {
            "metric": "busiest_window",
            "value": _format_timestamp(busiest_window),
        },
        {
            "metric": "peak_positive_window",
            "value": _format_timestamp(peak_positive_window),
        },
        {
            "metric": "peak_negative_window",
            "value": _format_timestamp(peak_negative_window),
        },
    ]

    return pd.DataFrame(metrics)


def _format_timestamp(timestamp: pd.Timestamp) -> str:
    if pd.isna(timestamp):
        return "N/A"
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")
