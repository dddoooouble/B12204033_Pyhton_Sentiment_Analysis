import argparse

from twitter_sentiment_project.config import DEFAULT_MIN_TWEETS, DEFAULT_TIME_FREQUENCY, DEFAULT_TOP_N_TERMS, resolve_default_input_file
from twitter_sentiment_project.pipeline import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Twitter sentiment analysis pipeline")
    parser.add_argument(
        "--input",
        default=str(resolve_default_input_file()),
        help="Path to the CSV data file",
    )
    parser.add_argument(
        "--output-dir",
        default="outputs",
        help="Directory where figures and reports will be stored",
    )
    parser.add_argument(
        "--freq",
        default=DEFAULT_TIME_FREQUENCY,
        help="Time bin frequency for timeline aggregation, for example 15min or 30min",
    )
    parser.add_argument(
        "--min-tweets",
        type=int,
        default=DEFAULT_MIN_TWEETS,
        help="Minimum number of tweets required to keep a time window",
    )
    parser.add_argument(
        "--top-n-terms",
        type=int,
        default=DEFAULT_TOP_N_TERMS,
        help="Number of representative terms to keep for each sentiment",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    outputs = run_pipeline(
        input_file=args.input,
        output_dir=args.output_dir,
        freq=args.freq,
        min_tweets=args.min_tweets,
        top_n_terms=args.top_n_terms,
    )

    print("Analysis completed successfully.")
    print(f"Input data: {outputs.input_file}")
    print(f"Total tweets analyzed: {outputs.total_tweets:,}")
    print(f"Time windows retained: {outputs.time_windows}")
    print(f"Reports saved to: {outputs.report_dir}")
    print(f"Figures saved to: {outputs.figure_dir}")
    print(f"Dashboard figure: {outputs.dashboard_path}")
    print(f"Top terms figure: {outputs.top_terms_figure_path}")
    if outputs.query_distribution_figure_path:
        print(f"Query distribution figure: {outputs.query_distribution_figure_path}")
    print(f"Capitol event subset tweets: {outputs.event_subset_tweets:,}")
    if outputs.event_timeline_figure_path:
        print(f"Capitol event timeline figure: {outputs.event_timeline_figure_path}")
    if outputs.event_comparison_figure_path:
        print(f"Capitol event comparison figure: {outputs.event_comparison_figure_path}")
    if outputs.event_top_terms_figure_path:
        print(f"Capitol event top terms figure: {outputs.event_top_terms_figure_path}")


if __name__ == "__main__":
    main()
