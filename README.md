# Python Twitter Sentiment Analysis

This project analyzes Twitter posts collected on `2021-01-06` and reframes the final report around the impact of the U.S. Capitol attack on social sentiment, with Donald Trump-related discussion as the main event focus. The pipeline performs text cleaning, VADER sentiment scoring, event-subset extraction, and time-based visualization for use in a final presentation or written report.

## Project Highlights

This version has been improved in four main ways:

1. The codebase was reorganized into a reusable package: `twitter_sentiment_project/`.
2. The analysis pipeline now produces both figures and CSV reports automatically.
3. The visualization output was upgraded from a single basic line chart to a dashboard plus event-focused supporting charts.
4. A Capitol-event subset was added so the project can separate general discussion from Trump / Capitol-related tweets.
5. Backward-compatible wrapper files were kept at the project root, so older notebook imports still work.

## Research Framing

The report theme is:

`Python Twitter情緒分析：川普國會山莊事件衝擊（以 2021 年 1 月 6 日國會暴動為例）`

The core research question is whether event-related Twitter discussion showed stronger negative sentiment and sharper volume spikes around key political signals on January 6, 2021.

## Why Snowflake Was Needed

This project does not depend on direct Twitter API calls to reconstruct every tweet timestamp. Instead, it uses a Snowflake-based reverse-engineering workflow inspired by `external/tweetedat-master/` so that tweet IDs can be mapped back to timestamps even when API access is limited or impractical for large historical batches.

## Recommended Project Structure

```text
.
├── data/
│   ├── raw/
│   │   └── tweets_2021-01-06.csv
│   └── processed/
│       └── tweets_with_created_at.csv
├── docs/
│   ├── Twitter.pdf
│   └── sentiment_script.docx
├── external/
│   └── tweetedat-master/
├── outputs/
│   ├── figures/
│   └── reports/
├── twitter_sentiment_project/
│   ├── analyzer.py
│   ├── config.py
│   ├── data_loader.py
│   ├── pipeline.py
│   ├── preprocessor.py
│   ├── sentiment_analyzer.py
│   └── visualizer.py
├── main.py
├── requirements.txt
└── README.md
```

## Main Files

- `main.py`: command-line entry point for the full pipeline.
- `twitter_sentiment_project/data_loader.py`: loads and validates the dataset.
- `twitter_sentiment_project/preprocessor.py`: cleans tweet text and tokenizes content.
- `twitter_sentiment_project/sentiment_analyzer.py`: applies VADER sentiment scoring.
- `twitter_sentiment_project/analyzer.py`: calculates time-based sentiment, event subsets, top terms, and summary tables.
- `twitter_sentiment_project/visualizer.py`: creates the dashboard and supporting charts.
- `twitter_sentiment_project/pipeline.py`: connects the whole workflow and exports outputs.

## Install

```bash
python3 -m pip install -r requirements.txt
```

## Run

Use the default processed dataset:

```bash
python3 main.py
```

Use a custom setting:

```bash
python3 main.py --input data/processed/tweets_with_created_at.csv --freq 15min --min-tweets 10 --top-n-terms 12
```

## Generated Outputs

After running the project, these outputs are created automatically:

### Figures

- `outputs/figures/sentiment_dashboard.png`
- `outputs/figures/top_terms_by_sentiment.png`
- `outputs/figures/query_distribution.png`
- `outputs/figures/capitol_event_timeline.png`
- `outputs/figures/capitol_event_sentiment_comparison.png`
- `outputs/figures/capitol_event_top_terms.png`

### Slides

- `slides/final_presentation.tex`
- `slides/final_presentation.pdf`

### Reports

- `outputs/reports/tweets_sentiment_scored.csv`
- `outputs/reports/time_sentiment_summary.csv`
- `outputs/reports/sentiment_distribution.csv`
- `outputs/reports/top_terms_by_sentiment.csv`
- `outputs/reports/query_distribution.csv`
- `outputs/reports/overall_summary.csv`
- `outputs/reports/capitol_event_summary.csv`
- `outputs/reports/capitol_event_sentiment_distribution.csv`
- `outputs/reports/capitol_event_sentiment_comparison.csv`
- `outputs/reports/capitol_event_top_terms.csv`
- `outputs/reports/capitol_event_time_summary.csv`

## Current Run Summary

Using `data/processed/tweets_with_created_at.csv`, the current pipeline produced:

- Raw rows: `82,309`
- Valid tweets analyzed: `82,035`
- Filtered rows during cleaning/validation: `274`
- Positive sentiment: `45.77%`
- Neutral sentiment: `20.89%`
- Negative sentiment: `33.34%`
- Busiest time window: `2021-01-06 13:45:00`
- Peak positive window: `2021-01-06 13:00:00`
- Peak negative window: `2021-01-06 09:45:00`

For the Capitol-event subset filtered by keywords such as `trump`, `capitol`, `congress`, `riot`, `insurrection`, and `pence`:

- Event subset rows: `5,604`
- Event subset share of all analyzed tweets: `6.83%`
- Event subset average sentiment score: `-0.1423`
- Event subset positive sentiment: `33.35%`
- Event subset neutral sentiment: `12.53%`
- Event subset negative sentiment: `54.12%`
- Event subset peak volume window: `2021-01-06 20:15:00`
- Event subset peak volume count: `3,136`

## Notes

- The canonical input file for the improved pipeline is `data/processed/tweets_with_created_at.csv`.
- Root-level files such as `1234at.csv`, `tweets_with_created_at.csv`, and `tweets_2021-01-06.csv` are still kept as legacy copies for reference.
- If you use `project_accmulated.ipynb`, open or run it from the project root so the compatibility imports continue to work.
