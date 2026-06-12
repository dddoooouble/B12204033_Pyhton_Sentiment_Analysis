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


def plot_sentiment_comparison(comparison_df: pd.DataFrame, output_path: str | Path, title: str) -> Path | None:
    if comparison_df.empty:
        return None

    _apply_plot_style()
    fig, ax = plt.subplots(figsize=(12, 7), constrained_layout=True)
    positions = range(len(SENTIMENT_LABELS))
    width = 0.34
    groups = comparison_df["group"].drop_duplicates().tolist()

    for index, group in enumerate(groups):
        subset = comparison_df[comparison_df["group"] == group].set_index("sentiment").reindex(SENTIMENT_LABELS)
        offset = (-width / 2) if index == 0 else (width / 2)
        bars = ax.bar(
            [position + offset for position in positions],
            subset["ratio_pct"],
            width=width,
            label=group,
            color=[SENTIMENT_COLORS[sentiment] for sentiment in SENTIMENT_LABELS] if index == 0 else "#D6E4F0",
            edgecolor="#233142",
            alpha=0.88,
        )
        for bar, value in zip(bars, subset["ratio_pct"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.9,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=10,
            )

    ax.set_xticks(list(positions))
    ax.set_xticklabels(SENTIMENT_LABELS)
    ax.set_ylabel("Ratio (%)")
    ax.set_ylim(0, max(comparison_df["ratio_pct"]) * 1.22)
    ax.set_title(title, fontsize=16, weight="bold")
    ax.legend(frameon=True)
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=220, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_event_timeline(
    time_df: pd.DataFrame,
    output_path: str | Path,
    title: str,
    event_markers: list[tuple[pd.Timestamp, str]] | None = None,
) -> Path | None:
    if time_df.empty:
        return None

    _apply_plot_style()
    working = time_df.sort_index().copy()
    full_index = _build_continuous_time_index(working.index)
    if full_index is not None:
        working = working.reindex(full_index)
        working["tweet_count"] = working["tweet_count"].fillna(0)
        for sentiment in SENTIMENT_LABELS:
            working[f"{sentiment}_ratio"] = working[f"{sentiment}_ratio"].fillna(0)

    fig, (volume_ax, ratio_ax) = plt.subplots(2, 1, figsize=(15, 8.8), constrained_layout=True, sharex=True)

    time_step_days = _infer_bar_width_days(working.index)
    volume_ax.bar(working.index, working["tweet_count"], width=time_step_days * 0.72, color="#9DB4C0", alpha=0.95)
    volume_ax.plot(working.index, working["tweet_count"], color="#E9C46A", linewidth=2.0, marker="o", markersize=4)
    volume_ax.set_title(title, fontsize=18, weight="bold")
    volume_ax.set_ylabel("Tweet Count")
    volume_ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    _annotate_volume_peak(volume_ax, working)

    cumulative_bottom = pd.Series(0.0, index=working.index)
    for sentiment in SENTIMENT_LABELS:
        ratio_ax.bar(
            working.index,
            working[f"{sentiment}_ratio"],
            bottom=cumulative_bottom,
            width=time_step_days * 0.72,
            color=SENTIMENT_COLORS[sentiment],
            alpha=0.9,
            label=sentiment,
        )
        cumulative_bottom = cumulative_bottom + working[f"{sentiment}_ratio"]

    ratio_ax.set_ylabel("Sentiment Share")
    ratio_ax.set_xlabel("Time (UTC)")
    ratio_ax.set_ylim(0, 1)
    ratio_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ratio_ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    ratio_ax.legend(loc="upper right", frameon=True, ncol=3)

    if event_markers:
        for marker_time, label in event_markers:
            for axis in (volume_ax, ratio_ax):
                axis.axvline(marker_time, color="#E9C46A", linestyle=":", linewidth=1.5, alpha=0.95)
            volume_ax.annotate(
                label,
                xy=(marker_time, 0.96),
                xycoords=("data", "axes fraction"),
                xytext=(4, -2),
                textcoords="offset points",
                rotation=90,
                va="top",
                ha="left",
                fontsize=8.5,
                color="#F1FAEE",
                bbox={"boxstyle": "round,pad=0.25", "facecolor": "#2B2D42", "edgecolor": "#E9C46A", "alpha": 0.9},
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


def _annotate_volume_peak(axis: plt.Axes, time_df: pd.DataFrame) -> None:
    if time_df.empty:
        return

    peak_time = time_df["tweet_count"].idxmax()
    peak_value = time_df.loc[peak_time, "tweet_count"]
    axis.annotate(
        f"Volume Peak\n{peak_time.strftime('%H:%M')} | {int(peak_value):,}",
        xy=(peak_time, peak_value),
        xytext=(-26, -8),
        textcoords="offset points",
        fontsize=9.5,
        color="#264653",
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "edgecolor": "#264653", "alpha": 0.9},
        arrowprops={"arrowstyle": "->", "color": "#264653", "lw": 1.2},
    )


def _build_continuous_time_index(index: pd.Index) -> pd.DatetimeIndex | None:
    if len(index) < 2:
        return None

    inferred = pd.infer_freq(index)
    if inferred:
        return pd.date_range(index.min(), index.max(), freq=inferred)

    deltas = pd.Series(index[1:] - index[:-1])
    step = deltas.mode().iloc[0] if not deltas.empty else None
    if step is None or pd.isna(step):
        return None
    return pd.date_range(index.min(), index.max(), freq=step)


def _infer_bar_width_days(index: pd.Index) -> float:
    if len(index) < 2:
        return 1 / 24
    deltas = pd.Series(index[1:] - index[:-1])
    step = deltas.mode().iloc[0]
    return step / pd.Timedelta(days=1)
