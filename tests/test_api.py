import app.main as main_module
from fastapi.testclient import TestClient
from src.utils import prediction_store
from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_predict_endpoint(tmp_path, monkeypatch):
    db_path = tmp_path / "predictions.db"
    monkeypatch.setattr(main_module, "ensure_predictions_table", lambda: prediction_store.ensure_predictions_table(db_path))
    monkeypatch.setattr(main_module, "fetch_recent_predictions", lambda limit=20: prediction_store.fetch_recent_predictions(limit=limit, db_path=db_path))
    monkeypatch.setattr(main_module, "log_prediction", lambda **kwargs: prediction_store.log_prediction(db_path=db_path, **kwargs))

    payload = {
        "content": "Error receiving block blk_-3544583377289625738 bad packet checksum detected",
        "component": "dfs.DataNode$DataXceiver",
        "level": "ERROR",
        "block_id": "blk_-3544583377289625738",
    }

    with TestClient(app) as client:
        response = client.post("/predict", json=payload)
        recent = client.get("/predictions/recent?limit=5")

    assert response.status_code == 200
    body = response.json()
    assert 0.0 <= body["anomaly_probability"] <= 1.0
    assert isinstance(body["predicted_anomaly"], bool)

    assert recent.status_code == 200
    recent_body = recent.json()
    assert len(recent_body) >= 1
    assert recent_body[0]["content"] == payload["content"]
