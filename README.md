# End-to-End MLOps Pipeline for HDFS Log Anomaly Detection

This project is a production-oriented starter for training and serving an HDFS log anomaly detection model with a lightweight DevOps toolchain. It includes model training, artifact persistence, a FastAPI inference service, Prometheus-compatible metrics, Docker packaging, GitHub Actions CI, and Kubernetes manifests for deployment.

## Architecture

- Training pipeline: load HDFS log data from CSV or generate a small sample log dataset, preprocess text and metadata, train a classifier, and save model artifacts.
- Inference API: expose `/predict`, `/health`, `/metrics`, and `/predictions/recent` endpoints through FastAPI.
- DevOps workflow: run tests in GitHub Actions, build a Docker image, and deploy via Kubernetes or Helm.
- Monitoring: expose request count, latency, latest prediction score, and persist prediction history for inspection.

## Project Structure

```text
.
|-- app/
|-- artifacts/
|-- data/
|-- docs/
|-- helm/
|-- k8s/
|-- src/
|-- tests/
|-- .github/workflows/
|-- Dockerfile
|-- docker-compose.yml
`-- requirements.txt
```

## Local Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m src.models.train
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the Swagger UI.

## Sample Prediction Request

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"Error receiving block blk_-3544583377289625738 bad packet checksum detected\",\"component\":\"dfs.DataNode$DataXceiver\",\"level\":\"ERROR\",\"block_id\":\"blk_-3544583377289625738\"}"
```

## Training Pipeline

The training script will read the first CSV file from `data/raw/` when available. If no dataset is present, it automatically generates a small HDFS-like sample dataset so the project remains runnable out of the box.

Artifacts produced in `artifacts/`:

- `model.joblib`: serialized scikit-learn pipeline
- `metrics.json`: training metrics including accuracy, precision, recall, F1, and ROC-AUC
- `sample_payload.json`: one valid example request payload
- `predictions.db`: SQLite database storing recent prediction history

## Prediction Logging

Each `/predict` request is stored in `artifacts/predictions.db` with:

- timestamp
- log content
- component
- level
- block ID
- anomaly probability
- predicted anomaly label

You can inspect recent predictions through:

```bash
curl "http://127.0.0.1:8000/predictions/recent?limit=10"
```

## Expected Dataset Schema

Place an HDFS CSV inside `data/raw/` with these columns:

```csv
content,component,level,block_id,anomaly
"Receiving block blk_-1608999687919862906 src /10.250.19.102 dest /10.250.19.102","dfs.DataNode$DataXceiver",INFO,"blk_-1608999687919862906",0
"Error receiving block blk_-3544583377289625738 bad packet checksum detected","dfs.DataNode$DataXceiver",ERROR,"blk_-3544583377289625738",1
```

Where:

- `content` is the raw log message
- `component` is the HDFS service/component
- `level` is the log level like `INFO` or `ERROR`
- `block_id` is the HDFS block identifier
- `anomaly` is the target label with `0` for normal and `1` for anomalous

## Docker

```bash
docker build -t hdfs-log-anomaly-api .
docker run -p 8000:8000 hdfs-log-anomaly-api
```

Or with Compose:

```bash
docker compose up --build
```

## Kubernetes

Apply the manifests:

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

If you use the Prometheus Operator, you can also apply:

```bash
kubectl apply -f k8s/prometheus-monitor.yaml
```

## CI/CD

The GitHub Actions workflow:

- installs Python dependencies
- runs `pytest`
- builds the Docker image

## Next Improvements

- replace the sample fallback data with the full HDFS_v1 dataset
- push container images to GHCR, ECR, or Docker Hub
- add Helm templates instead of static Helm metadata only
- add MLflow for experiment tracking
- add drift detection for log distributions
- add automatic retraining and rollout on approved model changes
