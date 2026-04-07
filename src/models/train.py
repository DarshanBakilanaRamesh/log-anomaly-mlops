from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.config import ARTIFACTS_DIR, METRICS_PATH, MODEL_PATH, RAW_DATA_DIR, SAMPLE_PAYLOAD_PATH
from src.data.hdfs import FEATURE_COLUMNS, TARGET_COLUMN, generate_sample_hdfs_dataset


def load_training_data(data_path: str | Path | None = None) -> pd.DataFrame:
    if data_path:
        return pd.read_csv(data_path)

    csv_files = sorted(RAW_DATA_DIR.glob("*.csv"))
    if csv_files:
        return pd.read_csv(csv_files[0])

    return generate_sample_hdfs_dataset()


def build_pipeline() -> Pipeline:
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(ngram_range=(1, 2), min_df=1), "content"),
            ("categorical", categorical_transformer, ["component", "level", "block_id"]),
        ]
    )

    model = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42)

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", model),
        ]
    )


def train_model(data_path: str | Path | None = None) -> dict[str, float]:
    df = load_training_data(data_path).copy()
    missing_columns = [column for column in FEATURE_COLUMNS + [TARGET_COLUMN] if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {missing_columns}")

    df[TARGET_COLUMN] = df[TARGET_COLUMN].astype(int)
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]

    metrics = {
        "task": "hdfs_log_anomaly_detection",
        "accuracy": round(float(accuracy_score(y_test, predictions)), 4),
        "precision": round(float(precision_score(y_test, predictions, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, predictions, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_test, predictions, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, probabilities)), 4),
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
    }

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    sample_payload = {
        key: ("" if pd.isna(value) else str(value))
        for key, value in X_test.head(1).to_dict(orient="records")[0].items()
    }
    SAMPLE_PAYLOAD_PATH.write_text(json.dumps(sample_payload, indent=2), encoding="utf-8")

    return metrics


if __name__ == "__main__":
    train_model()
