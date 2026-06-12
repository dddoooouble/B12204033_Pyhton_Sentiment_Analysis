from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .analyzer import compute_overall_summary, compute_query_distribution, compute_sentiment_distribution, compute_time_sentiment, compute_top_terms
from .config import DEFAULT_MIN_TWEETS, DEFAULT_TIME_FREQUENCY, DEFAULT_TOP_N_TERMS, OUTPUT_DIR, ensure_directories, resolve_default_input_file
from .data_loader import load_data, summarize_dataset
from .preprocessor import apply_cleaning
from .sentiment_analyzer import apply_sentiment
from .visualizer import plot_query_distribution, plot_sentiment_dashboard, plot_top_terms


@dataclass
class PipelineOutputs:
    input_file: Path
    report_dir: Path
    figure_dir: Path
    scored_data_path: Path
    time_report_path: Path
    distribution_report_path: Path
    summary_report_path: Path
    top_terms_report_path: Path
    query_distribution_report_path: Path | None
    dashboard_path: Path
    top_terms_figure_path: Path
    query_distribution_figure_path: Path | None
    total_tweets: int
    time_windows: int


def run_pipeline(
    input_file: str | Path | None = None,
    output_dir: str | Path = OUTPUT_DIR,
    freq: str = DEFAULT_TIME_FREQUENCY,
    min_tweets: int = DEFAULT_MIN_TWEETS,
    top_n_terms: int = DEFAULT_TOP_N_TERMS,
) -> PipelineOutputs:
    ensure_directories()

    source_path = Path(input_file) if input_file else resolve_default_input_file()
    output_root = Path(output_dir)
    report_dir = output_root / "reports"
    figure_dir = output_root / "figures"
    report_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    raw_df = load_data(source_path)
    cleaned_df = apply_cleaning(raw_df)
    scored_df = apply_sentiment(cleaned_df)

    time_df = compute_time_sentiment(scored_df, freq=freq, min_tweets=min_tweets)
    if time_df.empty:
        time_df = compute_time_sentiment(scored_df, freq=freq, min_tweets=1)

    distribution_df = compute_sentiment_distribution(scored_df)
    top_terms_df = compute_top_terms(scored_df, top_n=top_n_terms)
    query_distribution_df = compute_query_distribution(raw_df)
    summary_df = compute_overall_summary(
        scored_df,
        time_df,
        dataset_info=summarize_dataset(raw_df),
        freq=freq,
        min_tweets=min_tweets,
        source_path=str(source_path),
    )

    scored_data_path = report_dir / "tweets_sentiment_scored.csv"
    time_report_path = report_dir / "time_sentiment_summary.csv"
    distribution_report_path = report_dir / "sentiment_distribution.csv"
    summary_report_path = report_dir / "overall_summary.csv"
    top_terms_report_path = report_dir / "top_terms_by_sentiment.csv"
    query_distribution_report_path = report_dir / "query_distribution.csv"

    scored_df.to_csv(scored_data_path, index=False)
    time_df.reset_index().to_csv(time_report_path, index=False)
    distribution_df.to_csv(distribution_report_path, index=False)
    summary_df.to_csv(summary_report_path, index=False)
    top_terms_df.to_csv(top_terms_report_path, index=False)
    if not query_distribution_df.empty:
        query_distribution_df.to_csv(query_distribution_report_path, index=False)
    else:
        query_distribution_report_path = None

    topic_label = _infer_topic_label(raw_df)
    dashboard_path = plot_sentiment_dashboard(
        time_df=time_df,
        distribution_df=distribution_df,
        summary_df=summary_df,
        output_path=figure_dir / "sentiment_dashboard.png",
        title=f"Twitter Sentiment Dashboard - {topic_label}",
    )
    top_terms_figure_path = plot_top_terms(
        top_terms_df=top_terms_df,
        output_path=figure_dir / "top_terms_by_sentiment.png",
        top_n=top_n_terms,
    )
    query_distribution_figure_path = plot_query_distribution(
        query_df=query_distribution_df,
        output_path=figure_dir / "query_distribution.png",
    )

    return PipelineOutputs(
        input_file=source_path,
        report_dir=report_dir,
        figure_dir=figure_dir,
        scored_data_path=scored_data_path,
        time_report_path=time_report_path,
        distribution_report_path=distribution_report_path,
        summary_report_path=summary_report_path,
        top_terms_report_path=top_terms_report_path,
        query_distribution_report_path=query_distribution_report_path,
        dashboard_path=dashboard_path,
        top_terms_figure_path=top_terms_figure_path,
        query_distribution_figure_path=query_distribution_figure_path,
        total_tweets=int(len(scored_df)),
        time_windows=int(len(time_df)),
    )


def _infer_topic_label(df) -> str:
    if "query" in df.columns:
        non_null = df["query"].dropna().astype(str).str.strip()
        if not non_null.empty:
            counts = non_null.value_counts()
            if len(counts) == 1:
                return counts.index[0]
            if counts.iloc[0] / len(non_null) >= 0.5:
                return counts.index[0]
            return "Mixed Twitter Topics"
    return "Selected Topic"
