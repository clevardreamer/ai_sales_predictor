from pathlib import Path

import joblib

from src.train import TARGET_LEAKAGE_COLUMNS, train_model


def test_train_model_creates_metrics_and_model(tmp_path):
    metrics = train_model(
        input_path=Path("data/processed/processed.csv"),
        output_dir=tmp_path,
        model_path=tmp_path / "model.joblib",
    )

    assert "r2_score" in metrics
    assert metrics["r2_score"] <= 1.0
    assert (tmp_path / "metrics.json").exists()
    assert (tmp_path / "predictions.csv").exists()
    assert (tmp_path / "model.joblib").exists()

    pipeline = joblib.load(tmp_path / "model.joblib")
    used_features = {
        feature
        for _, _, features in pipeline.named_steps["pre"].transformers
        for feature in features
    }
    assert used_features.isdisjoint(TARGET_LEAKAGE_COLUMNS)
