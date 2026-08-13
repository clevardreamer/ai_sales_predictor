import os
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from flask import Flask, jsonify, request


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "models" / "best_model.joblib"
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "processed.csv"
TARGET_COLUMN = "gross income"


def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model artifact not found at {MODEL_PATH}. "
            "Run the training build step before starting the API."
        )
    return joblib.load(MODEL_PATH)


def load_feature_columns():
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(f"Processed dataset not found at {PROCESSED_DATA_PATH}")

    df = pd.read_csv(PROCESSED_DATA_PATH)
    return [column for column in df.columns if column != TARGET_COLUMN]


model = load_model()
FEATURE_COLUMNS = load_feature_columns()

app = Flask(__name__)


def normalize_key(value: str) -> str:
    return "".join(char.lower() if char.isalnum() else "_" for char in value).strip("_")


def predict_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("Request body must be a JSON object")

    normalized_payload = {normalize_key(str(key)): value for key, value in payload.items()}

    values: dict[str, Any] = {}
    for column in FEATURE_COLUMNS:
        if column in payload:
            values[column] = payload[column]
            continue

        normalized_column = normalize_key(column)
        if normalized_column in normalized_payload:
            values[column] = normalized_payload[normalized_column]
            continue

        if column == "Invoice ID":
            values[column] = "STREAMLIT-INPUT"
        elif column == "Date":
            values[column] = "2019-01-05"
        elif column == "Time":
            values[column] = "1:08:00 PM"
        elif column in {"Tax 5%", "cogs", "gross margin percentage", "Sales", "Rating"}:
            values[column] = 0.0
        else:
            values[column] = "Unknown"

    if "Unit price" in values and "Quantity" in values:
        values["Tax 5%"] = float(values["Unit price"]) * float(values["Quantity"]) * 0.05
        values["cogs"] = float(values["Unit price"]) * float(values["Quantity"])
        values["gross margin percentage"] = 4.761905
        values["Sales"] = float(values["Tax 5%"] + values["cogs"])
        values["Rating"] = 8.0

    df = pd.DataFrame([values], columns=FEATURE_COLUMNS)
    prediction = model.predict(df)
    return {"prediction": float(prediction[0])}


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "ML API is running", "features": FEATURE_COLUMNS})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(silent=True)
    try:
        return jsonify(predict_from_payload(payload))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    app.run(host=host, port=port, debug=False)
