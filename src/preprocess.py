from pathlib import Path
import pandas as pd

# Robust project root resolution:
# - If running as a script, use __file__ parent
# - If running in a notebook, fall back to current working directory
try:
    ROOT = Path(__file__).resolve().parents[1]
except NameError:
    ROOT = Path.cwd()

RAW_PATH = ROOT / "data" / "raw" / "SuperMarket_Analysis.csv"
PROCESSED_PATH = ROOT / "data" / "processed" / "processed.csv"


def load_raw(path: Path | str = RAW_PATH) -> pd.DataFrame:
    print(f"path in load_raw: {path}")
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found at: {path}")
    return pd.read_csv(path)


def clean_missing(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.ffill().bfill()
    return df



def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates()


def convert_types(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    if "Time" in df.columns:
        df["Time"] = df["Time"].astype(str)
    for col in ["Unit price", "Quantity", "Tax 5%", "Sales", "cogs", "gross income", "Rating"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "Quantity" in df.columns:
        df["Quantity"] = df["Quantity"].fillna(0).astype(int)
    return df


def save_processed(df: pd.DataFrame, path: Path | str = PROCESSED_PATH) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved processed CSV to: {path}")


def main() -> None:
    df = load_raw()
    df = clean_missing(df)
    df = deduplicate(df)
    df = convert_types(df)
    save_processed(df)


if __name__ == "__main__":
    main()
