# Twitter Sentiment Analysis Final Project

This project analyzes Twitter posts collected on `2021-01-06`, performs text cleaning and sentiment scoring, and generates visual reports that are ready to include in a final presentation or written report.

## Project Highlights

This version has been improved in four main ways:

1. The codebase was reorganized into a reusable package: `twitter_sentiment_project/`.
2. The analysis pipeline now produces both figures and CSV reports automatically.
3. The visualization output was upgraded from a single basic line chart to a dashboard plus supporting charts.
4. Backward-compatible wrapper files were kept at the project root, so older notebook imports still work.

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
- `twitter_sentiment_project/analyzer.py`: calculates time-based sentiment, top terms, and summary tables.
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

## Notes

- The canonical input file for the improved pipeline is `data/processed/tweets_with_created_at.csv`.
- Root-level files such as `1234at.csv`, `tweets_with_created_at.csv`, and `tweets_2021-01-06.csv` are still kept as legacy copies for reference.
- If you use `project_accmulated.ipynb`, open or run it from the project root so the compatibility imports continue to work.
