from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from src.config import ARTIFACTS_DIR, PREDICTIONS_DB_PATH


def ensure_predictions_table(db_path: Path = PREDICTIONS_DB_PATH) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                content TEXT NOT NULL,
                component TEXT NOT NULL,
                level TEXT NOT NULL,
                block_id TEXT NOT NULL,
                anomaly_probability REAL NOT NULL,
                predicted_anomaly INTEGER NOT NULL
            )
            """
        )
        connection.commit()


def log_prediction(
    *,
    content: str,
    component: str,
    level: str,
    block_id: str,
    anomaly_probability: float,
    predicted_anomaly: bool,
    db_path: Path = PREDICTIONS_DB_PATH,
) -> None:
    ensure_predictions_table(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO predictions (
                created_at,
                content,
                component,
                level,
                block_id,
                anomaly_probability,
                predicted_anomaly
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                content,
                component,
                level,
                block_id,
                anomaly_probability,
                int(predicted_anomaly),
            ),
        )
        connection.commit()


def fetch_recent_predictions(limit: int = 20, db_path: Path = PREDICTIONS_DB_PATH) -> list[dict[str, object]]:
    ensure_predictions_table(db_path)
    with sqlite3.connect(db_path) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            """
            SELECT id, created_at, content, component, level, block_id, anomaly_probability, predicted_anomaly
            FROM predictions
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "content": row["content"],
            "component": row["component"],
            "level": row["level"],
            "block_id": row["block_id"],
            "anomaly_probability": row["anomaly_probability"],
            "predicted_anomaly": bool(row["predicted_anomaly"]),
        }
        for row in rows
    ]
