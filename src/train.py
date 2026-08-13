
import argparse
import datetime
import json
import subprocess
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.config import BEST_MODEL_PATH, FIGURES_DIR, MODELS_DIR, PREPROCESSOR_PATH, RANDOM_STATE


def detect_feature_types(df, target):
    X = df.drop(columns=[target])
    numeric_cols = X.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    return numeric_cols, categorical_cols


def build_preprocessor(numeric_cols, categorical_cols):
    transformers = []
    if numeric_cols:
        transformers.append(("num", StandardScaler(), numeric_cols))
    if categorical_cols:
        try:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        except TypeError:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse=False)
        transformers.append(("cat", encoder, categorical_cols))

    if not transformers:
        return "passthrough"

    return ColumnTransformer(transformers, remainder="drop")


def evaluate_model(pipeline, X_test, y_test):
    predictions = pipeline.predict(X_test)
    rmse = mean_squared_error(y_test, predictions) ** 0.5
    return {
        "mae": float(mean_absolute_error(y_test, predictions)),
        "rmse": float(rmse),
        "r2_score": float(r2_score(y_test, predictions)),
    }


def get_git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return None


def save_artifacts(preprocessor, pipeline, metrics, best_params, output_dir, model_path, preprocessor_path, y_test, predictions):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    predictions_path = output_dir / "predictions.csv"
    model_path = Path(model_path)
    preprocessor_path = Path(preprocessor_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    preprocessor_path.parent.mkdir(parents=True, exist_ok=True)

    metrics_paths = [output_dir / "metrics.json", model_path.parent / "metrics.json"]
    metadata_paths = [output_dir / "metadata.json", model_path.parent / "metadata.json"]

    for metrics_path in metrics_paths:
        with metrics_path.open("w", encoding="utf-8") as handle:
            json.dump(metrics, handle, indent=2)

    pd.DataFrame({"actual": y_test.reset_index(drop=True), "predicted": predictions}).to_csv(predictions_path, index=False)
    joblib.dump(preprocessor, preprocessor_path)
    joblib.dump(pipeline, model_path)

    metadata = {
        "timestamp_utc": datetime.datetime.utcnow().isoformat(),
        "random_state": RANDOM_STATE,
        "best_params": best_params,
        "git_commit": get_git_commit(),
    }
    for metadata_path in metadata_paths:
        metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return metrics_paths[0], predictions_path


def train_model(
    input_path="data/processed/processed.csv",
    output_dir="outputs",
    model_path=BEST_MODEL_PATH,
    preprocessor_path=PREPROCESSOR_PATH,
    target="gross income",
    test_size=0.2,
    grid=False,
    cv=3,
):
    df = pd.read_csv(input_path)
    if target not in df.columns:
        raise KeyError(f"Target column '{target}' not found. Available columns: {list(df.columns)}")

    X = df.drop(columns=[target]).fillna(0)
    y = df[target]

    numeric_cols, categorical_cols = detect_feature_types(df, target)
    preprocessor = build_preprocessor(numeric_cols, categorical_cols)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=RANDOM_STATE)

    candidate_models = [
        ("Linear Regression", LinearRegression()),
        ("Random Forest", RandomForestRegressor(random_state=RANDOM_STATE, n_estimators=200, n_jobs=-1)),
        ("Gradient Boosting", GradientBoostingRegressor(random_state=RANDOM_STATE, n_estimators=200)),
    ]

    best_pipeline = None
    best_name = None
    best_metrics = None
    best_predictions = None
    best_params = None

    for name, model in candidate_models:
        pipeline = Pipeline([("pre", preprocessor), ("model", model)])

        if grid:
            param_grid = {
                "model__n_estimators": [100, 300],
                "model__max_depth": [None, 10, 30],
                "model__min_samples_split": [2, 5],
            }
            search = GridSearchCV(
                pipeline,
                param_grid=param_grid,
                cv=cv,
                scoring="neg_root_mean_squared_error",
                n_jobs=-1,
                verbose=0,
            )
            search.fit(X_train, y_train)
            pipeline = search.best_estimator_
            params = search.best_params_
        else:
            pipeline.fit(X_train, y_train)
            params = None

        predictions = pipeline.predict(X_test)
        metrics = evaluate_model(pipeline, X_test, y_test)
        print(f"{name}: {metrics}")

        if best_metrics is None or metrics["r2_score"] > best_metrics["r2_score"] + 1e-12 or (
            abs(metrics["r2_score"] - best_metrics["r2_score"]) <= 1e-12
            and (
                metrics["rmse"] < best_metrics["rmse"] - 1e-12
                or (
                    abs(metrics["rmse"] - best_metrics["rmse"]) <= 1e-12
                    and metrics["mae"] < best_metrics["mae"] - 1e-12
                )
            )
        ):
            best_pipeline = pipeline
            best_name = name
            best_metrics = metrics
            best_predictions = predictions
            best_params = params

    save_artifacts(
        preprocessor,
        best_pipeline,
        best_metrics,
        best_params,
        output_dir,
        model_path,
        preprocessor_path,
        y_test,
        best_predictions,
    )
    print("Training complete. Best model:", best_name, best_metrics)
    if best_params:
        print("Best params:", best_params)
    return best_metrics


def parse_args():
    parser = argparse.ArgumentParser(description="Train a sales prediction pipeline")
    parser.add_argument("--input-path", type=str, default="data/processed/processed.csv")
    parser.add_argument("--output-dir", type=str, default="outputs")
    parser.add_argument("--target", type=str, default="gross income")
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--grid", action="store_true")
    parser.add_argument("--cv", type=int, default=3)
    return parser.parse_args()


def train():
    args = parse_args()
    return train_model(
        input_path=args.input_path,
        output_dir=args.output_dir,
        target=args.target,
        test_size=args.test_size,
        grid=args.grid,
        cv=args.cv,
    )


def main():
    train()


if __name__ == "__main__":
    main()
