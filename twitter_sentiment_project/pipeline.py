from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .analyzer import (
    compute_event_summary,
    compute_overall_summary,
    compute_query_distribution,
    compute_sentiment_comparison,
    compute_sentiment_distribution,
    compute_time_sentiment,
    compute_top_terms,
    filter_event_subset,
)
from .config import (
    DEFAULT_MIN_TWEETS,
    DEFAULT_TIME_FREQUENCY,
    DEFAULT_TOP_N_TERMS,
    EVENT_MARKERS_UTC,
    OUTPUT_DIR,
    ensure_directories,
    resolve_default_input_file,
)
from .data_loader import load_data, summarize_dataset
from .preprocessor import apply_cleaning
from .sentiment_analyzer import apply_sentiment
from .visualizer import (
    plot_event_timeline,
    plot_query_distribution,
    plot_sentiment_comparison,
    plot_sentiment_dashboard,
    plot_top_terms,
)


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
    event_summary_report_path: Path | None
    event_distribution_report_path: Path | None
    event_comparison_report_path: Path | None
    event_top_terms_report_path: Path | None
    event_time_report_path: Path | None
    dashboard_path: Path
    top_terms_figure_path: Path
    query_distribution_figure_path: Path | None
    event_timeline_figure_path: Path | None
    event_comparison_figure_path: Path | None
    event_top_terms_figure_path: Path | None
    total_tweets: int
    time_windows: int
    event_subset_tweets: int


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
    event_summary_report_path = report_dir / "capitol_event_summary.csv"
    event_distribution_report_path = report_dir / "capitol_event_sentiment_distribution.csv"
    event_comparison_report_path = report_dir / "capitol_event_sentiment_comparison.csv"
    event_top_terms_report_path = report_dir / "capitol_event_top_terms.csv"
    event_time_report_path = report_dir / "capitol_event_time_summary.csv"

    scored_df.to_csv(scored_data_path, index=False)
    time_df.reset_index().to_csv(time_report_path, index=False)
    distribution_df.to_csv(distribution_report_path, index=False)
    summary_df.to_csv(summary_report_path, index=False)
    top_terms_df.to_csv(top_terms_report_path, index=False)
    if not query_distribution_df.empty:
        query_distribution_df.to_csv(query_distribution_report_path, index=False)
    else:
        query_distribution_report_path = None

    event_subset_df = filter_event_subset(scored_df)
    event_time_df = compute_time_sentiment(event_subset_df, freq=freq, min_tweets=1)
    event_distribution_df = compute_sentiment_distribution(event_subset_df) if not event_subset_df.empty else distribution_df.iloc[0:0].copy()
    event_top_terms_df = compute_top_terms(event_subset_df, top_n=top_n_terms) if not event_subset_df.empty else top_terms_df.iloc[0:0].copy()
    event_comparison_df = compute_sentiment_comparison(scored_df, event_subset_df)
    event_summary_df = compute_event_summary(event_subset_df, scored_df, event_time_df)

    if not event_summary_df.empty:
        event_summary_df.to_csv(event_summary_report_path, index=False)
    else:
        event_summary_report_path = None
    if not event_distribution_df.empty:
        event_distribution_df.to_csv(event_distribution_report_path, index=False)
    else:
        event_distribution_report_path = None
    if not event_comparison_df.empty:
        event_comparison_df.to_csv(event_comparison_report_path, index=False)
    else:
        event_comparison_report_path = None
    if not event_top_terms_df.empty:
        event_top_terms_df.to_csv(event_top_terms_report_path, index=False)
    else:
        event_top_terms_report_path = None
    if not event_time_df.empty:
        event_time_df.reset_index().to_csv(event_time_report_path, index=False)
    else:
        event_time_report_path = None

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
    event_markers = [
        (pd.Timestamp(timestamp, tz="UTC").tz_localize(None), label)
        for timestamp, label in EVENT_MARKERS_UTC
    ]
    event_timeline_figure_path = plot_event_timeline(
        time_df=event_time_df,
        output_path=figure_dir / "capitol_event_timeline.png",
        title="Jan. 6 Capitol Event Subset: Sentiment and Volume Over Time",
        event_markers=event_markers,
    )
    event_comparison_figure_path = plot_sentiment_comparison(
        comparison_df=event_comparison_df,
        output_path=figure_dir / "capitol_event_sentiment_comparison.png",
        title="Overall Dataset vs Capitol Event Subset",
    )
    event_top_terms_figure_path = plot_top_terms(
        top_terms_df=event_top_terms_df,
        output_path=figure_dir / "capitol_event_top_terms.png",
        top_n=top_n_terms,
    ) if not event_top_terms_df.empty else None

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
        event_summary_report_path=event_summary_report_path,
        event_distribution_report_path=event_distribution_report_path,
        event_comparison_report_path=event_comparison_report_path,
        event_top_terms_report_path=event_top_terms_report_path,
        event_time_report_path=event_time_report_path,
        dashboard_path=dashboard_path,
        top_terms_figure_path=top_terms_figure_path,
        query_distribution_figure_path=query_distribution_figure_path,
        event_timeline_figure_path=event_timeline_figure_path,
        event_comparison_figure_path=event_comparison_figure_path,
        event_top_terms_figure_path=event_top_terms_figure_path,
        total_tweets=int(len(scored_df)),
        time_windows=int(len(time_df)),
        event_subset_tweets=int(len(event_subset_df)),
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
