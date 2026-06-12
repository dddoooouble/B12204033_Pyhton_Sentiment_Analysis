from __future__ import annotations

from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

from .config import SENTIMENT_COLORS, SENTIMENT_LABELS


def _apply_plot_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")


def plot_fine_grained_sentiment(
    time_df: pd.DataFrame,
    level: str = "minute",
    output_path: str | Path | None = None,
    title: str | None = None,
) -> Path | None:
    _apply_plot_style()
    fig, ax = plt.subplots(figsize=(14, 6))

    for sentiment in SENTIMENT_LABELS:
        ax.plot(
            time_df.index,
            time_df[f"{sentiment}_ratio"],
            label=sentiment,
            linewidth=2.3,
            color=SENTIMENT_COLORS[sentiment],
        )

    ax.set_title(title or f"Sentiment Trend by {level.capitalize()}", fontsize=15, weight="bold")
    ax.set_xlabel("Time")
    ax.set_ylabel("Sentiment Ratio")
    ax.set_ylim(0, 1)
    ax.legend(frameon=True)
    ax.grid(True, linestyle="--", alpha=0.35)
    fig.tight_layout()

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, dpi=220, bbox_inches="tight")
        plt.close(fig)
        return path

    plt.show()
    return None


def plot_sentiment_dashboard(
    time_df: pd.DataFrame,
    distribution_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    output_path: str | Path,
    title: str,
) -> Path:
    _apply_plot_style()
    fig = plt.figure(figsize=(16, 10), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=[2.2, 1.2])

    trend_ax = fig.add_subplot(grid[0, :])
    distribution_ax = fig.add_subplot(grid[1, 0])
    summary_ax = fig.add_subplot(grid[1, 1])

    volume_ax = trend_ax.twinx()
    volume_ax.bar(time_df.index, time_df["tweet_count"], width=0.01, color="#D9D9D9", alpha=0.45, label="Tweet Count")
    volume_ax.set_ylabel("Tweet Count", color="#6C757D")
    volume_ax.grid(False)

    for sentiment in SENTIMENT_LABELS:
        trend_ax.plot(
            time_df.index,
            time_df[f"{sentiment}_ratio"],
            color=SENTIMENT_COLORS[sentiment],
            linewidth=2.5,
            marker="o",
            markersize=3.8,
            label=f"{sentiment} Ratio",
        )

    trend_ax.set_title(title, fontsize=18, weight="bold")
    trend_ax.set_xlabel("Time")
    trend_ax.set_ylabel("Sentiment Ratio")
    trend_ax.set_ylim(0, 1)
    trend_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    trend_ax.grid(True, linestyle="--", alpha=0.35)
    trend_ax.legend(loc="upper left", frameon=True, ncol=3)

    _annotate_peak(trend_ax, time_df, "Positive_ratio", "Positive Peak", SENTIMENT_COLORS["Positive"])
    _annotate_peak(trend_ax, time_df, "Negative_ratio", "Negative Peak", SENTIMENT_COLORS["Negative"])

    distribution_ax.barh(
        distribution_df["sentiment"],
        distribution_df["count"],
        color=[SENTIMENT_COLORS[sentiment] for sentiment in distribution_df["sentiment"]],
    )
    distribution_ax.set_title("Overall Sentiment Distribution", fontsize=14, weight="bold")
    distribution_ax.set_xlabel("Tweet Count")
    distribution_ax.set_ylabel("")
    distribution_ax.invert_yaxis()

    for row_index, row in distribution_df.reset_index(drop=True).iterrows():
        distribution_ax.text(
            row["count"] + max(distribution_df["count"]) * 0.01,
            row_index,
            f"{int(row['count']):,} ({row['ratio_pct']:.1f}%)",
            va="center",
            fontsize=11,
        )

    summary_ax.axis("off")
    summary_lookup = dict(zip(summary_df["metric"], summary_df["value"]))
    summary_text = "\n".join(
        [
            "Project Summary",
            f"Total tweets: {summary_lookup.get('total_tweets', 'N/A')}",
            f"Date range: {summary_lookup.get('date_range_start', 'N/A')} to",
            f"            {summary_lookup.get('date_range_end', 'N/A')}",
            f"Average score: {summary_lookup.get('average_sentiment_score', 'N/A')}",
            f"Positive share: {summary_lookup.get('positive_ratio_pct', 'N/A')}%",
            f"Neutral share: {summary_lookup.get('neutral_ratio_pct', 'N/A')}%",
            f"Negative share: {summary_lookup.get('negative_ratio_pct', 'N/A')}%",
            f"Busiest window: {summary_lookup.get('busiest_window', 'N/A')}",
            f"Peak positive: {summary_lookup.get('peak_positive_window', 'N/A')}",
            f"Peak negative: {summary_lookup.get('peak_negative_window', 'N/A')}",
        ]
    )
    summary_ax.text(
        0.02,
        0.98,
        summary_text,
        ha="left",
        va="top",
        fontsize=11.5,
        linespacing=1.55,
        bbox={"boxstyle": "round,pad=0.8", "facecolor": "#F8F9FA", "edgecolor": "#D9D9D9"},
    )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_top_terms(top_terms_df: pd.DataFrame, output_path: str | Path, top_n: int = 12) -> Path:
    _apply_plot_style()
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), constrained_layout=True)

    for axis, sentiment in zip(axes, SENTIMENT_LABELS):
        subset = top_terms_df[top_terms_df["sentiment"] == sentiment].head(top_n).copy()
        if subset.empty:
            axis.text(0.5, 0.5, "No terms available", ha="center", va="center", fontsize=12)
            axis.axis("off")
            continue

        subset = subset.sort_values("count", ascending=True)
        axis.barh(subset["term"], subset["count"], color=SENTIMENT_COLORS[sentiment], alpha=0.9)
        axis.set_title(f"{sentiment} Top Terms", fontsize=14, weight="bold")
        axis.set_xlabel("Count")
        axis.set_ylabel("")
        for _, row in subset.iterrows():
            axis.text(row["count"] + 0.3, row["term"], str(int(row["count"])), va="center", fontsize=10)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_query_distribution(query_df: pd.DataFrame, output_path: str | Path) -> Path | None:
    if query_df.empty:
        return None

    _apply_plot_style()
    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)
    ordered = query_df.sort_values("count", ascending=True)
    bars = ax.barh(ordered["query"], ordered["count"], color="#3D5A80", alpha=0.9)

    ax.set_title("Top Query Distribution", fontsize=16, weight="bold")
    ax.set_xlabel("Tweet Count")
    ax.set_ylabel("")
    ax.grid(True, axis="x", linestyle="--", alpha=0.3)

    for bar, (_, row) in zip(bars, ordered.iterrows()):
        ax.text(
            bar.get_width() + max(ordered["count"]) * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{int(row['count']):,} ({row['ratio_pct']:.1f}%)",
            va="center",
            fontsize=10.5,
        )

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def _annotate_peak(axis: plt.Axes, time_df: pd.DataFrame, column: str, label: str, color: str) -> None:
    if time_df.empty:
        return

    peak_time = time_df[column].idxmax()
    peak_value = time_df.loc[peak_time, column]
    axis.scatter([peak_time], [peak_value], color=color, s=70, zorder=4)
    axis.annotate(
        f"{label}\n{peak_time.strftime('%H:%M')} | {peak_value:.2f}",
        xy=(peak_time, peak_value),
        xytext=(10, 18),
        textcoords="offset points",
        fontsize=10,
        color=color,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": color, "alpha": 0.9},
        arrowprops={"arrowstyle": "->", "color": color, "lw": 1.2},
    )
