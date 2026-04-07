from __future__ import annotations

import json
from contextlib import asynccontextmanager

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

from src.config import METRICS_PATH, MODEL_PATH
from src.data.hdfs import FEATURE_COLUMNS
from src.models.train import train_model
from src.utils.prediction_store import ensure_predictions_table, fetch_recent_predictions, log_prediction


REQUEST_COUNT = Counter("prediction_requests_total", "Total prediction requests served")
REQUEST_LATENCY = Histogram("prediction_request_latency_seconds", "Latency for prediction requests")
PREDICTION_SCORE = Gauge("prediction_score", "Latest prediction score")


class LogRecord(BaseModel):
    content: str = Field(..., examples=["Error receiving block blk_-3544583377289625738 bad packet checksum detected"])
    component: str = Field(..., examples=["dfs.DataNode$DataXceiver"])
    level: str = Field(..., examples=["ERROR"])
    block_id: str = Field(..., examples=["blk_-3544583377289625738"])


class PredictionResponse(BaseModel):
    anomaly_probability: float
    predicted_anomaly: bool


class PredictionLogEntry(BaseModel):
    id: int
    created_at: str
    content: str
    component: str
    level: str
    block_id: str
    anomaly_probability: float
    predicted_anomaly: bool


app_state: dict[str, object] = {"model": None, "training_metrics": {}}


DEFAULT_SAMPLE = {
    "content": "Error receiving block blk_-3544583377289625738 bad packet checksum detected",
    "component": "dfs.DataNode$DataXceiver",
    "level": "ERROR",
    "block_id": "blk_-3544583377289625738",
}


def model_is_compatible(model: object) -> bool:
    try:
        sample = pd.DataFrame([[DEFAULT_SAMPLE[col] for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        model.predict_proba(sample)
        return True
    except Exception:
        return False


def ensure_model():
    retrain_required = not MODEL_PATH.exists() or not METRICS_PATH.exists()

    if not retrain_required and METRICS_PATH.exists():
        training_metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        if training_metrics.get("task") != "hdfs_log_anomaly_detection":
            retrain_required = True

    if retrain_required:
        train_model()

    if app_state["model"] is None:
        loaded_model = joblib.load(MODEL_PATH)
        if not model_is_compatible(loaded_model):
            train_model()
            loaded_model = joblib.load(MODEL_PATH)
        app_state["model"] = loaded_model

    if METRICS_PATH.exists():
        app_state["training_metrics"] = json.loads(METRICS_PATH.read_text(encoding="utf-8"))

    ensure_predictions_table()


@asynccontextmanager
async def lifespan(_: FastAPI):
    ensure_model()
    yield


app = FastAPI(
    title="HDFS Log Anomaly Detection API",
    description="Inference service for an end-to-end MLOps pipeline that detects anomalous HDFS log events.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "HDFS log anomaly detection API is running"}


@app.get("/health")
def health_check() -> dict[str, object]:
    ensure_model()
    return {
        "status": "ok",
        "model_loaded": app_state["model"] is not None,
        "training_metrics": app_state["training_metrics"],
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: LogRecord) -> PredictionResponse:
    ensure_model()
    model = app_state["model"]
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not available")

    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        features = pd.DataFrame([[getattr(payload, col) for col in FEATURE_COLUMNS]], columns=FEATURE_COLUMNS)
        probability = float(model.predict_proba(features)[0][1])
        prediction = bool(probability >= 0.5)

    PREDICTION_SCORE.set(probability)
    log_prediction(
        content=payload.content,
        component=payload.component,
        level=payload.level,
        block_id=payload.block_id,
        anomaly_probability=probability,
        predicted_anomaly=prediction,
    )
    return PredictionResponse(
        anomaly_probability=round(probability, 4),
        predicted_anomaly=prediction,
    )


@app.get("/predictions/recent", response_model=list[PredictionLogEntry])
def recent_predictions(limit: int = Query(default=20, ge=1, le=100)) -> list[PredictionLogEntry]:
    ensure_model()
    return [PredictionLogEntry(**entry) for entry in fetch_recent_predictions(limit=limit)]


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
