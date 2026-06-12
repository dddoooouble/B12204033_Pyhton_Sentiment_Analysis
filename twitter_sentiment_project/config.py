from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURES_DIR = OUTPUT_DIR / "figures"
REPORTS_DIR = OUTPUT_DIR / "reports"
DOCS_DIR = PROJECT_ROOT / "docs"
EXTERNAL_DIR = PROJECT_ROOT / "external"

DEFAULT_INPUT_FILE = PROCESSED_DATA_DIR / "tweets_with_created_at.csv"
LEGACY_INPUT_FILE = PROJECT_ROOT / "tweets_with_created_at.csv"
FALLBACK_INPUT_FILE = PROJECT_ROOT / "1234at.csv"

DEFAULT_TIME_FREQUENCY = "15min"
DEFAULT_MIN_TWEETS = 10
DEFAULT_TOP_N_TERMS = 12
EVENT_KEYWORDS = (
    "trump",
    "capitol",
    "congress",
    "riot",
    "insurrection",
    "pence",
)
EVENT_MARKERS_UTC = (
    ("2021-01-06 19:24:00", "Trump tweet on Pence"),
    ("2021-01-06 19:38:00", "Stay peaceful"),
    ("2021-01-06 21:17:00", "Go home video"),
    ("2021-01-06 23:01:00", "Remember this day"),
)

SENTIMENT_LABELS = ("Positive", "Neutral", "Negative")
SENTIMENT_COLORS = {
    "Positive": "#2A9D8F",
    "Neutral": "#577590",
    "Negative": "#E76F51",
}

COMMON_STOPWORDS = {
    "about",
    "after",
    "again",
    "against",
    "all",
    "also",
    "amp",
    "an",
    "and",
    "any",
    "are",
    "around",
    "because",
    "been",
    "before",
    "being",
    "between",
    "both",
    "but",
    "can",
    "cant",
    "could",
    "couldnt",
    "day",
    "days",
    "did",
    "didnt",
    "does",
    "doesnt",
    "doing",
    "dont",
    "done",
    "down",
    "each",
    "even",
    "every",
    "few",
    "for",
    "from",
    "further",
    "get",
    "got",
    "had",
    "hadnt",
    "has",
    "hasnt",
    "have",
    "havent",
    "having",
    "her",
    "here",
    "hers",
    "herself",
    "him",
    "himself",
    "his",
    "how",
    "https",
    "http",
    "into",
    "its",
    "itself",
    "just",
    "know",
    "like",
    "make",
    "more",
    "most",
    "much",
    "must",
    "need",
    "new",
    "not",
    "now",
    "off",
    "only",
    "one",
    "onto",
    "other",
    "our",
    "ours",
    "ourselves",
    "out",
    "over",
    "own",
    "people",
    "rt",
    "said",
    "same",
    "she",
    "should",
    "since",
    "some",
    "such",
    "than",
    "that",
    "the",
    "their",
    "theirs",
    "them",
    "themselves",
    "then",
    "there",
    "these",
    "they",
    "this",
    "those",
    "time",
    "through",
    "too",
    "tco",
    "under",
    "until",
    "very",
    "was",
    "wasnt",
    "were",
    "werent",
    "what",
    "when",
    "where",
    "which",
    "while",
    "who",
    "whom",
    "why",
    "will",
    "with",
    "within",
    "without",
    "would",
    "you",
    "your",
    "yours",
    "yourself",
    "yourselves",
}


def resolve_default_input_file() -> Path:
    for candidate in (DEFAULT_INPUT_FILE, LEGACY_INPUT_FILE, FALLBACK_INPUT_FILE):
        if candidate.exists():
            return candidate
    return DEFAULT_INPUT_FILE


DATA_FILE = str(resolve_default_input_file())


def ensure_directories() -> None:
    for path in (RAW_DATA_DIR, PROCESSED_DATA_DIR, FIGURES_DIR, REPORTS_DIR, DOCS_DIR, EXTERNAL_DIR):
        path.mkdir(parents=True, exist_ok=True)
