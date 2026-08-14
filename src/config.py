from pathlib import Path

# Resolve project root robustly
try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
except NameError:
    PROJECT_ROOT = Path.cwd().resolve()

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA = DATA_DIR / "raw" / "SuperMarket_Analysis.csv"
PROCESSED_CSV = DATA_DIR / "processed" / "processed.csv"
MODELS_DIR = PROJECT_ROOT / "models"
PREPROCESSOR_PATH = MODELS_DIR / "preprocessor_pipeline.joblib"
BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

RANDOM_STATE = 42


def validate_paths(create_if_missing=True):
    if create_if_missing:
        PROCESSED_CSV.parent.mkdir(parents=True, exist_ok=True)
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
